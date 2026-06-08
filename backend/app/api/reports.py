"""Reports router — list, view and download ISCS reports."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pathlib import Path
from typing import Any

from app.database.database import get_db
from app.models import Claim, Report

router = APIRouter()


class ReportListItem(BaseModel):
    id: str
    claim_id: str
    claim_number: str | None
    patient_name: str | None
    report_type: str
    is_generated: bool
    created_at: str


class ReportDetailOut(BaseModel):
    id: str
    claim_id: str
    claim_number: str | None
    patient_name: str | None
    report_type: str
    report_data: dict[str, Any] | None
    is_generated: bool
    version: int
    created_at: str


@router.get("")
async def list_reports(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[ReportListItem]:
    result = await db.execute(
        select(Report)
        .options(selectinload(Report.claim))
        .order_by(Report.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reports = result.scalars().all()

    return [
        ReportListItem(
            id=r.id,
            claim_id=r.claim_id,
            claim_number=r.claim.claim_number if r.claim else None,
            patient_name=r.claim.patient_name if r.claim else None,
            report_type=r.report_type or "ISCS",
            is_generated=r.is_generated,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in reports
    ]


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
) -> ReportDetailOut:
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .options(selectinload(Report.claim))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportDetailOut(
        id=report.id,
        claim_id=report.claim_id,
        claim_number=report.claim.claim_number if report.claim else None,
        patient_name=report.claim.patient_name if report.claim else None,
        report_type=report.report_type or "ISCS",
        report_data=report.report_data,
        is_generated=report.is_generated,
        version=report.version or 1,
        created_at=report.created_at.isoformat() if report.created_at else "",
    )


@router.get("/{report_id}/download")
async def download_report_pdf(
    report_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .options(selectinload(Report.claim))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not report.is_generated or not report.pdf_path:
        raise HTTPException(status_code=400, detail="PDF not yet generated")

    pdf_path = Path(report.pdf_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    claim_number = report.claim.claim_number if report.claim else "report"
    filename = f"ISCS_{claim_number}.pdf"

    return Response(
        content=pdf_path.read_bytes(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
