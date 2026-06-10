"""
Claims API Router — Week 1 MVP: Create, List, Detail, Upload.
All endpoints backed by real PostgreSQL queries.
"""

from __future__ import annotations

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
)
from app.services.storage import save_file

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
        claim_id=claim_id,
        action=f"Uploaded {len(uploaded)} document(s)",
        entity_type="Document",
    ))
    await db.commit()

    return {"claim_id": claim_id, "uploaded": len(uploaded), "files": uploaded}
