import os
from app.core.config import get_settings
import time
import json
from typing import List, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Claim, OCRResult, ExtractionResult, ClaimStatus, AuditLog

# ---------------------------------------------------------------------------
# Pydantic Schemas for OpenAI Structured Outputs
# ---------------------------------------------------------------------------

class ExtractedDiagnosis(BaseModel):
    description: str = Field(description="The medical diagnosis description")
    is_primary: bool = Field(description="True if this is the primary diagnosis")

class ExtractedProcedure(BaseModel):
    description: str = Field(description="The procedure name or description")
    date: Optional[str] = Field(None, description="Date of the procedure if available")

class ExtractedMedication(BaseModel):
    name: str = Field(description="Name of the medication")
    dosage: Optional[str] = Field(None, description="Dosage of the medication")
    frequency: Optional[str] = Field(None, description="Frequency of the medication")

class ExtractedInvestigation(BaseModel):
    name: str = Field(description="Name of the investigation or lab test")
    result: Optional[str] = Field(None, description="Result or findings if available")

class ClinicalExtraction(BaseModel):
    patient_name: Optional[str] = Field(None, description="Full name of the patient")
    age: Optional[str] = Field(None, description="Age of the patient")
    gender: Optional[str] = Field(None, description="Gender of the patient")
    admission_date: Optional[str] = Field(None, description="Date of admission")
    discharge_date: Optional[str] = Field(None, description="Date of discharge")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint or presenting illness")
    diagnosis: List[ExtractedDiagnosis] = Field(description="List of diagnoses extracted")
    procedures: List[ExtractedProcedure] = Field(description="List of procedures performed")
    medications: List[ExtractedMedication] = Field(description="List of medications prescribed or given")
    investigations: List[ExtractedInvestigation] = Field(description="List of investigations or lab tests")

# ---------------------------------------------------------------------------
# Extraction Logic
# ---------------------------------------------------------------------------

async def run_extraction_for_claim(claim_id: str, db: AsyncSession):
    """
    Runs the Gemini extraction pipeline on all OCR text for a given claim.
    Saves the structured output to ExtractionResult and logs metrics.
    """
    start_time = time.time()
    model_used = "gemini-2.5-flash"
    
    # 1. Fetch Claim FIRST so we can log to it on any failure
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalars().first()
    if not claim:
        raise ValueError(f"Claim {claim_id} not found.")

    try:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured in settings.")
        
        print(f"[EXTRACTION] Starting extraction for claim {claim_id}")
        
        db.add(AuditLog(
            claim_id=claim_id,
            action="EXTRACTION_STARTED",
            entity_type="Claim",
            entity_id=claim_id,
            new_value={"model": model_used}
        ))
        await db.commit()
        
        client = genai.Client(api_key=settings.gemini_api_key)

        ocr_stmt = select(OCRResult).where(OCRResult.claim_id == claim_id).order_by(OCRResult.page_number)
        ocr_result = await db.execute(ocr_stmt)
        ocr_records = ocr_result.scalars().all()

        if not ocr_records:
            raise ValueError(f"No OCR text found for claim {claim_id}.")

        # Concatenate all OCR text
        full_text = "\n\n".join([f"--- Page {record.page_number} ---\n{record.raw_text}" for record in ocr_records])

        # 2. Call Gemini Structured Outputs
        system_prompt = (
            "You are a medical data extraction engine. Extract the clinical information from the "
            "following discharge summary or medical document. If a field cannot be found, return null. "
            "Do not invent or guess any information."
        )

        print(f"[EXTRACTION] Dispatching Gemini API request for claim {claim_id}")
        response = await client.aio.models.generate_content(
            model=model_used,
            contents=full_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=ClinicalExtraction,
                temperature=0.0
            )
        )
        print(f"[EXTRACTION] Received Gemini API response for claim {claim_id}")
        extraction: ClinicalExtraction = response.parsed
        usage = response.usage_metadata
        prompt_tokens = usage.prompt_token_count if usage else 0
        candidates_tokens = usage.candidates_token_count if usage else 0
        token_count = prompt_tokens + candidates_tokens
        
        # Calculate cost for gemini-2.5-flash
        cost_prompt = (prompt_tokens / 1_000_000) * 0.075
        cost_candidates = (candidates_tokens / 1_000_000) * 0.30
        estimated_cost_usd = cost_prompt + cost_candidates
        
        duration = time.time() - start_time

        # 3. Save Extraction Result
        # Delete existing extraction result if any
        existing_result = await db.execute(select(ExtractionResult).where(ExtractionResult.claim_id == claim_id))
        existing = existing_result.scalars().first()
        if existing:
            await db.delete(existing)
            await db.flush()

        ext_res = ExtractionResult(
            claim_id=claim_id,
            patient_name=extraction.patient_name,
            age=extraction.age,
            gender=extraction.gender,
            admission_date=extraction.admission_date,
            discharge_date=extraction.discharge_date,
            chief_complaint=extraction.chief_complaint,
            diagnosis_json=[d.model_dump() for d in extraction.diagnosis],
            procedures_json=[p.model_dump() for p in extraction.procedures],
            medications_json=[m.model_dump() for m in extraction.medications],
            investigations_json=[i.model_dump() for i in extraction.investigations],
            confidence_score=0.95,
            is_approved=False
        )
        db.add(ext_res)

        # Update Claim status
        claim.status = ClaimStatus.EXTRACTION_COMPLETE.value

        # Update Claim patient info directly as well for the dashboard
        if extraction.patient_name:
            claim.patient_name = extraction.patient_name
        if extraction.age and extraction.age.isdigit():
            claim.patient_age = int(extraction.age)
        if extraction.gender:
            claim.patient_gender = extraction.gender
        if extraction.chief_complaint:
            claim.chief_complaint = extraction.chief_complaint

        # Log success Audit
        audit_log = AuditLog(
            claim_id=claim_id,
            action="EXTRACTION_COMPLETED",
            entity_type="Claim",
            entity_id=claim_id,
            new_value={
                "model": model_used,
                "duration_seconds": round(duration, 2),
                "tokens": token_count,
                "prompt_tokens": prompt_tokens,
                "candidates_tokens": candidates_tokens,
                "estimated_cost_usd": round(estimated_cost_usd, 6),
                "success": True
            }
        )
        db.add(audit_log)
        await db.commit()
        return ext_res

    except Exception as e:
        duration = time.time() - start_time
        # Update claim status
        claim.status = ClaimStatus.EXTRACTION_FAILED.value
        # Log failure
        audit_log = AuditLog(
            claim_id=claim_id,
            action="EXTRACTION_FAILED",
            entity_type="Claim",
            entity_id=claim_id,
            new_value={"error": str(e), "duration": round(duration, 2), "model": model_used}
        )
        db.add(audit_log)
        await db.commit()
        raise e
