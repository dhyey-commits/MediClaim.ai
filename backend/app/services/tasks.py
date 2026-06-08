from app.core.celery_app import celery_app


@celery_app.task(name="tasks.ocr_pipeline")
def run_ocr_pipeline(claim_id: str) -> dict[str, str]:
    return {"claim_id": claim_id, "status": "queued"}


@celery_app.task(name="tasks.iscs_generation")
def run_iscs_generation(claim_id: str) -> dict[str, str]:
    return {"claim_id": claim_id, "status": "queued"}
