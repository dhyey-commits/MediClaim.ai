from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict
from pydantic import BaseModel
import io
import csv
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from app.database.database import get_db
from app.core.security import get_current_user
from app.models import BenchmarkRun, User, Claim, Document, ClaimStatus, DocumentStatus, AuditLog, BackgroundJob, JobStatus
from app.services.storage import save_file
import uuid
from app.services.evaluation import evaluate_claim

router = APIRouter(tags=["Benchmarks"])

class EvaluateRequest(BaseModel):
    claim_id: str
    document_source: str
    ground_truth: dict
    system_output: dict
    review_time_sec: Optional[float] = None
    correction_time_sec: Optional[float] = None
    approval_time_sec: Optional[float] = None

@router.post("/upload")
async def upload_benchmark(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ingests a real clinical PDF as a benchmark document"""
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

@router.post("/evaluate")
async def evaluate_run(
    req: EvaluateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    metrics = evaluate_claim(req.ground_truth, req.system_output)
    
    # Optional DB link if claim exists
    org_id = current_user.organization_id
    if req.claim_id:
        res = await db.execute(select(Claim).where(Claim.id == req.claim_id))
        claim = res.scalars().first()
        if claim:
            org_id = claim.organization_id

    run = BenchmarkRun(
        claim_id=req.claim_id,
        organization_id=org_id,
        document_source=req.document_source,
        reviewer=current_user.email,
        ground_truth_json=req.ground_truth,
        metrics_json=metrics,
        review_time_sec=req.review_time_sec,
        correction_time_sec=req.correction_time_sec,
        approval_time_sec=req.approval_time_sec
    )
    db.add(run)
    await db.commit()
    return {"id": run.id, "metrics": metrics}

@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(BenchmarkRun).where(BenchmarkRun.organization_id == current_user.organization_id))
    runs = res.scalars().all()
    
    if not runs:
        return {"overall_accuracy": 0.0, "runs_count": 0}

    total_acc = sum(r.metrics_json.get("overall", {}).get("accuracy", 0) for r in runs)
    
    # Timing averages
    avg_review = sum(r.review_time_sec or 0 for r in runs) / len(runs)
    avg_correction = sum(r.correction_time_sec or 0 for r in runs) / len(runs)
    avg_approval = sum(r.approval_time_sec or 0 for r in runs) / len(runs)

    # Hospital Grouping
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
        "per_field_accuracy": {
            "patient_name": round(sum(r.metrics_json.get("scalar_fields", {}).get("patient_name", {}).get("accuracy", 0) for r in runs) / len(runs), 2),
            "diagnoses_precision": round(sum(r.metrics_json.get("list_fields", {}).get("diagnoses", {}).get("precision", 0) for r in runs) / len(runs), 2),
            "diagnoses_recall": round(sum(r.metrics_json.get("list_fields", {}).get("diagnoses", {}).get("recall", 0) for r in runs) / len(runs), 2)
        }
    }

@router.get("/export/csv")
async def export_csv(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(BenchmarkRun).where(BenchmarkRun.organization_id == current_user.organization_id))
    runs = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Claim ID", "Date", "Source", "Reviewer", "Overall Accuracy", "Review Time (s)", "Correction Time (s)", "Approval Time (s)"])
    
    for r in runs:
        writer.writerow([
            r.id, 
            r.claim_id, 
            r.run_date.isoformat(), 
            r.document_source, 
            r.reviewer,
            r.metrics_json.get("overall", {}).get("accuracy", 0),
            r.review_time_sec or 0,
            r.correction_time_sec or 0,
            r.approval_time_sec or 0
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=benchmarks.csv"}
    )

@router.get("/export/pdf")
async def export_pdf(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = await db.execute(select(BenchmarkRun).where(BenchmarkRun.organization_id == current_user.organization_id))
    runs = res.scalars().all()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "MediClaim AI - Benchmark Evaluation Report")
    
    if runs:
        total_acc = sum(r.metrics_json.get("overall", {}).get("accuracy", 0) for r in runs) / len(runs)
        avg_review = sum(r.review_time_sec or 0 for r in runs) / len(runs)
        c.drawString(100, 700, f"Total Runs: {len(runs)}")
        c.drawString(100, 680, f"Overall System Accuracy: {total_acc:.2%}")
        c.drawString(100, 660, f"Avg Review Time: {avg_review:.1f} sec")
    else:
        c.drawString(100, 700, "No benchmark runs found.")

    c.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=benchmarks.pdf"}
    )
