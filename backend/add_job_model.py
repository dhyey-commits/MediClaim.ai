import re

def update_models():
    path = "app/models/__init__.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add JobStatus
    job_status_code = """
class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

# ---------------------------------------------------------------------------
"""
    content = content.replace("# ---------------------------------------------------------------------------\n# Claim", job_status_code + "# Claim")

    # Add BackgroundJob model at the very end
    background_job_code = """
# ---------------------------------------------------------------------------
# BackgroundJob
# ---------------------------------------------------------------------------

class BackgroundJob(Base):
    __tablename__ = "background_jobs"

    id = Column(String, primary_key=True) # ARQ job_id
    claim_id = Column(String, ForeignKey("claims.id"), nullable=True)
    job_type = Column(String, nullable=False) # e.g. OCR, EXTRACTION
    status = Column(String, default=JobStatus.QUEUED.value)
    retry_count = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claim = relationship("Claim")
"""
    content += background_job_code

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_models()
