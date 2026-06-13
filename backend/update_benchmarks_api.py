import re
import sys

def update_benchmarks_api():
    path = "app/api/benchmarks.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update EvaluateRequest
    req_old = """class EvaluateRequest(BaseModel):
    claim_id: Optional[str] = None
    document_source: str
    ground_truth: dict
    system_output: dict"""
    
    req_new = """class EvaluateRequest(BaseModel):
    claim_id: str
    document_source: str
    ground_truth: dict
    system_output: dict
    review_time_sec: Optional[float] = None
    correction_time_sec: Optional[float] = None
    approval_time_sec: Optional[float] = None"""

    content = content.replace(req_old, req_new)

    # 2. Update evaluate_run
    run_old = """    run = BenchmarkRun(
        claim_id=req.claim_id,
        organization_id=org_id,
        document_source=req.document_source,
        reviewer=current_user.email,
        metrics_json=metrics
    )"""

    run_new = """    run = BenchmarkRun(
        claim_id=req.claim_id,
        organization_id=org_id,
        document_source=req.document_source,
        reviewer=current_user.email,
        metrics_json=metrics,
        review_time_sec=req.review_time_sec,
        correction_time_sec=req.correction_time_sec,
        approval_time_sec=req.approval_time_sec
    )"""

    content = content.replace(run_old, run_new)

    # 3. Update dashboard
    dashboard_old = """    # Very basic aggregation for demo purposes
    return {
        "overall_accuracy": round(total_acc / len(runs), 2),
        "runs_count": len(runs),
        "per_field_accuracy": {"""

    dashboard_new = """    # Timing averages
    avg_review = sum(r.review_time_sec or 0 for r in runs) / len(runs)
    avg_correction = sum(r.correction_time_sec or 0 for r in runs) / len(runs)
    avg_approval = sum(r.approval_time_sec or 0 for r in runs) / len(runs)

    # Very basic aggregation for demo purposes
    return {
        "overall_accuracy": round(total_acc / len(runs), 2),
        "runs_count": len(runs),
        "avg_review_time_sec": round(avg_review, 2),
        "avg_correction_time_sec": round(avg_correction, 2),
        "avg_approval_time_sec": round(avg_approval, 2),
        "per_field_accuracy": {"""
    
    content = content.replace(dashboard_old, dashboard_new)

    # 4. Update CSV
    csv_old_header = """    writer.writerow(["ID", "Claim ID", "Date", "Source", "Reviewer", "Overall Accuracy"])"""
    csv_new_header = """    writer.writerow(["ID", "Claim ID", "Date", "Source", "Reviewer", "Overall Accuracy", "Review Time (s)", "Correction Time (s)", "Approval Time (s)"])"""
    content = content.replace(csv_old_header, csv_new_header)

    csv_old_row = """        writer.writerow([
            r.id, 
            r.claim_id, 
            r.run_date.isoformat(), 
            r.document_source, 
            r.reviewer,
            r.metrics_json.get("overall", {}).get("accuracy", 0)
        ])"""
    csv_new_row = """        writer.writerow([
            r.id, 
            r.claim_id, 
            r.run_date.isoformat(), 
            r.document_source, 
            r.reviewer,
            r.metrics_json.get("overall", {}).get("accuracy", 0),
            r.review_time_sec or 0,
            r.correction_time_sec or 0,
            r.approval_time_sec or 0
        ])"""
    content = content.replace(csv_old_row, csv_new_row)

    # 5. Update PDF
    pdf_old = """        total_acc = sum(r.metrics_json.get("overall", {}).get("accuracy", 0) for r in runs) / len(runs)
        c.drawString(100, 700, f"Total Runs: {len(runs)}")
        c.drawString(100, 680, f"Overall System Accuracy: {total_acc:.2%}")"""
    
    pdf_new = """        total_acc = sum(r.metrics_json.get("overall", {}).get("accuracy", 0) for r in runs) / len(runs)
        avg_review = sum(r.review_time_sec or 0 for r in runs) / len(runs)
        c.drawString(100, 700, f"Total Runs: {len(runs)}")
        c.drawString(100, 680, f"Overall System Accuracy: {total_acc:.2%}")
        c.drawString(100, 660, f"Avg Review Time: {avg_review:.1f} sec")"""
    content = content.replace(pdf_old, pdf_new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_benchmarks_api()
