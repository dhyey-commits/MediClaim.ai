"""
Real clinical extraction service using GPT-4o Vision.
"""

from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


async def extract_clinical_data(
    file_path: str,
    claim_id: str,
    document_id: str,
) -> dict:
    """
    Extract clinical data from a document.
    Uses GPT-4o Vision if OPENAI_API_KEY is configured.
    """
    if settings.openai_api_key:
        return await _extract_with_openai(file_path, claim_id)
    else:
        raise NotImplementedError("OCR extraction not yet implemented. Please configure OPENAI_API_KEY.")


async def _extract_with_openai(file_path: str, claim_id: str) -> dict:
    """Real GPT-4o Vision extraction pipeline."""
    import base64

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        path = Path(file_path)
        with open(path, "rb") as f:
            file_bytes = f.read()

        b64 = base64.b64encode(file_bytes).decode()

        # Determine media type
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            media_type = "application/pdf"
        elif suffix in (".jpg", ".jpeg"):
            media_type = "image/jpeg"
        elif suffix == ".png":
            media_type = "image/png"
        else:
            media_type = "application/octet-stream"

        prompt = """You are a medical AI assistant specialized in analyzing Indian hospital discharge summaries.
Extract the following information from the provided document and return a JSON object with these exact keys:
{
  "patient_name": "string",
  "patient_age": integer,
  "patient_gender": "Male|Female|Other",
  "patient_uhid": "string or null",
  "admission_date": "YYYY-MM-DD or null",
  "discharge_date": "YYYY-MM-DD or null",
  "chief_complaint": "string",
  "diagnoses": ["list", "of", "diagnosis", "strings"],
  "procedures": ["list", "of", "procedure", "strings"],
  "medications": ["list", "of", "medication", "strings"],
  "investigations": ["list", "of", "investigation", "strings"],
  "confidence_scores": {
    "patient_name": 0.95,
    "diagnoses": 0.90,
    "procedures": 0.85,
    "medications": 0.88,
    "investigations": 0.92
  }
}
Be thorough and extract ALL diagnoses, medications, and procedures mentioned."""

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{b64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
        )

        import json
        return json.loads(response.choices[0].message.content or "{}")
    except Exception as e:
        print(f"OpenAI extraction failed: {e}")
        raise NotImplementedError(f"OCR extraction failed: {e}")
