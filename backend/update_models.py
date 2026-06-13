import re

def update_models():
    with open("app/models/__init__.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Claim model fix
    old_claim = """    hospital_name = Column(String(255))
    total_amount = Column(Float)
    status = Column(String(50), default="UPLOADED")  # maps to ClaimStatus

    created_at = Column(DateTime, default=datetime.utcnow)"""

    new_claim = """    hospital_name = Column(String(255))
    total_amount = Column(Float)
    status = Column(String(50), default="UPLOADED")  # maps to ClaimStatus

    # Dataset Validation Flag
    is_benchmark = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)"""
    
    if "is_benchmark = Column(Boolean, default=False)" not in content[:2000]: # check if it exists in Claim
        content = content.replace(old_claim, new_claim)
        
    with open("app/models/__init__.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_models()
