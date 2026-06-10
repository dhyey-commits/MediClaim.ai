from app.schemas.claims import CopilotRequest, CopilotResponse


def generate_gpt_response(message: str) -> str | None:
    # Placeholder for OpenAI integration in production mode.
    # Return None in demo mode so deterministic rule-based handling is used.
    return None


def answer_copilot_request(request: CopilotRequest) -> CopilotResponse:
    raise NotImplementedError("Copilot not implemented yet")
