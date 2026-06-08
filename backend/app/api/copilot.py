from fastapi import APIRouter

from app.schemas.claims import CopilotRequest, CopilotResponse
from app.services.copilot import answer_copilot_request

router = APIRouter()


@router.post("/chat", response_model=CopilotResponse)
async def chat(request: CopilotRequest) -> CopilotResponse:
    return answer_copilot_request(request)
