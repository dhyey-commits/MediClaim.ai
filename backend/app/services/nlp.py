from app.schemas.claims import ClinicalExtraction


def extract_medical_entities(raw_text: str) -> dict[str, list[str]]:
    # Empty until NLP is implemented
    return {}


def enrich_extraction_with_nlp(extraction: ClinicalExtraction, raw_text: str) -> ClinicalExtraction:
    entities = extract_medical_entities(raw_text)
    return extraction.model_copy(
        update={
            "symptoms": entities.get("symptoms", extraction.symptoms),
            "diagnosis": entities.get("diagnosis", extraction.diagnosis),
            "procedures": entities.get("procedures", extraction.procedures),
        }
    )
