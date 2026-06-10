from app.schemas.claims import ClaimRecord, ClinicalExtraction
from app.services.nlp import enrich_extraction_with_nlp


def build_extraction_result(claim: ClaimRecord) -> ClinicalExtraction:
    # Empty schema until OCR is implemented
    extraction = ClinicalExtraction(
        patient_name=claim.patient_name or "Unknown",
        patient_age=0,
        patient_gender="Unknown",
        symptoms=[],
        diagnosis=[],
        procedures=[],
        investigations=[],
        medications=[],
        admission_details="",
        discharge_details="",
        confidence_scores={},
    )
    raw_text = " ".join(claim.documents + claim.diagnosis)
    return enrich_extraction_with_nlp(extraction, raw_text)
