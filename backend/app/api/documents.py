"""Documents router — browse all documents, view extracted text."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.models import Claim, Document

router = APIRouter()


class DocumentDetailOut(BaseModel):
    id: str
    claim_id: str
    claim_number: str | None
    file_name: str
    file_type: str | None
    file_size: int | None
    status: str
    extracted_text: str | None
    confidence_score: float
    page_count: int
    created_at: str


@router.get("")
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[DocumentDetailOut]:
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.claim))
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    docs = result.scalars().all()

    return [
        DocumentDetailOut(
            id=d.id,
            claim_id=d.claim_id,
            claim_number=d.claim.claim_number if d.claim else None,
            file_name=d.file_name,
            file_type=d.file_type,
            file_size=d.file_size,
            status=d.status,
            extracted_text=d.extracted_text,
            confidence_score=d.confidence_score or 0.0,
            page_count=d.page_count or 1,
            created_at=d.created_at.isoformat() if d.created_at else "",
        )
        for d in docs
    ]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
) -> DocumentDetailOut:
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.claim))
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentDetailOut(
        id=doc.id,
        claim_id=doc.claim_id,
        claim_number=doc.claim.claim_number if doc.claim else None,
        file_name=doc.file_name,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status=doc.status,
        extracted_text=doc.extracted_text,
        confidence_score=doc.confidence_score or 0.0,
        page_count=doc.page_count or 1,
        created_at=doc.created_at.isoformat() if doc.created_at else "",
    )
