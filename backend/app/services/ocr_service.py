from app.schemas.claims import ClaimRecord, ClinicalExtraction
from app.services.demo import get_demo_extraction
from app.services.nlp import enrich_extraction_with_nlp


def build_extraction_result(claim: ClaimRecord) -> ClinicalExtraction:
    extraction = get_demo_extraction()
    extraction = extraction.model_copy(update={"patient_name": claim.patient_name})
    raw_text = " ".join(claim.documents + claim.diagnosis)
    return enrich_extraction_with_nlp(extraction, raw_text)
