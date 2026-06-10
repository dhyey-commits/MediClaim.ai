from fastapi import APIRouter

from app.schemas.claims import OperationsOverview

router = APIRouter()


@router.get("/overview", response_model=OperationsOverview)
async def overview() -> OperationsOverview:
    return OperationsOverview(notifications=[], api_keys=[], webhooks=[], audit_events=[])
