from fastapi import APIRouter

from app.schemas.claims import RolePermission

router = APIRouter()


@router.get("/roles", response_model=list[RolePermission])
async def roles() -> list[RolePermission]:
    return []
