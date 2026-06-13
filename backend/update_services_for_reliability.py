import re

def update_extraction_service():
    path = "app/services/extraction_service.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("async def run_extraction_for_claim(claim_id: str, db: AsyncSession):", "async def run_extraction_for_claim(claim_id: str, user_id: str, db: AsyncSession):")
    
    # Update AuditLog creation
    content = content.replace(
        "db.add(AuditLog(\n            claim_id=claim_id,\n            action=",
        "db.add(AuditLog(\n            user_id=user_id,\n            claim_id=claim_id,\n            action="
    )
    content = content.replace(
        "db.add(AuditLog(\n        claim_id=claim_id,\n        action=",
        "db.add(AuditLog(\n        user_id=user_id,\n        claim_id=claim_id,\n        action="
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def update_ocr_service():
    path = "app/services/ocr_service.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("async def run_ocr_for_claim(claim_id: str, db: AsyncSession):", "async def run_ocr_for_claim(claim_id: str, user_id: str, db: AsyncSession):")

    # Update AuditLog creation
    content = content.replace(
        "db.add(AuditLog(\n            claim_id=claim_id,\n            action=",
        "db.add(AuditLog(\n            user_id=user_id,\n            claim_id=claim_id,\n            action="
    )
    content = content.replace(
        "db.add(AuditLog(\n        claim_id=claim_id,\n        action=",
        "db.add(AuditLog(\n        user_id=user_id,\n        claim_id=claim_id,\n        action="
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_extraction_service()
    update_ocr_service()
