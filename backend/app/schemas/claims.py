from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ClaimStatus(str, Enum):
    draft = "Draft"
    ready = "Ready"
    submitted = "Submitted"
    under_review = "Under Review"
    approved = "Approved"
    rejected = "Rejected"


class OCRStage(str, Enum):
    extraction = "OCR Extraction"
    entities = "Medical Entity Detection"
    diagnosis = "Diagnosis Extraction"
    procedures = "Procedure Extraction"
    icd = "ICD Mapping"
    validation = "Validation"
    report = "Report Generation"


class CodeSuggestion(BaseModel):
    system: str
    code: str
    label: str
    confidence: float = Field(ge=0, le=1)
    source: str = "AI"


class ClinicalExtraction(BaseModel):
    patient_name: str
    patient_age: int
    patient_gender: str
    symptoms: list[str]
    diagnosis: list[str]
    procedures: list[str]
    investigations: list[str]
    medications: list[str]
    admission_details: str
    discharge_details: str
    confidence_scores: dict[str, float]


class ClaimValidationIssue(BaseModel):
    severity: str
    title: str
    detail: str


class ValidationResult(BaseModel):
    claim_readiness_score: int
    issues: list[ClaimValidationIssue]
    compliance_flags: list[str]


class ISCSSection(BaseModel):
    title: str
    content: list[str]


class ISCSReport(BaseModel):
    claim_id: str
    title: str
    sections: list[ISCSSection]
    export_formats: list[str]
    share_link: str


class ClaimRecord(BaseModel):
    id: str
    hospital_name: str
    insurer: str
    patient_name: str
    status: ClaimStatus
    amount_inr: float
    created_at: str
    diagnosis: list[str]
    documents: list[str]


class ClaimSummary(BaseModel):
    id: str
    hospital_name: str
    insurer: str
    status: ClaimStatus
    amount_inr: float
    readiness_score: int


class UploadFileItem(BaseModel):
    file_name: str
    file_type: str
    progress: int = Field(ge=0, le=100)
    ocr_status: str


class UploadBatchRequest(BaseModel):
    organization_id: str
    claim_id: str
    files: list[UploadFileItem]


class UploadBatchResponse(BaseModel):
    batch_id: str
    accepted: int
    files: list[UploadFileItem]


class OCRStageProgress(BaseModel):
    stage: OCRStage
    progress: int = Field(ge=0, le=100)
    state: str


class OCRProgressResponse(BaseModel):
    claim_id: str
    stages: list[OCRStageProgress]
    current_stage: OCRStage


class FraudSignal(BaseModel):
    title: str
    severity: str
    score: int = Field(ge=0, le=100)
    detail: str


class FraudAnalysis(BaseModel):
    claim_id: str
    risk_score: int = Field(ge=0, le=100)
    anomalies: list[FraudSignal]
    missing_evidence: list[str]
    suspicious_patterns: list[str]


class InsurerRule(BaseModel):
    insurer: str
    supports_cashless: bool
    required_documents: list[str]


class ClaimPacket(BaseModel):
    packet_id: str
    claim_id: str
    insurer: str
    status: ClaimStatus
    amount_inr: float


class RolePermission(BaseModel):
    role: str
    permissions: list[str]


class NotificationEvent(BaseModel):
    id: str
    kind: str
    message: str
    created_at: str


class ApiKeyRecord(BaseModel):
    key_id: str
    name: str
    last_used_at: str
    scopes: list[str]


class WebhookRecord(BaseModel):
    id: str
    target_url: str
    event: str
    active: bool


class OperationsOverview(BaseModel):
    notifications: list[NotificationEvent]
    api_keys: list[ApiKeyRecord]
    webhooks: list[WebhookRecord]
    audit_events: list[dict[str, Any]]


class ClaimResponse(BaseModel):
    claim: ClaimRecord
    extraction: ClinicalExtraction
    coding: list[CodeSuggestion]
    validation: ValidationResult
    iscs: ISCSReport
    claim_status: ClaimStatus


class CopilotRequest(BaseModel):
    message: str
    context: dict[str, Any] | None = None


class CopilotResponse(BaseModel):
    message: str
    suggested_actions: list[str]
    confidence: float


class AnalyticsOverview(BaseModel):
    total_claims: int
    approval_rate: float
    average_processing_time_minutes: float
    claim_value_inr: float
    hospital_performance: list[dict[str, Any]]
    fraud_alerts: int
