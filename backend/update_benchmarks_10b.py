import re

def update_benchmarks():
    path = "app/api/benchmarks.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add imports for UploadFile, File, Request, etc.
    if "UploadFile" not in content:
        content = content.replace("from fastapi import APIRouter, Depends, HTTPException, Query", 
                                  "from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request")
        content = content.replace("from app.models import BenchmarkRun, User, Claim",
                                  "from app.models import BenchmarkRun, User, Claim, Document, ClaimStatus, DocumentStatus, AuditLog, BackgroundJob, JobStatus\nfrom app.services.storage import save_file\nimport uuid")

    # 2. Add POST /upload endpoint
    new_upload = """@router.post("/upload")
async def upload_benchmark(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    \"\"\"Ingests a real clinical PDF as a benchmark document\"\"\"
    # Create Claim with is_benchmark=True
    from app.api.claims import _generate_claim_number
    claim = Claim(
        claim_number=_generate_claim_number(),
        patient_name="Benchmark Document",
        status=ClaimStatus.DOCUMENT_UPLOADED.value,
        organization_id=current_user.organization_id,
        is_benchmark=True
    )
    db.add(claim)
    await db.commit()
    await db.refresh(claim)

    # Save file and create Document
    file_path, file_size = await save_file(file, claim.id)
    doc = Document(
        claim_id=claim.id,
        file_name=file.filename or "benchmark.pdf",
        file_type=file.content_type,
        file_path=file_path,
        file_size=file_size,
        status=DocumentStatus.PENDING.value,
    )
    db.add(doc)
    
    # Enqueue OCR automatically
    job_id = str(uuid.uuid4())
    job = BackgroundJob(
        id=job_id,
        claim_id=claim.id,
        job_type="OCR",
        status=JobStatus.QUEUED.value
    )
    db.add(job)
    await db.commit()
    
    await request.app.state.redis.enqueue_job('ocr_task', job_id, claim.id, current_user.id, _job_id=job_id)
    
    return {"message": "Benchmark dataset ingested and queued for OCR", "claim_id": claim.id}

"""
    if "def upload_benchmark" not in content:
        # Insert before evaluate_run
        content = content.replace("@router.post(\"/evaluate\")", new_upload + "@router.post(\"/evaluate\")")

    # 3. Update EvaluateRequest
    if "class EvaluateRequest" in content:
        old_evaluate_req = """class EvaluateRequest(BaseModel):
    claim_id: str
    document_source: str
    ground_truth: dict
    system_output: dict
    review_time_sec: Optional[float] = None
    correction_time_sec: Optional[float] = None
    approval_time_sec: Optional[float] = None"""

        new_evaluate_req = """class EvaluateRequest(BaseModel):
    claim_id: str
    document_source: str
    ground_truth: dict
    system_output: dict
    review_time_sec: Optional[float] = None
    correction_time_sec: Optional[float] = None
    approval_time_sec: Optional[float] = None"""
    # no change to model here, but we update evaluate_run to save ground_truth
    
    old_run = """    run = BenchmarkRun(
        claim_id=req.claim_id,
        organization_id=org_id,
        document_source=req.document_source,
        reviewer=current_user.email,
        metrics_json=metrics,
        review_time_sec=req.review_time_sec,
        correction_time_sec=req.correction_time_sec,
        approval_time_sec=req.approval_time_sec
    )"""

    new_run = """    run = BenchmarkRun(
        claim_id=req.claim_id,
        organization_id=org_id,
        document_source=req.document_source,
        reviewer=current_user.email,
        ground_truth_json=req.ground_truth,
        metrics_json=metrics,
        review_time_sec=req.review_time_sec,
        correction_time_sec=req.correction_time_sec,
        approval_time_sec=req.approval_time_sec
    )"""
    content = content.replace(old_run, new_run)

    # 4. Dashboard Enhancements
    old_dash = """    # Very basic aggregation for demo purposes
    return {
        "overall_accuracy": round(total_acc / len(runs), 2),
        "runs_count": len(runs),
        "avg_review_time_sec": round(avg_review, 2),
        "avg_correction_time_sec": round(avg_correction, 2),
        "avg_approval_time_sec": round(avg_approval, 2),
        "per_field_accuracy": {"""

    new_dash = """    # Hospital Grouping
    hospital_acc = {}
    for r in runs:
        hosp = r.document_source.split(".")[0] if r.document_source else "Unknown"
        acc = r.metrics_json.get("overall", {}).get("accuracy", 0)
        if hosp not in hospital_acc:
            hospital_acc[hosp] = []
        hospital_acc[hosp].append(acc)
    hospital_summary = {k: round(sum(v)/len(v), 2) for k, v in hospital_acc.items()}
    
    # Error analysis ranking
    field_accuracies = {
        "patient_name": sum(r.metrics_json.get("scalar_fields", {}).get("patient_name", {}).get("accuracy", 0) for r in runs) / len(runs),
        "diagnoses_precision": sum(r.metrics_json.get("list_fields", {}).get("diagnoses", {}).get("precision", 0) for r in runs) / len(runs),
        "diagnoses_recall": sum(r.metrics_json.get("list_fields", {}).get("diagnoses", {}).get("recall", 0) for r in runs) / len(runs),
        "icd_mapping": sum(r.metrics_json.get("list_fields", {}).get("icd_recommendations", {}).get("accuracy", 0) for r in runs) / len(runs)
    }
    sorted_errors = sorted(field_accuracies.items(), key=lambda x: x[1])

    # Time savings (baseline 900 seconds)
    avg_time_savings = 900 - avg_review if avg_review < 900 else 0

    return {
        "overall_accuracy": round(total_acc / len(runs), 2),
        "runs_count": len(runs),
        "avg_review_time_sec": round(avg_review, 2),
        "avg_correction_time_sec": round(avg_correction, 2),
        "avg_approval_time_sec": round(avg_approval, 2),
        "avg_reviewer_time_savings_sec": round(avg_time_savings, 2),
        "hospital_accuracy": hospital_summary,
        "error_analysis_ranking": [{"field": k, "accuracy": round(v, 2)} for k, v in sorted_errors],
        "per_field_accuracy": {"""
    
    content = content.replace(old_dash, new_dash)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_benchmarks()
