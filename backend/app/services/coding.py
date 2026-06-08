from app.schemas.claims import ClinicalExtraction, CodeSuggestion
from app.services.demo import get_demo_coding


def map_diagnosis_to_codes(extraction: ClinicalExtraction) -> list[CodeSuggestion]:
    # In production, this would call a terminology service for ICD-10/SNOMED/CPT/RxNorm mapping.
    return get_demo_coding()


def build_coding_response(extraction: ClinicalExtraction) -> list[CodeSuggestion]:
    return map_diagnosis_to_codes(extraction)
