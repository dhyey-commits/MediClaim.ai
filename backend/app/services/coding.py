from app.schemas.claims import ClinicalExtraction, CodeSuggestion
def map_diagnosis_to_codes(extraction: ClinicalExtraction) -> list[CodeSuggestion]:
    # In production, this would call a terminology service for ICD-10/SNOMED/CPT/RxNorm mapping.
    return []


def build_coding_response(extraction: ClinicalExtraction) -> list[CodeSuggestion]:
    return map_diagnosis_to_codes(extraction)
