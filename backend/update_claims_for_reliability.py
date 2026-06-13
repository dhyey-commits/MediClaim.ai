import re
import sys

def main():
    path = "app/api/claims.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update AuditLogs to include user_id
    content = content.replace("db.add(AuditLog(\n        claim_id=", "db.add(AuditLog(\n        user_id=current_user.id,\n        claim_id=")
    content = content.replace("db.add(AuditLog(\n            claim_id=", "db.add(AuditLog(\n            user_id=current_user.id,\n            claim_id=")

    # 2. Add OCR Page Limit Validation in trigger_ocr
    ocr_limit_logic = """
    from app.models import Document
    import pypdf
    docs_result = await db.execute(select(Document).where(Document.claim_id == claim_id))
    docs = docs_result.scalars().all()
    total_pages = 0
    for doc in docs:
        if doc.file_path and doc.file_path.endswith(".pdf"):
            try:
                reader = pypdf.PdfReader(doc.file_path)
                total_pages += len(reader.pages)
            except Exception:
                pass
    if total_pages > 50:
        db.add(AuditLog(
            user_id=current_user.id,
            claim_id=claim_id,
            action="OCR_REJECTED_PAGE_LIMIT",
            entity_type="Claim",
            entity_id=claim_id
        ))
        await db.commit()
        raise HTTPException(status_code=413, detail="PDF exceeds 50 page limit")

    claim.status = ClaimStatus.OCR_PROCESSING.value
    await db.commit()
"""
    # Replace the simple status update in trigger_ocr
    content = content.replace(
        "    claim.status = ClaimStatus.OCR_PROCESSING.value\n    await db.commit()",
        ocr_limit_logic
    )

    # 3. Extraction Locking
    # In trigger_extraction:
    # Instead of `claim.status = ClaimStatus.EXTRACTION_PROCESSING.value; await db.commit()`
    # We do an atomic update.
    extraction_locking = """
    from sqlalchemy import update
    upd = update(Claim).where(
        Claim.id == claim_id,
        Claim.organization_id == current_user.organization_id,
        Claim.status != ClaimStatus.EXTRACTION_PROCESSING.value
    ).values(status=ClaimStatus.EXTRACTION_PROCESSING.value)
    
    upd_res = await db.execute(upd)
    if upd_res.rowcount == 0:
        raise HTTPException(status_code=409, detail="Extraction already running")
    await db.commit()
"""
    # We will replace these 3 lines:
    content = content.replace(
        "    if claim.status == ClaimStatus.EXTRACTION_PROCESSING.value:\n        raise HTTPException(status_code=409, detail=\"Extraction already running\")",
        ""
    )
    content = content.replace(
        "    claim.status = ClaimStatus.EXTRACTION_PROCESSING.value\n    await db.commit()",
        extraction_locking
    )

    # 4. Report Generation Locking
    report_gen = """
    # 3. Save to disk
    uploads_dir = os.path.join(os.getcwd(), "uploads", "reports")
    os.makedirs(uploads_dir, exist_ok=True)
    file_name = f"ISCS_{claim.claim_number}.pdf"
    file_path = os.path.join(uploads_dir, file_name)

    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    # 4. Save to DB
    new_report = Report(
        claim_id=claim_id,
        file_name=file_name,
        file_path=file_path,
        version=1
    )
    db.add(new_report)
    
    from sqlalchemy.exc import IntegrityError
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # Duplicate concurrent request occurred.
        # Clean up orphaned file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Fetch the one that succeeded
        rep_res = await db.execute(select(Report).where(Report.claim_id == claim_id))
        report = rep_res.scalars().first()
        return {
            "claim_id": claim_id,
            "report_id": report.id,
            "status": claim.status,
            "message": "Report already generated (concurrent call handled)"
        }
"""
    # We'll use regex to replace the save logic
    pattern = re.compile(r'    # 3\. Save to disk.*?await db\.commit\(\)', re.DOTALL)
    content = pattern.sub(report_gen, content)

    # Make sure run_extraction_for_claim is called with current_user.id
    content = content.replace("await run_extraction_for_claim(cid, session)", "await run_extraction_for_claim(cid, current_user.id, session)")
    content = content.replace("await run_ocr_for_claim(cid, session)", "await run_ocr_for_claim(cid, current_user.id, session)")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
