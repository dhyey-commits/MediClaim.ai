from fastapi import APIRouter

from app.schemas.claims import RolePermission
from app.services.demo import get_role_permissions

router = APIRouter()


@router.get("/roles", response_model=list[RolePermission])
async def roles() -> list[RolePermission]:
    return get_role_permissions()
