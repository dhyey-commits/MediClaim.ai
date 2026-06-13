from __future__ import annotations

from app.core.security import get_current_user
"""
Claims API Router — Week 1 MVP: Create, List, Detail, Upload.
All endpoints backed by real PostgreSQL queries.
"""


import uuid
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.models import (
    AuditLog,
    Claim,
    ClaimStatus,
    Document,
    DocumentStatus,
    OCRResult,
    ExtractionResult,
    Diagnosis,
    ClaimICDRecommendation,
    RecommendationStatus,
)
from app.services.storage import save_file
from app.services.ocr_service import run_ocr_for_claim
from app.services.extraction_service import run_extraction_for_claim
from app.services.icd_mapper_service import suggest_icd_codes

router = APIRouter()


# ─────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────

class ClaimCreateRequest(BaseModel):
    patient_name: str | None = None
    notes: str | None = None


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
    )


# ─────────────────────────────────────────────
# POST /claims  — Create new claim
# ─────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_claim(
    body: ClaimCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
        user_id=current_user.id,
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
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
) -> ClaimDetailOut:
    result = await db.execute(
        select(Claim)
        .where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id)
        .options(
            selectinload(Claim.documents),
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
    current_user: User = Depends(get_current_user),
) -> dict:
    # Verify claim exists
    result = await db.execute(select(Claim).where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    uploaded = []
    for file in files:
        # Validate file type
        allowed_types = {
            "application/pdf", "image/jpeg", "image/jpg",
            "image/png",
        }
        if file.content_type and file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed. Use PDF, PNG, JPG, or JPEG.",
            )

        file_path, file_size = await save_file(file, claim_id)

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
        user_id=current_user.id,
        claim_id=claim_id,
        action=f"Uploaded {len(uploaded)} document(s)",
        entity_type="Document",
    ))
    await db.commit()

    return {"claim_id": claim_id, "uploaded": len(uploaded), "files": uploaded}

# ─────────────────────────────────────────────
# POST /claims/{id}/ocr  — Trigger OCR
# ─────────────────────────────────────────────

@router.post("/{claim_id}/ocr", status_code=status.HTTP_202_ACCEPTED)
async def trigger_ocr(
    claim_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    result = await db.execute(select(Claim).where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id))
    claim = result.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        

    from app.models import Document
    import pypdf
    docs_result = await db.execute(select(Document).where(Document.claim_id == claim_id))
    docs = docs_result.scalars().all()
    total_pages = 0
    for doc in docs:
        if doc.file_path and doc.file_path.endswith(".pdf"):
            try:
                reader = pypdf.PdfReader(doc.file_path)
                total_pages += len(reader.pages)
            except Exception:
                pass
    if total_pages > 50:
        db.add(AuditLog(
            user_id=current_user.id,
            claim_id=claim_id,
            action="OCR_REJECTED_PAGE_LIMIT",
            entity_type="Claim",
            entity_id=claim_id
        ))
        await db.commit()
        raise HTTPException(status_code=413, detail="PDF exceeds 50 page limit")

    claim.status = ClaimStatus.OCR_PROCESSING.value
    await db.commit()

        
    # In FastAPI, BackgroundTasks run in the same event loop, but we need db session 
    # to be open. Instead of passing db, we might need a fresh session for the background task,
    # or pass a factory.
    # For MVP, we will run the OCR task synchronously if it's very simple, or pass it an async wrapper
    # that creates its own session.
    # Since run_ocr_for_claim takes a session, we can just await it synchronously for simplicity in Week 2
    # if it's just one document, but background_tasks is preferred.
    # To use background tasks with SQLAlchemy async, we should spawn a new session.
    # Let's adjust the wrapper to create a new session inline or just do it synchronously for MVP reliability.
    
    from app.models import BackgroundJob, JobStatus
    import uuid
    job_id = uuid.uuid4().hex
    db.add(BackgroundJob(
        id=job_id,
        claim_id=claim_id,
        job_type="OCR",
        status=JobStatus.QUEUED.value
    ))
    db.add(AuditLog(
        claim_id=claim_id,
        action="JOB_QUEUED",
        entity_type="BackgroundJob",
        entity_id=job_id,
        new_value={"job_type": "OCR"}
    ))
    await db.commit()
    await request.app.state.redis.enqueue_job('ocr_task', job_id, claim_id, current_user.id, _job_id=job_id)
    return {"message": "OCR processing started", "status": "OCR_PROCESSING"}


# ─────────────────────────────────────────────
# GET /claims/{id}/ocr  — Get OCR Results
# ─────────────────────────────────────────────

class OCRResultOut(BaseModel):
    document_id: str
    page_number: int
    raw_text: str
    status: str
    
    class Config:
        from_attributes = True

@router.get("/{claim_id}/ocr", response_model=list[OCRResultOut])
async def get_ocr_results(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(OCRResult)
        .where(OCRResult.claim_id == claim_id)
        .order_by(OCRResult.document_id, OCRResult.page_number)
    )
    return result.scalars().all()

# ─────────────────────────────────────────────
# Extraction Endpoints
# ─────────────────────────────────────────────

class ExtractionResultOut(BaseModel):
    id: str
    claim_id: str
    patient_name: str | None
    age: str | None
    gender: str | None
    admission_date: str | None
    discharge_date: str | None
    chief_complaint: str | None
    diagnosis_json: list | None
    procedures_json: list | None
    medications_json: list | None
    investigations_json: list | None
    confidence_score: float
    is_approved: bool

    class Config:
        from_attributes = True

class ExtractionUpdate(BaseModel):
    patient_name: str | None = None
    age: str | None = None
    gender: str | None = None
    admission_date: str | None = None
    discharge_date: str | None = None
    chief_complaint: str | None = None
    diagnosis_json: list | None = None
    procedures_json: list | None = None
    medications_json: list | None = None
    investigations_json: list | None = None
    is_approved: bool | None = None

@router.post("/{claim_id}/extract")
async def trigger_extraction(
    claim_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Claim).where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id))
    claim = result.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")



    if claim.status not in [ClaimStatus.OCR_COMPLETE.value, ClaimStatus.EXTRACTION_COMPLETE.value, ClaimStatus.EXTRACTION_FAILED.value]:
        raise HTTPException(status_code=400, detail="Claim is not ready for extraction")


    from sqlalchemy import update
    upd = update(Claim).where(
        Claim.id == claim_id,
        Claim.organization_id == current_user.organization_id,
        Claim.status != ClaimStatus.EXTRACTION_PROCESSING.value
    ).values(status=ClaimStatus.EXTRACTION_PROCESSING.value)
    
    upd_res = await db.execute(upd)
    if upd_res.rowcount == 0:
        raise HTTPException(status_code=409, detail="Extraction already running")
    await db.commit()


    from app.models import BackgroundJob, JobStatus
    import uuid
    job_id = uuid.uuid4().hex
    db.add(BackgroundJob(
        id=job_id,
        claim_id=claim_id,
        job_type="EXTRACTION",
        status=JobStatus.QUEUED.value
    ))
    db.add(AuditLog(
        claim_id=claim_id,
        action="JOB_QUEUED",
        entity_type="BackgroundJob",
        entity_id=job_id,
        new_value={"job_type": "EXTRACTION"}
    ))
    await db.commit()
    await request.app.state.redis.enqueue_job('extraction_task', job_id, claim_id, current_user.id, _job_id=job_id)
    return {"message": "Extraction started", "status": "EXTRACTION_PROCESSING"}

@router.get("/{claim_id}/extraction", response_model=ExtractionResultOut)
async def get_extraction(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(ExtractionResult).where(ExtractionResult.claim_id == claim_id))
    ext = result.scalars().first()
    if not ext:
        raise HTTPException(status_code=404, detail="Extraction not found")
    return ext

@router.post("/{claim_id}/review/start")
async def start_review(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Claim).where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id))
    claim = result.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status != ClaimStatus.EXTRACTION_COMPLETE.value:
        raise HTTPException(status_code=400, detail="Claim must be EXTRACTION_COMPLETE to start review")

    ext_res = await db.execute(select(ExtractionResult).where(ExtractionResult.claim_id == claim_id))
    ext = ext_res.scalars().first()
    if ext:
        ext.reviewed_by = "System User"
        ext.reviewed_at = datetime.utcnow()

    claim.status = ClaimStatus.UNDER_REVIEW.value
    db.add(AuditLog(
        user_id=current_user.id,
        claim_id=claim_id,
        action="REVIEW_STARTED",
        entity_type="Claim",
        entity_id=claim_id
    ))
    await db.commit()
    return {"message": "Review started", "status": claim.status}

@router.patch("/{claim_id}/review", response_model=ExtractionResultOut)
async def update_review(
    claim_id: str,
    update_data: ExtractionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Claim).where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id))
    claim = result.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
        
    if claim.status == ClaimStatus.APPROVED.value:
        raise HTTPException(status_code=403, detail="Claim is already approved and cannot be edited")

    ext_res = await db.execute(select(ExtractionResult).where(ExtractionResult.claim_id == claim_id))
    ext = ext_res.scalars().first()
    if not ext:
        raise HTTPException(status_code=404, detail="Extraction not found")

    update_dict = update_data.model_dump(exclude_unset=True)
    
    # Audit log changes
    for k, v in update_dict.items():
        old_val = getattr(ext, k)
        if old_val != v:
            setattr(ext, k, v)
            db.add(AuditLog(
                claim_id=claim_id,
                action="FIELD_EDITED",
                entity_type="ExtractionResult",
                entity_id=ext.id,
                old_value={k: old_val},
                new_value={k: v}
            ))

    db.add(AuditLog(
        user_id=current_user.id,
        claim_id=claim_id,
        action="REVIEW_SAVED",
        entity_type="ExtractionResult",
        entity_id=ext.id
    ))

    await db.commit()
    await db.refresh(ext)
    return ext

@router.post("/{claim_id}/approve")
async def approve_claim(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Claim).where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id))
    claim = result.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status != ClaimStatus.UNDER_REVIEW.value:
        raise HTTPException(status_code=400, detail="Claim must be UNDER_REVIEW to be approved")

    ext_res = await db.execute(select(ExtractionResult).where(ExtractionResult.claim_id == claim_id))
    ext = ext_res.scalars().first()
    if ext:
        ext.is_approved = True
        ext.approved_by = "System User"
        ext.approved_at = datetime.utcnow()

    claim.status = ClaimStatus.APPROVED.value
    db.add(AuditLog(
        user_id=current_user.id,
        claim_id=claim_id,
        action="CLAIM_APPROVED",
        entity_type="Claim",
        entity_id=claim_id
    ))
    
    await db.commit()
    return {"message": "Claim approved", "status": claim.status}

@router.get("/{claim_id}/audit")
async def get_claim_audit(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(AuditLog).where(AuditLog.claim_id == claim_id).order_by(AuditLog.created_at.desc()))
    audits = result.scalars().all()
    return [{
        "id": a.id,
        "action": a.action,
        "entity_type": a.entity_type,
        "old_value": a.old_value,
        "new_value": a.new_value,
        "created_at": a.created_at.isoformat()
    } for a in audits]

@router.post("/{claim_id}/icd/suggest")
async def suggest_icd(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim_res = await db.execute(select(Claim).where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id))
    claim = claim_res.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status != ClaimStatus.APPROVED.value:
        raise HTTPException(status_code=400, detail="Claim must be APPROVED to generate ICD suggestions")

    # Get diagnoses
    ext_res = await db.execute(select(ExtractionResult).where(ExtractionResult.claim_id == claim_id))
    ext = ext_res.scalars().first()
    
    if not ext or not ext.diagnosis_json:
        return {"message": "No diagnoses found to suggest for."}

    generated_count = 0
    # Check if we already generated
    existing_res = await db.execute(select(ClaimICDRecommendation).where(ClaimICDRecommendation.claim_id == claim_id))
    if existing_res.scalars().first():
        return {"message": "Suggestions already generated."}

    for diag in ext.diagnosis_json:
        diag_text = diag.get("description", "")
        if not diag_text:
            continue
        suggestions = await suggest_icd_codes(diag_text, db)
        for sug in suggestions:
            rec = ClaimICDRecommendation(
                claim_id=claim_id,
                diagnosis_text=diag_text,
                icd_code=sug["code"],
                confidence=sug["confidence"],
                source="FTS5_SEARCH",
                status=RecommendationStatus.SUGGESTED.value
            )
            db.add(rec)
        generated_count += len(suggestions)
        
    db.add(AuditLog(
        user_id=current_user.id,
        claim_id=claim_id,
        action="ICD_SUGGESTION_GENERATED",
        entity_type="Claim",
        entity_id=claim_id,
        new_value={"count": generated_count}
    ))
    
    await db.commit()
    return {"message": f"Generated {generated_count} suggestions"}


@router.get("/{claim_id}/icd")
async def get_icd_recommendations(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models import ICDCode
    stmt = select(ClaimICDRecommendation, ICDCode.description).join(
        ICDCode, ClaimICDRecommendation.icd_code == ICDCode.code
    ).where(ClaimICDRecommendation.claim_id == claim_id)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return [{
        "id": r[0].id,
        "diagnosis_text": r[0].diagnosis_text,
        "icd_code": r[0].icd_code,
        "description": r[1],
        "confidence": r[0].confidence,
        "status": r[0].status
    } for r in rows]


@router.post("/{claim_id}/icd/accept/{rec_id}")
async def accept_icd(
    claim_id: str,
    rec_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec_res = await db.execute(select(ClaimICDRecommendation).where(ClaimICDRecommendation.id == rec_id))
    rec = rec_res.scalars().first()
    if not rec or rec.claim_id != claim_id:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = RecommendationStatus.ACCEPTED.value
    
    db.add(AuditLog(
        user_id=current_user.id,
        claim_id=claim_id,
        action="ICD_ACCEPTED",
        entity_type="ClaimICDRecommendation",
        entity_id=rec_id,
        new_value={"icd_code": rec.icd_code}
    ))
    await db.commit()
    return {"message": "Accepted", "status": rec.status}


@router.post("/{claim_id}/icd/reject/{rec_id}")
async def reject_icd(
    claim_id: str,
    rec_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec_res = await db.execute(select(ClaimICDRecommendation).where(ClaimICDRecommendation.id == rec_id))
    rec = rec_res.scalars().first()
    if not rec or rec.claim_id != claim_id:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = RecommendationStatus.REJECTED.value
    
    db.add(AuditLog(
        user_id=current_user.id,
        claim_id=claim_id,
        action="ICD_REJECTED",
        entity_type="ClaimICDRecommendation",
        entity_id=rec_id,
        new_value={"icd_code": rec.icd_code}
    ))
    await db.commit()
    return {"message": "Rejected", "status": rec.status}

@router.post("/{claim_id}/generate-report")
async def generate_report(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models import Report
    from app.services.report_generator import build_iscs_report_data, generate_pdf
    import os

    claim_res = await db.execute(select(Claim).where(Claim.id == claim_id, Claim.organization_id == current_user.organization_id))
    claim = claim_res.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if claim.status not in (ClaimStatus.APPROVED.value, ClaimStatus.ICD_MAPPED.value, ClaimStatus.REPORT_GENERATED.value):
        raise HTTPException(status_code=400, detail="Claim must be APPROVED or ICD_MAPPED to generate report")

    # Prevent duplicate generation
    rep_res = await db.execute(select(Report).where(Report.claim_id == claim_id))
    report = rep_res.scalars().first()
    if report:
        return {
            "claim_id": claim_id,
            "report_id": report.id,
            "status": claim.status,
            "message": "Report already generated"
        }

    # 1. Build Data
    try:
        report_data = await build_iscs_report_data(claim_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build report data: {str(e)}")

    # 2. Generate PDF
    try:
        pdf_bytes = generate_pdf(report_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


    # 3. Save to disk
    uploads_dir = os.path.join(os.getcwd(), "uploads", "reports")
    os.makedirs(uploads_dir, exist_ok=True)
    file_name = f"ISCS_{claim.claim_number}.pdf"
    file_path = os.path.join(uploads_dir, file_name)

    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    # 4. Save to DB
    new_report = Report(
        claim_id=claim_id,
        file_name=file_name,
        file_path=file_path,
        version=1
    )
    db.add(new_report)
    
    from sqlalchemy.exc import IntegrityError
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # Duplicate concurrent request occurred.
        # Clean up orphaned file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Fetch the one that succeeded
        rep_res = await db.execute(select(Report).where(Report.claim_id == claim_id))
        report = rep_res.scalars().first()
        return {
            "claim_id": claim_id,
            "report_id": report.id,
            "status": claim.status,
            "message": "Report already generated (concurrent call handled)"
        }

    await db.refresh(new_report)

    return {
        "claim_id": claim_id,
        "report_id": new_report.id,
        "status": claim.status,
        "message": "Report generated successfully"
    }


@router.get("/{claim_id}/report")
async def get_report_metadata(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models import Report
    rep_res = await db.execute(select(Report).where(Report.claim_id == claim_id))
    report = rep_res.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "id": report.id,
        "claim_id": report.claim_id,
        "file_name": report.file_name,
        "version": report.version,
        "generated_at": report.generated_at.isoformat()
    }


@router.get("/{claim_id}/report/download")
async def download_report(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models import Report
    from fastapi.responses import FileResponse
    import os
    
    rep_res = await db.execute(select(Report).where(Report.claim_id == claim_id))
    report = rep_res.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    db.add(AuditLog(
        user_id=current_user.id,
        claim_id=claim_id,
        action="REPORT_DOWNLOADED",
        entity_type="Report",
        entity_id=report.id,
        new_value={"file_name": report.file_name}
    ))
    await db.commit()
    
    return FileResponse(
        path=report.file_path,
        filename=report.file_name,
        media_type="application/pdf"
    )
