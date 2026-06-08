from app.schemas.claims import (
    AnalyticsOverview,
    ApiKeyRecord,
    ClaimPacket,
    ClaimRecord,
    ClaimStatus,
    ClinicalExtraction,
    CodeSuggestion,
    FraudAnalysis,
    FraudSignal,
    ISCSReport,
    ISCSSection,
    InsurerRule,
    NotificationEvent,
    OCRProgressResponse,
    OCRStage,
    OCRStageProgress,
    OperationsOverview,
    RolePermission,
    UploadBatchRequest,
    UploadBatchResponse,
    ValidationResult,
    WebhookRecord,
)


def get_demo_claims() -> list[ClaimRecord]:
    return [
        ClaimRecord(
            id="CLM-24081",
            hospital_name="Apex Care Hospital",
            insurer="Star Health",
            patient_name="Rahul Mehta",
            status=ClaimStatus.ready,
            amount_inr=84500,
            created_at="2026-06-04T09:10:00Z",
            diagnosis=["Viral fever", "Dehydration"],
            documents=["Discharge summary", "CBC report", "Doctor signature"],
        ),
        ClaimRecord(
            id="CLM-24082",
            hospital_name="Narayana Multispecialty",
            insurer="HDFC Ergo",
            patient_name="Ananya Rao",
            status=ClaimStatus.under_review,
            amount_inr=124000,
            created_at="2026-06-04T11:45:00Z",
            diagnosis=["Appendicitis"],
            documents=["Surgery note", "Lab report", "Consent form"],
        ),
    ]


def get_demo_extraction() -> ClinicalExtraction:
    return ClinicalExtraction(
        patient_name="Rahul Mehta",
        patient_age=42,
        patient_gender="Male",
        symptoms=["Fever", "Weakness", "Reduced appetite"],
        diagnosis=["Viral fever", "Mild dehydration"],
        procedures=["IV fluid therapy"],
        investigations=["CBC", "Platelet count", "Chest X-ray"],
        medications=["Paracetamol", "ORS", "Antiemetic"],
        admission_details="Admitted through emergency intake on 03 Jun 2026.",
        discharge_details="Discharged after 2 days with stable vitals and improved hydration.",
        confidence_scores={
            "patient_details": 0.98,
            "diagnosis": 0.94,
            "procedures": 0.91,
            "medications": 0.96,
        },
    )


def get_demo_coding() -> list[CodeSuggestion]:
    return [
        CodeSuggestion(system="ICD-10", code="A09", label="Infectious gastroenteritis and colitis, unspecified", confidence=0.89),
        CodeSuggestion(system="SNOMED CT", code="186747009", label="Viral fever", confidence=0.87),
        CodeSuggestion(system="CPT", code="96360", label="Intravenous infusion, hydration", confidence=0.91),
        CodeSuggestion(system="RxNorm", code="198440", label="Paracetamol", confidence=0.96),
    ]


def get_analytics_overview() -> AnalyticsOverview:
    return AnalyticsOverview(
        total_claims=12480,
        approval_rate=0.916,
        average_processing_time_minutes=14.5,
        claim_value_inr=128500000,
        hospital_performance=[
            {"hospital": "Apex Care Hospital", "approval_rate": 0.94},
            {"hospital": "Narayana Multispecialty", "approval_rate": 0.89},
            {"hospital": "City Medical Center", "approval_rate": 0.92},
        ],
        fraud_alerts=27,
    )


def create_upload_batch(payload: UploadBatchRequest) -> UploadBatchResponse:
    return UploadBatchResponse(
        batch_id=f"UP-{payload.claim_id}",
        accepted=len(payload.files),
        files=payload.files,
    )


def get_ocr_progress(claim_id: str) -> OCRProgressResponse:
    stages = [
        OCRStageProgress(stage=OCRStage.extraction, progress=100, state="completed"),
        OCRStageProgress(stage=OCRStage.entities, progress=100, state="completed"),
        OCRStageProgress(stage=OCRStage.diagnosis, progress=100, state="completed"),
        OCRStageProgress(stage=OCRStage.procedures, progress=84, state="in_progress"),
        OCRStageProgress(stage=OCRStage.icd, progress=56, state="queued"),
        OCRStageProgress(stage=OCRStage.validation, progress=22, state="queued"),
        OCRStageProgress(stage=OCRStage.report, progress=0, state="queued"),
    ]
    return OCRProgressResponse(claim_id=claim_id, stages=stages, current_stage=OCRStage.procedures)


def get_fraud_analysis(claim_id: str) -> FraudAnalysis:
    anomalies = [
        FraudSignal(
            title="Length-of-stay deviation",
            severity="high",
            score=82,
            detail="Observed stay is significantly above diagnosis cluster baseline.",
        ),
        FraudSignal(
            title="Duplicate lab trend",
            severity="medium",
            score=68,
            detail="Repeated investigations without corresponding treatment deltas.",
        ),
    ]
    return FraudAnalysis(
        claim_id=claim_id,
        risk_score=74,
        anomalies=anomalies,
        missing_evidence=["Consultant signature", "Final nursing note"],
        suspicious_patterns=["Billing outlier for consumables", "Procedure-to-diagnosis mismatch"],
    )


def get_insurer_rules() -> list[InsurerRule]:
    return [
        InsurerRule(insurer="Star Health", supports_cashless=True, required_documents=["Discharge summary", "Diagnostic report", "Final bill"]),
        InsurerRule(insurer="Niva Bupa", supports_cashless=True, required_documents=["Discharge summary", "Consultant notes", "KYC proof"]),
        InsurerRule(insurer="ICICI Lombard", supports_cashless=True, required_documents=["Admission notes", "Procedure notes", "Final bill"]),
        InsurerRule(insurer="HDFC Ergo", supports_cashless=True, required_documents=["Discharge summary", "Lab evidence", "Policy mapping"]),
        InsurerRule(insurer="Care Health", supports_cashless=True, required_documents=["Diagnosis note", "Procedure note", "Bill breakdown"]),
        InsurerRule(insurer="Government Schemes", supports_cashless=False, required_documents=["ISCS report", "Government form", "Hospital attestation"]),
    ]


def get_claim_packets() -> list[ClaimPacket]:
    return [
        ClaimPacket(packet_id="PKT-1408", claim_id="CLM-24081", insurer="Star Health", status=ClaimStatus.ready, amount_inr=84500),
        ClaimPacket(packet_id="PKT-1409", claim_id="CLM-24082", insurer="Niva Bupa", status=ClaimStatus.submitted, amount_inr=112000),
        ClaimPacket(packet_id="PKT-1410", claim_id="CLM-24083", insurer="HDFC Ergo", status=ClaimStatus.under_review, amount_inr=124000),
    ]


def get_role_permissions() -> list[RolePermission]:
    return [
        RolePermission(role="Hospital Admin", permissions=["upload:documents", "manage:organization", "view:analytics"]),
        RolePermission(role="Doctor", permissions=["review:clinical-extraction", "edit:clinical-notes"]),
        RolePermission(role="Medical Coder", permissions=["review:coding", "override:coding"]),
        RolePermission(role="Insurance Reviewer", permissions=["review:claims", "add:insurer-notes"]),
        RolePermission(role="TPA Executive", permissions=["submit:claim-packets", "manage:webhooks"]),
        RolePermission(role="Super Admin", permissions=["admin:all"]),
    ]


def get_operations_overview() -> OperationsOverview:
    notifications = [
        NotificationEvent(id="N-101", kind="claim", message="Claim CLM-24082 moved to Under Review", created_at="2026-06-05T09:10:00Z"),
        NotificationEvent(id="N-102", kind="fraud", message="High risk anomaly detected in CLM-24083", created_at="2026-06-05T09:24:00Z"),
    ]
    api_keys = [
        ApiKeyRecord(key_id="AK-prod-01", name="TPA Integration", last_used_at="2026-06-05T08:50:00Z", scopes=["claims:read", "claims:write"]),
        ApiKeyRecord(key_id="AK-prod-02", name="Hospital ERP", last_used_at="2026-06-05T08:11:00Z", scopes=["reports:read"]),
    ]
    webhooks = [
        WebhookRecord(id="WH-901", target_url="https://partner.example.com/claims", event="claim.status.updated", active=True),
        WebhookRecord(id="WH-902", target_url="https://partner.example.com/fraud", event="fraud.detected", active=True),
    ]
    audit_events = [
        {"actor": "Super Admin", "action": "Updated insurer policy mapping", "time": "2026-06-05T08:00:00Z"},
        {"actor": "Medical Coder", "action": "Manual ICD override accepted", "time": "2026-06-05T08:22:00Z"},
    ]
    return OperationsOverview(notifications=notifications, api_keys=api_keys, webhooks=webhooks, audit_events=audit_events)


def get_demo_iscs(
    claim: ClaimRecord,
    extraction: ClinicalExtraction | None = None,
    coding: list[CodeSuggestion] | None = None,
    validation: ValidationResult | None = None,
) -> ISCSReport:
    extraction = extraction or get_demo_extraction()
    coding = coding or get_demo_coding()
    validation = validation or ValidationResult(
        claim_readiness_score=92,
        issues=[],
        compliance_flags=["Signature verified", "Supporting evidence complete"],
    )

    return ISCSReport(
        claim_id=claim.id,
        title="Indian Standard Clinical Summary",
        sections=[
            ISCSSection(title="Patient Information", content=[f"{extraction.patient_name}, {extraction.patient_age}, {extraction.patient_gender}"]),
            ISCSSection(title="Clinical Timeline", content=[extraction.admission_details, extraction.discharge_details]),
            ISCSSection(title="Diagnosis", content=extraction.diagnosis),
            ISCSSection(title="Investigations", content=extraction.investigations),
            ISCSSection(title="Procedures", content=extraction.procedures),
            ISCSSection(title="Medication Summary", content=extraction.medications),
            ISCSSection(title="ICD Mapping", content=[f"{item.system}: {item.code} - {item.label}" for item in coding]),
            ISCSSection(title="Insurance Notes", content=[f"Readiness score: {validation.claim_readiness_score}"] + validation.compliance_flags),
        ],
        export_formats=["PDF", "Word", "Share Link"],
        share_link=f"https://demo.mediclaim.ai/iscs/{claim.id}",
    )
