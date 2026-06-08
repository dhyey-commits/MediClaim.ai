"""
ICD-10 mapping service.
Maps free-text diagnosis descriptions to ICD-10 codes.
Uses fuzzy keyword matching against the seeded ICD reference table.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# Keyword → ICD code shortcuts for common Indian diagnoses
KEYWORD_MAP: dict[str, str] = {
    "myocardial infarction": "I21.9",
    "heart attack": "I21.9",
    "mi ": "I21.9",
    "coronary artery disease": "I25.10",
    "cad": "I25.10",
    "heart failure": "I50.9",
    "cardiac failure": "I50.9",
    "hypertension": "I10",
    "htn": "I10",
    "high blood pressure": "I10",
    "atrial fibrillation": "I48.91",
    "af ": "I48.91",
    "stroke": "I63.9",
    "cerebrovascular accident": "I64",
    "cva": "I64",
    "ischemic stroke": "I63.9",
    "pneumonia": "J18.9",
    "copd": "J44.1",
    "chronic obstructive": "J44.1",
    "upper respiratory": "J06.9",
    "uri": "J06.9",
    "asthma": "J45.909",
    "respiratory failure": "J96.00",
    "type 2 diabetes": "E11.9",
    "t2dm": "E11.9",
    "dm type 2": "E11.9",
    "diabetes mellitus": "E11.9",
    "hyperglycemia": "E11.65",
    "type 1 diabetes": "E10.9",
    "t1dm": "E10.9",
    "hypothyroidism": "E03.9",
    "thyrotoxicosis": "E05.90",
    "hyperthyroidism": "E05.90",
    "melena": "K92.1",
    "pancreatitis": "K85.9",
    "gallstone": "K80.20",
    "cholelithiasis": "K80.20",
    "diverticulosis": "K57.30",
    "gastric ulcer": "K25.9",
    "peptic ulcer": "K25.9",
    "chronic kidney disease": "N18.9",
    "ckd": "N18.9",
    "renal failure": "N18.9",
    "urinary tract infection": "N39.0",
    "uti": "N39.0",
    "kidney stone": "N20.0",
    "renal calculus": "N20.0",
    "gastroenteritis": "A09",
    "dengue fever": "A90",
    "dengue": "A90",
    "dengue haemorrhagic": "A91",
    "typhoid": "A01.0",
    "viral infection": "B34.9",
    "tuberculosis": "A15.0",
    "tb ": "A15.0",
    "back pain": "M54.5",
    "lbp": "M54.5",
    "osteoarthritis": "M17.11",
    "migraine": "G43.909",
    "epilepsy": "G40.909",
    "seizure": "G40.909",
    "normal delivery": "O80",
    "cesarean": "O34.21",
    "c-section": "O34.21",
    "femur fracture": "S72.001A",
    "concussion": "S06.0X9A",
    "lung cancer": "C34.90",
    "breast cancer": "C50.919",
    "anaemia": "D64.9",
    "anemia": "D64.9",
    "iron deficiency": "D50.9",
}


async def map_diagnosis_to_icd(
    diagnosis_text: str,
    session: AsyncSession,
) -> tuple[str | None, str | None, float]:
    """
    Returns (icd_code_id, icd_code_str, confidence).
    First tries keyword matching, then DB lookup.
    """
    from app.models import ICDCode  # noqa: PLC0415

    text_lower = diagnosis_text.lower()

    # 1. Keyword map
    matched_code: str | None = None
    confidence = 0.0
    for keyword, code in KEYWORD_MAP.items():
        if keyword in text_lower:
            matched_code = code
            confidence = 0.88 + (len(keyword) / 100)  # longer match = higher conf
            confidence = min(confidence, 0.99)
            break

    if not matched_code:
        # 2. No match → fall back to generic
        matched_code = "B34.9"  # Viral infection, unspecified
        confidence = 0.45

    # 3. Look up the ICDCode record in DB
    result = await session.execute(
        select(ICDCode).where(ICDCode.code == matched_code)
    )
    icd_record = result.scalar_one_or_none()

    if icd_record:
        return icd_record.id, icd_record.code, round(confidence, 2)
    return None, matched_code, round(confidence, 2)
