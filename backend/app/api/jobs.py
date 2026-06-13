from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database.database import get_db
from app.core.security import get_current_user
from app.models import BackgroundJob, User, Claim

router = APIRouter(prefix="/jobs", tags=["Jobs"])

class JobOut(BaseModel):
    id: str
    claim_id: Optional[str]
    job_type: str
    status: str
    retry_count: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[JobOut])
async def list_jobs(
    claim_id: Optional[str] = Query(None, description="Filter by claim ID"),
    status: Optional[str] = Query(None, description="Filter by status (e.g., QUEUED, RUNNING)"),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(BackgroundJob).join(Claim).where(Claim.organization_id == current_user.organization_id)
    
    if claim_id:
        stmt = stmt.where(BackgroundJob.claim_id == claim_id)
    if status:
        stmt = stmt.where(BackgroundJob.status == status)
        
    stmt = stmt.order_by(BackgroundJob.created_at.desc()).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{job_id}", response_model=JobOut)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(BackgroundJob).join(Claim).where(
        BackgroundJob.id == job_id,
        Claim.organization_id == current_user.organization_id
    )
    res = await db.execute(stmt)
    job = res.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
