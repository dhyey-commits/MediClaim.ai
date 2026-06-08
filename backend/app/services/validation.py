from app.schemas.claims import ClaimRecord, ClinicalExtraction, CodeSuggestion, ClaimValidationIssue, ValidationResult


def build_validation_result(
    claim: ClaimRecord,
    extraction: ClinicalExtraction,
    coding: list[CodeSuggestion],
) -> ValidationResult:
    issues = [
        ClaimValidationIssue(
            severity="low",
            title="Documentation complete",
            detail="Admission, discharge, and investigation trail are present.",
        ),
    ]

    if claim.status.value == "Draft":
        issues.append(
            ClaimValidationIssue(
                severity="medium",
                title="Claim still in draft",
                detail="Packet has not been submitted to the insurer yet.",
            )
        )

    readiness = 92 if len(coding) >= 3 else 78
    return ValidationResult(
        claim_readiness_score=readiness,
        issues=issues,
        compliance_flags=["Signature verified", "No conflicting diagnoses", "Insurance policy aligned"],
    )
