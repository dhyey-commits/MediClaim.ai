"""
Claims API Router — all endpoints backed by real PostgreSQL queries.
"""

from __future__ import annotations

import re
import uuid
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.models import (
    AuditLog,
    Claim,
    ClaimStatus,
    Diagnosis,
    Document,
    DocumentStatus,
    ExtractedEntity,
    ICDCode,
    Report,
)
from app.services.extraction_service import extract_clinical_data
from app.services.icd_mapper import map_diagnosis_to_icd
from app.services.report_generator import build_iscs_report_data, generate_pdf
from app.services.storage import save_upload

router = APIRouter()


# ─────────────────────────────────────────────
# Pydantic Schemas (inline for this module)
# ─────────────────────────────────────────────

class ClaimCreateRequest(BaseModel):
    patient_name: str | None = None
    notes: str | None = None


class DiagnosisOverrideRequest(BaseModel):
    icd_code: str


class ClaimListItem(BaseModel):
    id: str
    claim_number: str
    patient_name: str | None
    status: str
    document_count: int
    created_at: str

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    id: str
    file_name: str
    file_type: str | None
    file_size: int | None
    status: str
    confidence_score: float
    created_at: str

    class Config:
        from_attributes = True


class DiagnosisOut(BaseModel):
    id: str
    description: str
    icd_code: str | None
    icd_description: str | None
    confidence: float
    is_primary: bool
    is_manually_overridden: bool

    class Config:
        from_attributes = True


class ExtractedEntityOut(BaseModel):
    id: str
    entity_type: str
    value: str
    confidence: float

    class Config:
        from_attributes = True


class ReportOut(BaseModel):
    id: str
    report_type: str
    is_generated: bool
    created_at: str

    class Config:
        from_attributes = True


class ClaimDetailOut(BaseModel):
    id: str
    claim_number: str
    patient_name: str | None
    patient_age: int | None
    patient_gender: str | None
    patient_uhid: str | None
    admission_date: str | None
    discharge_date: str | None
    chief_complaint: str | None
    status: str
    notes: str | None
    created_at: str
    updated_at: str
    documents: list[DocumentOut]
    diagnoses: list[DiagnosisOut]
    extracted_entities: list[ExtractedEntityOut]
    report: ReportOut | None


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _fmt_date(d: Any) -> str | None:
    if d is None:
        return None
    if isinstance(d, (date, datetime)):
        return d.isoformat()
    return str(d)


def _generate_claim_number() -> str:
    prefix = "MC"
    ts = datetime.utcnow().strftime("%y%m%d")
    rand = str(uuid.uuid4().int)[:4]
    return f"{prefix}-{ts}-{rand}"


def _build_claim_detail(claim: Claim) -> ClaimDetailOut:
    documents = [
        DocumentOut(
            id=d.id,
            file_name=d.file_name,
            file_type=d.file_type,
            file_size=d.file_size,
            status=d.status,
            confidence_score=d.confidence_score or 0.0,
            created_at=_fmt_date(d.created_at) or "",
        )
        for d in claim.documents
    ]

    diagnoses = [
        DiagnosisOut(
            id=diag.id,
            description=diag.description,
            icd_code=diag.icd_code_override or (diag.icd_code.code if diag.icd_code else None),
            icd_description=diag.icd_code.description if diag.icd_code else None,
            confidence=diag.confidence or 0.0,
            is_primary=diag.is_primary,
            is_manually_overridden=diag.is_manually_overridden,
        )
        for diag in claim.diagnoses
    ]

    entities = [
        ExtractedEntityOut(
            id=e.id,
            entity_type=e.entity_type,
            value=e.value,
            confidence=e.confidence or 0.0,
        )
        for e in claim.extracted_entities
    ]

    report_out = None
    if claim.report:
        report_out = ReportOut(
            id=claim.report.id,
            report_type=claim.report.report_type or "ISCS",
            is_generated=claim.report.is_generated,
            created_at=_fmt_date(claim.report.created_at) or "",
        )

    return ClaimDetailOut(
        id=claim.id,
        claim_number=claim.claim_number,
        patient_name=claim.patient_name,
        patient_age=claim.patient_age,
        patient_gender=claim.patient_gender,
        patient_uhid=claim.patient_uhid,
        admission_date=_fmt_date(claim.admission_date),
        discharge_date=_fmt_date(claim.discharge_date),
        chief_complaint=claim.chief_complaint,
        status=claim.status,
        notes=claim.notes,
        created_at=_fmt_date(claim.created_at) or "",
        updated_at=_fmt_date(claim.updated_at) or "",
        documents=documents,
        diagnoses=diagnoses,
        extracted_entities=entities,
        report=report_out,
    )


# ─────────────────────────────────────────────
# POST /claims  — Create new claim
# ─────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_claim(
    body: ClaimCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    claim = Claim(
        claim_number=_generate_claim_number(),
        patient_name=body.patient_name,
        notes=body.notes,
        status=ClaimStatus.DRAFT.value,
    )
    db.add(claim)
    await db.commit()
    await db.refresh(claim)

    db.add(AuditLog(
        claim_id=claim.id,
        action="Claim created",
        entity_type="Claim",
        entity_id=claim.id,
    ))
    await db.commit()

    return {"id": claim.id, "claim_number": claim.claim_number, "status": claim.status}


# ─────────────────────────────────────────────
# GET /claims  — List all claims
# ─────────────────────────────────────────────

@router.get("")
async def list_claims(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[ClaimListItem]:
    result = await db.execute(
        select(Claim)
        .options(selectinload(Claim.documents))
        .order_by(Claim.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    claims = result.scalars().all()

    return [
        ClaimListItem(
            id=c.id,
            claim_number=c.claim_number,
            patient_name=c.patient_name,
            status=c.status,
            document_count=len(c.documents),
            created_at=_fmt_date(c.created_at) or "",
        )
        for c in claims
    ]


# ─────────────────────────────────────────────
# GET /claims/{id}  — Claim detail
# ─────────────────────────────────────────────

@router.get("/{claim_id}")
async def get_claim(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
) -> ClaimDetailOut:
    result = await db.execute(
        select(Claim)
        .where(Claim.id == claim_id)
        .options(
            selectinload(Claim.documents),
            selectinload(Claim.diagnoses).selectinload(Diagnosis.icd_code),
            selectinload(Claim.extracted_entities),
            selectinload(Claim.report),
        )
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return _build_claim_detail(claim)


# ─────────────────────────────────────────────
# POST /claims/{id}/upload  — Upload documents
# ─────────────────────────────────────────────

@router.post("/{claim_id}/upload", status_code=status.HTTP_201_CREATED)
async def upload_documents(
    claim_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Verify claim exists
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    uploaded = []
    for file in files:
        # Validate file type
        allowed_types = {
            "application/pdf", "image/jpeg", "image/jpg",
            "image/png", "image/tiff",
        }
        if file.content_type and file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed. Use PDF or images.",
            )

        file_path, file_size = await save_upload(file, claim_id)

        doc = Document(
            claim_id=claim_id,
            file_name=file.filename or "upload",
            file_type=file.content_type,
            file_path=file_path,
            file_size=file_size,
            status=DocumentStatus.PENDING.value,
        )
        db.add(doc)
        uploaded.append({"file_name": file.filename, "size": file_size})

    # Update claim status
    claim.status = ClaimStatus.DOCUMENT_UPLOADED.value
    db.add(AuditLog(
        claim_id=claim_id,
        action=f"Uploaded {len(uploaded)} document(s)",
        entity_type="Document",
    ))
    await db.commit()

    return {"claim_id": claim_id, "uploaded": len(uploaded), "files": uploaded}


# ─────────────────────────────────────────────
# POST /claims/{id}/extract  — Run OCR + NLP
# ─────────────────────────────────────────────

@router.post("/{claim_id}/extract")
async def run_extraction(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Claim)
        .where(Claim.id == claim_id)
        .options(selectinload(Claim.documents))
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if not claim.documents:
        raise HTTPException(status_code=400, detail="No documents uploaded yet")

    # Process the first document (or all)
    primary_doc = claim.documents[0]
    primary_doc.status = DocumentStatus.OCR_PROCESSING.value
    await db.commit()

    # Run extraction
    extracted = await extract_clinical_data(
        file_path=primary_doc.file_path or "",
        claim_id=claim_id,
        document_id=primary_doc.id,
    )

    # Update document
    primary_doc.status = DocumentStatus.OCR_COMPLETE.value
    primary_doc.confidence_score = max(extracted.get("confidence_scores", {}).values(), default=0.0)

    # Update claim with patient info
    from datetime import date as date_type
    def _parse_date(s: str | None) -> date_type | None:
        if not s:
            return None
        try:
            return date_type.fromisoformat(s)
        except Exception:
            return None

    claim.patient_name = extracted.get("patient_name")
    claim.patient_age = extracted.get("patient_age")
    claim.patient_gender = extracted.get("patient_gender")
    claim.patient_uhid = extracted.get("patient_uhid")
    claim.admission_date = _parse_date(extracted.get("admission_date"))
    claim.discharge_date = _parse_date(extracted.get("discharge_date"))
    claim.chief_complaint = extracted.get("chief_complaint")
    claim.status = ClaimStatus.OCR_COMPLETE.value

    # Delete old extracted entities for this claim
    old_entities_result = await db.execute(
        select(ExtractedEntity).where(ExtractedEntity.claim_id == claim_id)
    )
    for old in old_entities_result.scalars().all():
        await db.delete(old)

    # Store extracted entities
    entity_type_map = {
        "diagnoses": "diagnosis",
        "procedures": "procedure",
        "medications": "medication",
        "investigations": "investigation",
    }
    scores = extracted.get("confidence_scores", {})

    for field, etype in entity_type_map.items():
        items = extracted.get(field, [])
        for item in items:
            db.add(ExtractedEntity(
                claim_id=claim_id,
                entity_type=etype,
                value=item,
                confidence=scores.get(field, 0.85),
                source_document_id=primary_doc.id,
            ))

    claim.status = ClaimStatus.EXTRACTION_COMPLETE.value
    db.add(AuditLog(
        claim_id=claim_id,
        action="AI extraction completed",
        entity_type="Claim",
        entity_id=claim_id,
    ))
    await db.commit()

    return {
        "claim_id": claim_id,
        "status": claim.status,
        "patient_name": claim.patient_name,
        "entities_extracted": sum(
            len(extracted.get(f, [])) for f in entity_type_map
        ),
        "confidence_scores": extracted.get("confidence_scores", {}),
    }


# ─────────────────────────────────────────────
# POST /claims/{id}/icd-map  — ICD-10 Mapping
# ─────────────────────────────────────────────

@router.post("/{claim_id}/icd-map")
async def map_icd_codes(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Claim)
        .where(Claim.id == claim_id)
        .options(selectinload(Claim.extracted_entities))
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Get diagnosis entities
    diag_entities = [
        e for e in claim.extracted_entities if e.entity_type == "diagnosis"
    ]
    if not diag_entities:
        raise HTTPException(status_code=400, detail="Run extraction first — no diagnoses found")

    # Delete existing diagnoses
    old_diag_result = await db.execute(
        select(Diagnosis).where(Diagnosis.claim_id == claim_id)
    )
    for old in old_diag_result.scalars().all():
        await db.delete(old)
    await db.flush()

    mappings = []
    for idx, entity in enumerate(diag_entities):
        icd_code_id, icd_code_str, confidence = await map_diagnosis_to_icd(
            entity.value, db
        )
        diag = Diagnosis(
            claim_id=claim_id,
            description=entity.value,
            icd_code_id=icd_code_id,
            confidence=confidence,
            is_primary=(idx == 0),
        )
        db.add(diag)
        mappings.append({
            "diagnosis": entity.value,
            "icd_code": icd_code_str,
            "confidence": confidence,
        })

    claim.status = ClaimStatus.ICD_MAPPED.value
    db.add(AuditLog(
        claim_id=claim_id,
        action=f"ICD-10 mapping completed for {len(mappings)} diagnosis(es)",
        entity_type="Claim",
        entity_id=claim_id,
    ))
    await db.commit()

    return {
        "claim_id": claim_id,
        "status": claim.status,
        "mappings": mappings,
    }


# ─────────────────────────────────────────────
# PATCH /claims/{id}/diagnoses/{diag_id}/override
# ─────────────────────────────────────────────

@router.patch("/{claim_id}/diagnoses/{diagnosis_id}/override")
async def override_icd_code(
    claim_id: str,
    diagnosis_id: str,
    body: DiagnosisOverrideRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Diagnosis).where(
            Diagnosis.id == diagnosis_id,
            Diagnosis.claim_id == claim_id,
        )
    )
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    diag.icd_code_override = body.icd_code
    diag.is_manually_overridden = True
    await db.commit()

    return {"diagnosis_id": diagnosis_id, "icd_code_override": body.icd_code}


# ─────────────────────────────────────────────
# POST /claims/{id}/generate-report
# ─────────────────────────────────────────────

@router.post("/{claim_id}/generate-report", status_code=status.HTTP_201_CREATED)
async def generate_report(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status not in (ClaimStatus.ICD_MAPPED.value, ClaimStatus.REPORT_GENERATED.value):
        raise HTTPException(
            status_code=400,
            detail="Complete ICD mapping before generating the report",
        )

    # Build report data
    report_data = await build_iscs_report_data(claim_id, db)

    # Generate PDF
    pdf_bytes = generate_pdf(report_data)

    # Save PDF to disk
    from pathlib import Path
    from app.core.config import get_settings
    s = get_settings()
    pdf_dir = s.upload_path / claim_id
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / "iscs_report.pdf"
    pdf_path.write_bytes(pdf_bytes)

    # Upsert Report record
    existing = await db.execute(select(Report).where(Report.claim_id == claim_id))
    report = existing.scalar_one_or_none()
    if report:
        report.report_data = report_data
        report.pdf_path = str(pdf_path)
        report.is_generated = True
        report.version = (report.version or 1) + 1
    else:
        report = Report(
            claim_id=claim_id,
            report_type="ISCS",
            report_data=report_data,
            pdf_path=str(pdf_path),
            is_generated=True,
        )
        db.add(report)

    claim.status = ClaimStatus.REPORT_GENERATED.value
    db.add(AuditLog(
        claim_id=claim_id,
        action="ISCS report generated",
        entity_type="Report",
    ))
    await db.commit()
    await db.refresh(report)

    return {
        "claim_id": claim_id,
        "report_id": report.id,
        "status": claim.status,
        "pdf_size_kb": round(len(pdf_bytes) / 1024, 1),
    }
