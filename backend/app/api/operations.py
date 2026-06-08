from fastapi import APIRouter

from app.schemas.claims import OperationsOverview
from app.services.demo import get_operations_overview

router = APIRouter()


@router.get("/overview", response_model=OperationsOverview)
async def overview() -> OperationsOverview:
    return get_operations_overview()
