"""
ICD-10 seed data — common Indian hospital discharge diagnoses.
Only inserts codes that don't already exist (idempotent).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# (code, description, category)
ICD_SEED: list[tuple[str, str, str]] = [
    # Cardiovascular
    ("I21.9",  "Acute myocardial infarction, unspecified", "Cardiovascular"),
    ("I25.10", "Atherosclerotic heart disease, unspecified", "Cardiovascular"),
    ("I50.9",  "Heart failure, unspecified", "Cardiovascular"),
    ("I10",    "Essential (primary) hypertension", "Cardiovascular"),
    ("I48.91", "Unspecified atrial fibrillation", "Cardiovascular"),
    ("I63.9",  "Cerebral infarction, unspecified", "Cardiovascular"),
    ("I64",    "Stroke, not specified as haemorrhage or infarction", "Cardiovascular"),
    # Respiratory
    ("J18.9",  "Pneumonia, unspecified organism", "Respiratory"),
    ("J44.1",  "Chronic obstructive pulmonary disease with acute exacerbation", "Respiratory"),
    ("J06.9",  "Acute upper respiratory infection, unspecified", "Respiratory"),
    ("J45.909","Unspecified asthma, uncomplicated", "Respiratory"),
    ("J96.00", "Acute respiratory failure, unspecified", "Respiratory"),
    # Endocrine
    ("E11.9",  "Type 2 diabetes mellitus without complications", "Endocrine"),
    ("E11.65", "Type 2 diabetes mellitus with hyperglycemia", "Endocrine"),
    ("E10.9",  "Type 1 diabetes mellitus without complications", "Endocrine"),
    ("E03.9",  "Hypothyroidism, unspecified", "Endocrine"),
    ("E05.90", "Thyrotoxicosis, unspecified, without thyrotoxic crisis", "Endocrine"),
    # Gastrointestinal
    ("K92.1",  "Melena", "Gastrointestinal"),
    ("K85.9",  "Acute pancreatitis, unspecified", "Gastrointestinal"),
    ("K80.20", "Calculus of gallbladder without cholecystitis, without obstruction", "Gastrointestinal"),
    ("K57.30", "Diverticulosis of large intestine without perforation or abscess, without bleeding", "Gastrointestinal"),
    ("K25.9",  "Gastric ulcer, unspecified", "Gastrointestinal"),
    # Renal
    ("N18.9",  "Chronic kidney disease, unspecified", "Renal"),
    ("N39.0",  "Urinary tract infection, site not specified", "Renal"),
    ("N20.0",  "Calculus of kidney", "Renal"),
    # Infectious
    ("A09",    "Other and unspecified gastroenteritis and colitis of infectious origin", "Infectious"),
    ("A90",    "Dengue fever [classical dengue]", "Infectious"),
    ("A91",    "Dengue haemorrhagic fever", "Infectious"),
    ("A01.0",  "Typhoid fever", "Infectious"),
    ("B34.9",  "Viral infection, unspecified", "Infectious"),
    ("A15.0",  "Tuberculosis of lung", "Infectious"),
    # Musculoskeletal
    ("M79.3",  "Panniculitis, unspecified", "Musculoskeletal"),
    ("M54.5",  "Low back pain", "Musculoskeletal"),
    ("M17.11", "Primary osteoarthritis, right knee", "Musculoskeletal"),
    # Neurological
    ("G43.909","Migraine, unspecified, not intractable, without status migrainosus", "Neurological"),
    ("G40.909","Epilepsy, unspecified, not intractable, without status epilepticus", "Neurological"),
    # Obstetric
    ("O80",    "Encounter for full-term uncomplicated delivery", "Obstetric"),
    ("O34.21", "Maternal care for scar from previous cesarean delivery", "Obstetric"),
    # Injury
    ("S72.001A","Fracture of unspecified part of neck of right femur, initial encounter", "Injury"),
    ("S06.0X9A","Concussion with loss of consciousness of unspecified duration, initial encounter", "Injury"),
    # Cancer
    ("C34.90", "Malignant neoplasm of unspecified part of unspecified bronchus or lung", "Oncology"),
    ("C50.919","Malignant neoplasm of unspecified site of unspecified female breast", "Oncology"),
    # Anaemia
    ("D64.9",  "Anaemia, unspecified", "Haematology"),
    ("D50.9",  "Iron deficiency anaemia, unspecified", "Haematology"),
]


async def seed_icd_codes(session: AsyncSession) -> None:
    from app.models import ICDCode  # noqa: PLC0415

    # Check if already seeded
    result = await session.execute(select(ICDCode).limit(1))
    if result.scalar_one_or_none() is not None:
        return  # already seeded

    for code, description, category in ICD_SEED:
        session.add(ICDCode(code=code, description=description, category=category))

    await session.commit()
    print(f"[OK] Seeded {len(ICD_SEED)} ICD-10 codes")
