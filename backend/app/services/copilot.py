from app.schemas.claims import CopilotRequest, CopilotResponse


def generate_gpt_response(message: str) -> str | None:
    # Placeholder for OpenAI integration in production mode.
    # Return None in demo mode so deterministic rule-based handling is used.
    return None


def answer_copilot_request(request: CopilotRequest) -> CopilotResponse:
    message = request.message.lower()
    gpt_reply = generate_gpt_response(message)

    if gpt_reply:
        return CopilotResponse(
            message=gpt_reply,
            suggested_actions=["Explain coding", "Summarize record", "Highlight missing evidence"],
            confidence=0.88,
        )

    if "icd" in message:
        reply = "The code maps the diagnosis to an insurance and billing standard. I can explain the label, code family, and confidence."
        actions = ["Explain the ICD code", "Show mapped diagnosis", "Suggest a manual override"]
    elif "missing" in message or "document" in message:
        reply = "The packet needs a discharge signature, a supporting investigation, or an updated procedure note."
        actions = ["List missing documents", "Open validation issues", "Generate reminder"]
    elif "reject" in message:
        reply = "The rejection is typically due to incomplete evidence, inconsistent diagnosis mapping, or a missing signature trail."
        actions = ["Summarize rejection reasons", "Show insurer notes", "Draft appeal summary"]
    else:
        reply = "I can summarize the record, explain coding decisions, and help prepare insurer-ready notes."
        actions = ["Summarize the chart", "Explain coding choices", "Prepare claim summary"]

    return CopilotResponse(message=reply, suggested_actions=actions, confidence=0.93)
