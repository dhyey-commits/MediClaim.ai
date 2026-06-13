import re
import sys

def update_main():
    path = "app/main.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    arq_imports = """
from arq import create_pool
from app.worker import redis_settings
"""
    content = content.replace("from fastapi import FastAPI", arq_imports + "from fastapi import FastAPI")

    pool_init = """
    app.state.redis = await create_pool(redis_settings)
    print("[OK] ARQ Redis Pool initialized")
"""
    pool_close = """
    await app.state.redis.close()
"""
    content = content.replace("    try:\n        await init_db()", pool_init + "\n    try:\n        await init_db()")
    content = content.replace("    yield\n    logger.info(\"[MediClaim AI] API shutting down\")", "    yield\n" + pool_close + "    logger.info(\"[MediClaim AI] API shutting down\")")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def update_claims():
    path = "app/api/claims.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # We need to change the function signatures to take Request instead of BackgroundTasks
    # And then do `await request.app.state.redis.enqueue_job(...)`
    # Also we need to add the BackgroundJob to DB
    
    # 1. OCR trigger
    content = content.replace(
        "    background_tasks: BackgroundTasks,",
        "    request: Request,"
    )
    
    # In trigger_ocr, replace the background tasks logic:
    ocr_wrapper_old = """    from app.database.database import AsyncSessionLocal
    async def ocr_wrapper(cid: str):
        async with AsyncSessionLocal() as session:
            await run_ocr_for_claim(cid, current_user.id, session)
            
    background_tasks.add_task(ocr_wrapper, claim_id)"""
    
    ocr_arq_new = """    from app.models import BackgroundJob, JobStatus
    import uuid
    job_id = uuid.uuid4().hex
    db.add(BackgroundJob(
        id=job_id,
        claim_id=claim_id,
        job_type="OCR",
        status=JobStatus.QUEUED.value
    ))
    db.add(AuditLog(
        claim_id=claim_id,
        action="JOB_QUEUED",
        entity_type="BackgroundJob",
        entity_id=job_id,
        new_value={"job_type": "OCR"}
    ))
    await db.commit()
    await request.app.state.redis.enqueue_job('ocr_task', job_id, claim_id, current_user.id, _job_id=job_id)"""
    
    content = content.replace(ocr_wrapper_old, ocr_arq_new)

    # 2. Extraction trigger
    extraction_wrapper_old = """    from app.database.database import AsyncSessionLocal
    async def extraction_wrapper(cid: str):
        async with AsyncSessionLocal() as session:
            try:
                await run_extraction_for_claim(cid, current_user.id, session)
            except Exception as e:
                print(f"Extraction failed: {e}")

    background_tasks.add_task(extraction_wrapper, claim_id)"""

    extraction_arq_new = """    from app.models import BackgroundJob, JobStatus
    import uuid
    job_id = uuid.uuid4().hex
    db.add(BackgroundJob(
        id=job_id,
        claim_id=claim_id,
        job_type="EXTRACTION",
        status=JobStatus.QUEUED.value
    ))
    db.add(AuditLog(
        claim_id=claim_id,
        action="JOB_QUEUED",
        entity_type="BackgroundJob",
        entity_id=job_id,
        new_value={"job_type": "EXTRACTION"}
    ))
    await db.commit()
    await request.app.state.redis.enqueue_job('extraction_task', job_id, claim_id, current_user.id, _job_id=job_id)"""
    
    content = content.replace(extraction_wrapper_old, extraction_arq_new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_main()
    update_claims()
