"""
MediClaim AI — SQLAlchemy ORM Models
Full production schema for the MVP: Users, Organizations, Claims,
Documents, ExtractedEntities, Diagnoses, ICDCodes, ICDMappings, Reports, AuditLogs
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ClaimStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    OCR_PROCESSING = "OCR_PROCESSING"
    OCR_FAILED = "OCR_FAILED"
    OCR_COMPLETE = "OCR_COMPLETE"
    EXTRACTION_PROCESSING = "EXTRACTION_PROCESSING"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    EXTRACTION_COMPLETE = "EXTRACTION_COMPLETE"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    ICD_MAPPED = "ICD_MAPPED"
    REPORT_GENERATED = "REPORT_GENERATED"


class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    OCR_PROCESSING = "OCR_PROCESSING"
    OCR_COMPLETE = "OCR_COMPLETE"
    FAILED = "FAILED"

class RecommendationStatus(str, enum.Enum):
    SUGGESTED = "SUGGESTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    hospital_type = Column(String(50))  # Government / Private / Clinic
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    claims = relationship("Claim", back_populates="organization")


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    clerk_id = Column(String(255), unique=True, index=True)  # Clerk external ID
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="medical_coder")
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    claims = relationship("Claim", back_populates="created_by")
    audit_logs = relationship("AuditLog", back_populates="user")



class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

# ---------------------------------------------------------------------------
# Claim  (core entity — everything revolves around this)
# ---------------------------------------------------------------------------

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, default=_uuid)
    claim_number = Column(String(50), unique=True, nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    created_by_id = Column(String, ForeignKey("users.id"), nullable=True)

    # Patient info (filled in from extraction)
    patient_name = Column(String(255))
    patient_age = Column(Integer)
    patient_gender = Column(String(20))
    patient_uhid = Column(String(100))

    # Admission info
    admission_date = Column(Date)
    discharge_date = Column(Date)
    chief_complaint = Column(Text)
    notes = Column(Text)

    # Workflow status
    status = Column(String(50), default=ClaimStatus.DRAFT.value)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="claims")
    created_by = relationship("User", back_populates="claims")
    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="claim", cascade="all, delete-orphan")
    icd_recommendations = relationship("ClaimICDRecommendation", back_populates="claim")
    extracted_entities = relationship("ExtractedEntity", back_populates="claim", cascade="all, delete-orphan")
    extraction_result = relationship("ExtractionResult", back_populates="claim", uselist=False, cascade="all, delete-orphan")
    report = relationship("Report", back_populates="claim", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="claim")


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50))          # application/pdf, image/jpeg, etc.
    file_path = Column(String(500))         # local path or S3 key
    file_size = Column(Integer)             # bytes
    status = Column(String(50), default=DocumentStatus.PENDING.value)
    extracted_text = Column(Text)           # raw OCR output
    confidence_score = Column(Float, default=0.0)
    page_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claim = relationship("Claim", back_populates="documents")


# ---------------------------------------------------------------------------
# OCRResult
# ---------------------------------------------------------------------------

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(String, primary_key=True, default=_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, default=1)
    raw_text = Column(Text, nullable=False)
    status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim")
    document = relationship("Document")
# ---------------------------------------------------------------------------
# ExtractedEntity  (structured clinical data from NLP)
# ---------------------------------------------------------------------------

class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(String, primary_key=True, default=_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    entity_type = Column(String(100), nullable=False)   # diagnosis, medication, procedure, investigation
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    source_document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="extracted_entities")


# ---------------------------------------------------------------------------
# ExtractionResult  (JSON-based structured extraction from OpenAI)
# ---------------------------------------------------------------------------

class ExtractionResult(Base):
    __tablename__ = "extraction_results"

    id = Column(String, primary_key=True, default=_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False, unique=True)
    ocr_result_id = Column(String, ForeignKey("ocr_results.id"), nullable=True)

    patient_name = Column(String(255))
    age = Column(String(50))
    gender = Column(String(50))
    admission_date = Column(String(50))
    discharge_date = Column(String(50))
    chief_complaint = Column(Text)

    diagnosis_json = Column(JSON)
    procedures_json = Column(JSON)
    medications_json = Column(JSON)
    investigations_json = Column(JSON)

    confidence_score = Column(Float, default=0.0)
    is_approved = Column(Boolean, default=False)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claim = relationship("Claim", back_populates="extraction_result")
    ocr_result = relationship("OCRResult")


# ---------------------------------------------------------------------------
# ICD Code  (reference table — seeded on startup)
# ---------------------------------------------------------------------------

class ICDCode(Base):
    __tablename__ = "icd_codes"

    id = Column(String, primary_key=True, default=_uuid)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    category = Column(String(100))
    chapter = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    diagnoses = relationship("Diagnosis", back_populates="icd_code")


# ---------------------------------------------------------------------------
# Diagnosis  (links claim → ICD code)
# ---------------------------------------------------------------------------

class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(String, primary_key=True, default=_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    description = Column(Text, nullable=False)          # free-text diagnosis
    icd_code_id = Column(String, ForeignKey("icd_codes.id"), nullable=True)
    icd_code_override = Column(String(20))              # manual override
    confidence = Column(Float, default=0.0)
    is_primary = Column(Boolean, default=False)
    is_manually_overridden = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claim = relationship("Claim", back_populates="diagnoses")
    icd_code = relationship("ICDCode", back_populates="diagnoses")



class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

# ---------------------------------------------------------------------------
# Claim ICD Recommendation  (Suggested codes for a given text)
# ---------------------------------------------------------------------------

class ClaimICDRecommendation(Base):
    __tablename__ = "claim_icd_recommendations"

    id = Column(String, primary_key=True, default=_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False, index=True)
    diagnosis_text = Column(Text, nullable=False)
    icd_code = Column(String(20), nullable=False)
    confidence = Column(Float, default=0.0)
    source = Column(String(100), default="FTS5_SEARCH")
    status = Column(String(50), default=RecommendationStatus.SUGGESTED.value)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claim = relationship("Claim", back_populates="icd_recommendations")

# ---------------------------------------------------------------------------
# Report  (generated ISCS report)
# ---------------------------------------------------------------------------

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=_uuid)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False, unique=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    version = Column(Integer, default=1)
    generated_at = Column(DateTime, default=datetime.utcnow)

    claim = relationship("Claim", back_populates="report")


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=True)
    action = Column(String(200), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(String)
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
    claim = relationship("Claim", back_populates="audit_logs")

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
