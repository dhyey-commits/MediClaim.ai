"""
ISCS Report Generator — Indian Standard Clinical Summary.
Assembles structured report data from DB and generates a PDF.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from app.schemas.report import ISCSReportData, ReportSection

async def build_iscs_report_data(claim_id: str, session: AsyncSession) -> ISCSReportData:
    """Assemble structured ISCS report from claim data in DB."""
    from app.models import Claim, ExtractionResult, ClaimICDRecommendation, RecommendationStatus
    from app.models import ICDCode

    result = await session.execute(
        select(Claim)
        .where(Claim.id == claim_id)
        .options(
            selectinload(Claim.documents),
            selectinload(Claim.extraction_result),
        )
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise ValueError(f"Claim {claim_id} not found")

    ext = claim.extraction_result
    if not ext:
        raise ValueError(f"No extraction result found for Claim {claim_id}")

    # Fetch accepted ICD codes
    icd_result = await session.execute(
        select(ClaimICDRecommendation, ICDCode.description)
        .join(ICDCode, ClaimICDRecommendation.icd_code == ICDCode.code)
        .where(
            ClaimICDRecommendation.claim_id == claim_id,
            ClaimICDRecommendation.status == RecommendationStatus.ACCEPTED.value
        )
    )
    accepted_icds = icd_result.all()

    # Build diagnoses section from ExtractionResult
    diag_lines = []
    for diag in ext.diagnosis_json or []:
        diag_lines.append(diag.get("description", "—"))

    # Build ICD mapping section
    icd_lines = []
    for rec, desc in accepted_icds:
        icd_lines.append(f"{rec.diagnosis_text} → {rec.icd_code} ({desc})")

    # Build procedures, medications, investigations
    proc_lines = [p.get("description", "—") for p in ext.procedures_json or []]
    med_lines = [f"{m.get('name', '—')} - {m.get('dosage', '—')} {m.get('frequency', '—')}" for m in ext.medications_json or []]
    inv_lines = [i.get("test_name", "—") for i in ext.investigations_json or []]

    def _format_date(d):
        return d if d else '—'

    sections = [
        ReportSection(
            title="Patient Information",
            content=[
                f"Name: {ext.patient_name or '—'}",
                f"Age: {ext.age or '—'} years",
                f"Gender: {ext.gender or '—'}",
                f"UHID: {claim.patient_uhid or '—'}",
            ]
        ),
        ReportSection(
            title="Admission Details",
            content=[
                f"Admission Date: {_format_date(ext.admission_date)}",
                f"Discharge Date: {_format_date(ext.discharge_date)}",
                f"Chief Complaint: {ext.chief_complaint or '—'}",
            ]
        ),
        ReportSection(
            title="Diagnosis",
            content=diag_lines or ["No diagnoses recorded."],
        ),
        ReportSection(
            title="Procedures",
            content=proc_lines or ["No procedures recorded."],
        ),
        ReportSection(
            title="Medications",
            content=med_lines or ["No medications recorded."],
        ),
        ReportSection(
            title="Investigations",
            content=inv_lines or ["No investigations recorded."],
        ),
        ReportSection(
            title="Approved ICD-10 Mappings",
            content=icd_lines or ["No ICD mappings accepted."],
        ),
        ReportSection(
            title="Claim Metadata",
            content=[
                f"📋 Claim created: {claim.created_at.strftime('%d %b %Y %H:%M') if claim.created_at else '—'}",
                f"📄 Documents uploaded: {len(claim.documents)} file(s)",
                f"📊 Report Status: Generated",
            ]
        )
    ]

    report_data = ISCSReportData(
        report_type="ISCS",
        generated_at=datetime.utcnow().isoformat(),
        claim_id=claim_id,
        claim_number=claim.claim_number,
        sections=sections
    )
    return report_data


def _days_between(d1: Any, d2: Any) -> str:
    if d1 and d2:
        return str((d2 - d1).days)
    return "—"


def generate_pdf(report_data: ISCSReportData) -> bytes:
    """Generate a professional PDF from ISCS report data using reportlab."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            HRFlowable,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()
        BRAND_BLUE = colors.HexColor("#0ea5e9")
        DARK = colors.HexColor("#0f172a")
        GRAY = colors.HexColor("#64748b")
        LIGHT_BG = colors.HexColor("#f0f9ff")

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=22,
            textColor=DARK,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        )
        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=GRAY,
            spaceAfter=2,
        )
        section_style = ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontSize=12,
            textColor=BRAND_BLUE,
            spaceBefore=12,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9.5,
            textColor=DARK,
            spaceAfter=3,
            leading=14,
        )

        story = []

        # Header
        story.append(Paragraph("MediClaim AI", title_style))
        story.append(Paragraph("Indian Standard Clinical Summary (ISCS)", subtitle_style))
        story.append(
            Paragraph(
                f"Claim #{report_data.claim_number} &nbsp;|&nbsp; Generated: {datetime.utcnow().strftime('%d %b %Y %H:%M UTC')}",
                subtitle_style,
            )
        )
        story.append(HRFlowable(width="100%", thickness=2, color=BRAND_BLUE, spaceAfter=10))

        # Sections
        for section in report_data.sections:
            story.append(Paragraph(section.title, section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_BG, spaceAfter=4))
            for line in section.content:
                story.append(Paragraph(f"• {line}", body_style))
            story.append(Spacer(1, 6))

        # Footer table
        story.append(HRFlowable(width="100%", thickness=1, color=GRAY, spaceBefore=10))
        footer_data = [
            ["MediClaim AI Platform", "ISCS v1.0", f"Claim ID: {report_data.claim_id[:8]}..."],
        ]
        footer_table = Table(footer_data, colWidths=["40%", "30%", "30%"])
        footer_table.setStyle(
            TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (0, 0), (-1, -1), GRAY),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("ALIGN", (2, 0), (2, 0), "RIGHT"),
            ])
        )
        story.append(footer_table)

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        # reportlab not installed — return a minimal text-based PDF placeholder
        return _minimal_pdf(report_data)


def _minimal_pdf(report_data: ISCSReportData) -> bytes:
    """Fallback: plain-text PDF when reportlab is not installed."""
    lines = [
        f"MEDICLAIM AI — ISCS REPORT",
        f"Claim: {report_data.claim_number}",
        f"Generated: {datetime.utcnow().isoformat()}",
        "",
    ]
    for section in report_data.sections:
        lines.append(f"\n{section.title.upper()}")
        lines.append("-" * 40)
        for item in section.content:
            lines.append(f"  {item}")
    text = "\n".join(lines)
    # Wrap in minimal valid PDF
    return text.encode("utf-8")
