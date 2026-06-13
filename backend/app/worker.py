import asyncio
import logging
from arq.connections import RedisSettings
from sqlalchemy.future import select

from app.core.config import settings
from app.database.database import AsyncSessionLocal
from app.models import BackgroundJob, JobStatus, AuditLog
from app.core.logger import get_logger

logger = get_logger("worker")

redis_settings = RedisSettings.from_dsn(settings.redis_url)

async def update_job_status(job_id: str, status: JobStatus, error_message: str = None, retry_count: int = None):
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
        job = res.scalars().first()
        if job:
            job.status = status.value
            if error_message:
                job.error_message = error_message
            if retry_count is not None:
                job.retry_count = retry_count
            await db.commit()

async def log_job_audit(job_id: str, action: str):
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
        job = res.scalars().first()
        if job:
            db.add(AuditLog(
                claim_id=job.claim_id,
                action=action,
                entity_type="BackgroundJob",
                entity_id=job_id,
                new_value={"job_type": job.job_type, "status": job.status}
            ))
            await db.commit()

async def handle_job_start(job_id: str, job_try: int):
    status = JobStatus.RUNNING if job_try == 1 else JobStatus.RETRYING
    await update_job_status(job_id, status, retry_count=job_try - 1)
    await log_job_audit(job_id, "JOB_STARTED" if job_try == 1 else "JOB_RETRYING")

async def handle_job_complete(job_id: str):
    await update_job_status(job_id, JobStatus.COMPLETED)
    await log_job_audit(job_id, "JOB_COMPLETED")

async def handle_job_exception(job_id: str, exc: Exception):
    await update_job_status(job_id, JobStatus.FAILED, error_message=str(exc))
    await log_job_audit(job_id, "JOB_FAILED")

# --- Tasks ---

async def ocr_task(ctx, job_id: str, claim_id: str, user_id: str):
    job_try = ctx.get('job_try', 1)
    await handle_job_start(job_id, job_try)
    try:
        from app.services.ocr_service import run_ocr_for_claim
        async with AsyncSessionLocal() as db:
            await run_ocr_for_claim(claim_id, user_id, db)
        await handle_job_complete(job_id)
    except Exception as e:
        await handle_job_exception(job_id, e)
        raise

async def extraction_task(ctx, job_id: str, claim_id: str, user_id: str):
    job_try = ctx.get('job_try', 1)
    await handle_job_start(job_id, job_try)
    try:
        from app.services.extraction_service import run_extraction_for_claim
        async with AsyncSessionLocal() as db:
            await run_extraction_for_claim(claim_id, user_id, db)
        await handle_job_complete(job_id)
    except Exception as e:
        await handle_job_exception(job_id, e)
        raise

async def icd_task(ctx, job_id: str, claim_id: str, user_id: str):
    job_try = ctx.get('job_try', 1)
    await handle_job_start(job_id, job_try)
    try:
        from app.services.icd_mapper_service import run_icd_mapping
        async with AsyncSessionLocal() as db:
            try:
                await run_icd_mapping(claim_id, db)
            except TypeError:
                await run_icd_mapping(claim_id, user_id, db)
        await handle_job_complete(job_id)
    except Exception as e:
        await handle_job_exception(job_id, e)
        raise

async def startup(ctx):
    logger.info("ARQ Worker starting up...")

async def shutdown(ctx):
    logger.info("ARQ Worker shutting down...")

class WorkerSettings:
    functions = [ocr_task, extraction_task, icd_task]
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown
    max_tries = 3
    job_timeout = 300
