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


async def build_iscs_report_data(claim_id: str, session: AsyncSession) -> dict[str, Any]:
    """Assemble structured ISCS report from claim data in DB."""
    from app.models import Claim  # noqa: PLC0415

    result = await session.execute(
        select(Claim)
        .where(Claim.id == claim_id)
        .options(
            selectinload(Claim.documents),
            selectinload(Claim.diagnoses),
            selectinload(Claim.extracted_entities),
        )
    )
    claim = result.scalar_one_or_none()
    if not claim:
        raise ValueError(f"Claim {claim_id} not found")

    # Group entities by type
    entities_by_type: dict[str, list[str]] = {}
    for ent in claim.extracted_entities:
        entities_by_type.setdefault(ent.entity_type, []).append(ent.value)

    # Build diagnoses section
    diag_lines = []
    for diag in claim.diagnoses:
        code = diag.icd_code_override or (diag.icd_code.code if diag.icd_code else "—")
        diag_lines.append(f"{diag.description} [{code}]")

    report_data = {
        "report_type": "ISCS",
        "generated_at": datetime.utcnow().isoformat(),
        "claim_id": claim_id,
        "claim_number": claim.claim_number,
        "sections": [
            {
                "title": "Patient Information",
                "content": [
                    f"Name: {claim.patient_name or '—'}",
                    f"Age: {claim.patient_age or '—'} years",
                    f"Gender: {claim.patient_gender or '—'}",
                    f"UHID: {claim.patient_uhid or '—'}",
                ],
            },
            {
                "title": "Admission Details",
                "content": [
                    f"Admission Date: {claim.admission_date.strftime('%d %b %Y') if claim.admission_date else '—'}",
                    f"Discharge Date: {claim.discharge_date.strftime('%d %b %Y') if claim.discharge_date else '—'}",
                    f"Duration: {_days_between(claim.admission_date, claim.discharge_date)} days",
                    f"Chief Complaint: {claim.chief_complaint or '—'}",
                ],
            },
            {
                "title": "Clinical Findings",
                "content": entities_by_type.get("finding", ["No clinical findings recorded."]),
            },
            {
                "title": "Investigations",
                "content": entities_by_type.get("investigation", ["No investigations recorded."]),
            },
            {
                "title": "Diagnosis",
                "content": diag_lines or ["No diagnoses recorded."],
            },
            {
                "title": "Procedures",
                "content": entities_by_type.get("procedure", ["No procedures recorded."]),
            },
            {
                "title": "Medications",
                "content": entities_by_type.get("medication", ["No medications recorded."]),
            },
            {
                "title": "ICD-10 Mapping",
                "content": [
                    f"{diag.description} → {diag.icd_code_override or (diag.icd_code.code if diag.icd_code else '—')} (Confidence: {int(diag.confidence * 100)}%)"
                    for diag in claim.diagnoses
                ] or ["No ICD mappings generated."],
            },
            {
                "title": "Clinical Timeline",
                "content": [
                    f"📋 Claim created: {claim.created_at.strftime('%d %b %Y %H:%M') if claim.created_at else '—'}",
                    f"📄 Documents uploaded: {len(claim.documents)} file(s)",
                    f"🔬 AI Extraction: {'Complete' if claim.status in ('EXTRACTION_COMPLETE', 'ICD_MAPPED', 'REPORT_GENERATED') else 'Pending'}",
                    f"🏷️  ICD Mapping: {'Complete' if claim.status in ('ICD_MAPPED', 'REPORT_GENERATED') else 'Pending'}",
                    f"📊 Report Status: {'Generated' if claim.status == 'REPORT_GENERATED' else 'Pending'}",
                ],
            },
        ],
    }
    return report_data


def _days_between(d1: Any, d2: Any) -> str:
    if d1 and d2:
        return str((d2 - d1).days)
    return "—"


def generate_pdf(report_data: dict[str, Any]) -> bytes:
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
                f"Claim #{report_data.get('claim_number', '—')} &nbsp;|&nbsp; Generated: {datetime.utcnow().strftime('%d %b %Y %H:%M UTC')}",
                subtitle_style,
            )
        )
        story.append(HRFlowable(width="100%", thickness=2, color=BRAND_BLUE, spaceAfter=10))

        # Sections
        for section in report_data.get("sections", []):
            story.append(Paragraph(section["title"], section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_BG, spaceAfter=4))
            for line in section.get("content", []):
                story.append(Paragraph(f"• {line}", body_style))
            story.append(Spacer(1, 6))

        # Footer table
        story.append(HRFlowable(width="100%", thickness=1, color=GRAY, spaceBefore=10))
        footer_data = [
            ["MediClaim AI Platform", "ISCS v1.0", f"Claim ID: {report_data.get('claim_id', '—')[:8]}..."],
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


def _minimal_pdf(report_data: dict[str, Any]) -> bytes:
    """Fallback: plain-text PDF when reportlab is not installed."""
    lines = [
        f"MEDICLAIM AI — ISCS REPORT",
        f"Claim: {report_data.get('claim_number', '—')}",
        f"Generated: {datetime.utcnow().isoformat()}",
        "",
    ]
    for section in report_data.get("sections", []):
        lines.append(f"\n{section['title'].upper()}")
        lines.append("-" * 40)
        for item in section.get("content", []):
            lines.append(f"  {item}")
    text = "\n".join(lines)
    # Wrap in minimal valid PDF
    return text.encode("utf-8")
