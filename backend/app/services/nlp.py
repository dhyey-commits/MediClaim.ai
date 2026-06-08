from app.schemas.claims import ClinicalExtraction


def extract_medical_entities(raw_text: str) -> dict[str, list[str]]:
    # Stubbed NLP output for demo environments.
    return {
        "symptoms": ["Fever", "Weakness"],
        "diagnosis": ["Viral fever"],
        "procedures": ["IV hydration"],
    }


def enrich_extraction_with_nlp(extraction: ClinicalExtraction, raw_text: str) -> ClinicalExtraction:
    entities = extract_medical_entities(raw_text)
    return extraction.model_copy(
        update={
            "symptoms": entities.get("symptoms", extraction.symptoms),
            "diagnosis": entities.get("diagnosis", extraction.diagnosis),
            "procedures": entities.get("procedures", extraction.procedures),
        }
    )
