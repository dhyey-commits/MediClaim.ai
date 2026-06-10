"use client";

import { useState } from "react";
import { use } from "react";
import Link from "next/link";
import {
  CheckCircle2, Clock, Circle,
  FileText, RefreshCw, Edit2, Check, X, Loader2, AlertTriangle, Plus, Download
} from "lucide-react";
import { useClaim, useOverrideIcd } from "@/hooks/queries";
import { formatDate, formatFileSize, formatConfidence, STATUS_BADGE_CLASS, STATUS_LABELS } from "@/lib/utils";
import { api } from "@/services/api";
import { toast } from "sonner";
import type { DiagnosisOut, ExtractedEntityOut } from "@/services/api";

// ─────────────────────────────────────────────
// Workflow steps
// ─────────────────────────────────────────────
const WORKFLOW_STEPS = [
  { status: "DRAFT", label: "Draft" },
  { status: "DOCUMENT_UPLOADED", label: "Uploaded" },
  { status: "OCR_COMPLETE", label: "OCR Done" },
  { status: "EXTRACTION_COMPLETE", label: "Extracted" },
  { status: "ICD_MAPPED", label: "ICD Mapped" },
  { status: "REPORT_GENERATED", label: "Report Ready" },
];

const STATUS_ORDER = WORKFLOW_STEPS.map((s) => s.status);

function getStepState(stepStatus: string, claimStatus: string) {
  const stepIdx = STATUS_ORDER.indexOf(stepStatus);
  const claimIdx = STATUS_ORDER.indexOf(claimStatus);
  if (stepIdx < claimIdx) return "done";
  if (stepIdx === claimIdx) return "active";
  return "pending";
}

// ─────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────

function ConfidenceBar({ score }: { score: number }) {
  const level = score >= 0.85 ? "high" : score >= 0.65 ? "medium" : "low";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div className="confidence-bar" style={{ width: 60, flex: "none" }}>
        <div
          className={`confidence-fill confidence-${level}`}
          style={{ width: `${Math.round(score * 100)}%` }}
        />
      </div>
      <span style={{ fontSize: 11.5, color: "var(--text-muted)" }}>{formatConfidence(score)}</span>
    </div>
  );
}

function EntityGroup({ title, entities }: { title: string; entities: ExtractedEntityOut[] }) {
  if (entities.length === 0) return null;
  return (
    <div>
      <div style={{ fontSize: 11, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-muted)", marginBottom: 8 }}>
        {title}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {entities.map((e) => (
          <div
            key={e.id}
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "8px 12px",
              borderRadius: 10,
              background: "rgba(255,255,255,0.03)",
              border: "1px solid var(--border)",
            }}
          >
            <span style={{ fontSize: 13, color: "var(--text-primary)" }}>{e.value}</span>
            <ConfidenceBar score={e.confidence} />
          </div>
        ))}
      </div>
    </div>
  );
}

function DiagnosisRow({
  diag,
  claimId,
}: {
  diag: DiagnosisOut;
  claimId: string;
}) {
  const [editing, setEditing] = useState(false);
  const [icdInput, setIcdInput] = useState(diag.icd_code || "");
  const override = useOverrideIcd(claimId);

  const save = async () => {
    if (!icdInput.trim()) return;
    try {
      await override.mutateAsync({ diagnosisId: diag.id, icdCode: icdInput.trim().toUpperCase() });
      toast.success("ICD code updated");
      setEditing(false);
    } catch {
      toast.error("Failed to update ICD code");
    }
  };

  return (
    <tr>
      <td>
        {diag.is_primary && (
          <span
            style={{
              fontSize: 10,
              padding: "2px 6px",
              borderRadius: 6,
              background: "rgba(14,165,233,0.15)",
              color: "var(--brand-400)",
              marginRight: 6,
            }}
          >
            PRIMARY
          </span>
        )}
        {diag.description}
      </td>
      <td>
        {editing ? (
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <input
              className="input"
              value={icdInput}
              onChange={(e) => setIcdInput(e.target.value)}
              style={{ width: 90, padding: "4px 8px", fontSize: 12 }}
              placeholder="E11.9"
              autoFocus
            />
            <button onClick={save} className="btn btn-primary btn-sm" disabled={override.isPending}>
              {override.isPending ? <Loader2 size={12} /> : <Check size={12} />}
            </button>
            <button onClick={() => { setEditing(false); setIcdInput(diag.icd_code || ""); }} className="btn btn-secondary btn-sm">
              <X size={12} />
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <code
              style={{
                fontSize: 12.5,
                color: "var(--brand-400)",
                background: "rgba(14,165,233,0.1)",
                padding: "2px 8px",
                borderRadius: 6,
              }}
            >
              {diag.icd_code || "—"}
            </code>
            {diag.is_manually_overridden && (
              <span style={{ fontSize: 10, color: "var(--warning)" }}>edited</span>
            )}
            <button onClick={() => setEditing(true)} className="btn btn-ghost btn-sm" style={{ padding: "2px 4px", marginLeft: 2 }}>
              <Edit2 size={12} />
            </button>
          </div>
        )}
      </td>
      <td style={{ fontSize: 12.5, color: "var(--text-muted)", maxWidth: 240 }}>
        {diag.icd_description || "—"}
      </td>
      <td>
        <ConfidenceBar score={diag.confidence} />
      </td>
    </tr>
  );
}

// ─────────────────────────────────────────────
// Main Page
// ─────────────────────────────────────────────

export default function ClaimDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: claim, isLoading, refetch } = useClaim(id);

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 900 }}>
        {[...Array(4)].map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 120 }} />
        ))}
      </div>
    );
  }

  if (!claim) {
    return (
      <div style={{ textAlign: "center", padding: 60 }}>
        <AlertTriangle size={40} style={{ color: "var(--danger)", margin: "0 auto 12px" }} />
        <p style={{ color: "var(--text-muted)" }}>Claim not found</p>
        <Link href="/claims" className="btn btn-secondary btn-sm" style={{ marginTop: 12, display: "inline-flex" }}>
          Back to claims
        </Link>
      </div>
    );
  }

  // Group extracted entities (optional — Week 2+ feature)
  const extractedEntities = claim.extracted_entities || [];
  const byType: Record<string, ExtractedEntityOut[]> = {};
  extractedEntities.forEach((e) => {
    (byType[e.entity_type] = byType[e.entity_type] || []).push(e);
  });
  const diagnoses = claim.diagnoses || [];
  const report = claim.report || null;



  return (
    <div className="animate-fade-in" style={{ maxWidth: 960 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <h1 className="page-title" style={{ fontSize: 20 }}>{claim.claim_number}</h1>
            <span className={STATUS_BADGE_CLASS[claim.status] || "badge badge-draft"}>
              {STATUS_LABELS[claim.status] || claim.status}
            </span>
          </div>
          <p className="page-subtitle">
            {claim.patient_name || "Patient name pending extraction"} • Created {formatDate(claim.created_at)}
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button onClick={() => refetch()} className="btn btn-secondary btn-sm">
            <RefreshCw size={14} />
          </button>
          <Link href="/claims" className="btn btn-secondary btn-sm">Back</Link>
        </div>
      </div>

      {/* Workflow timeline */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Workflow Progress</div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
          {WORKFLOW_STEPS.map((step, i) => {
            const state = getStepState(step.status, claim.status);
            return (
              <div key={step.status} style={{ display: "flex", alignItems: "center", flex: i < WORKFLOW_STEPS.length - 1 ? 1 : 0 }}>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
                  <div
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: state === "done" ? "var(--success)" : state === "active" ? "var(--brand-500)" : "var(--surface-2)",
                      border: `2px solid ${state === "done" ? "var(--success)" : state === "active" ? "var(--brand-500)" : "var(--border)"}`,
                      transition: "all 0.3s",
                    }}
                  >
                    {state === "done" ? (
                      <CheckCircle2 size={14} color="white" />
                    ) : state === "active" ? (
                      <Clock size={14} color="white" />
                    ) : (
                      <Circle size={12} style={{ color: "var(--text-muted)" }} />
                    )}
                  </div>
                  <span style={{ fontSize: 10.5, color: state === "active" ? "var(--brand-400)" : state === "done" ? "var(--success)" : "var(--text-muted)", whiteSpace: "nowrap" }}>
                    {step.label}
                  </span>
                </div>
                {i < WORKFLOW_STEPS.length - 1 && (
                  <div
                    style={{
                      flex: 1,
                      height: 2,
                      background: getStepState(WORKFLOW_STEPS[i + 1].status, claim.status) !== "pending" ? "var(--success)" : "var(--border)",
                      margin: "0 4px",
                      marginBottom: 18,
                      transition: "background 0.3s",
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Status info */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Workflow Status</div>
          <div className="card-desc">Current status: {claim.status === "DOCUMENT_UPLOADED" ? "Documents uploaded — ready for processing" : claim.status === "DRAFT" ? "Draft — upload documents to proceed" : claim.status}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
        {/* Patient Info */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Patient Information</div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              ["Name", claim.patient_name],
              ["Age", claim.patient_age ? `${claim.patient_age} years` : null],
              ["Gender", claim.patient_gender],
              ["UHID", claim.patient_uhid],
              ["Admission", formatDate(claim.admission_date)],
              ["Discharge", formatDate(claim.discharge_date)],
              ["Chief Complaint", claim.chief_complaint],
            ].map(([label, value]) => (
              <div key={label as string} style={{ display: "flex", gap: 12, fontSize: 13 }}>
                <span style={{ color: "var(--text-muted)", minWidth: 110, flexShrink: 0 }}>{label as string}</span>
                <span style={{ color: value ? "var(--text-primary)" : "var(--text-muted)" }}>
                  {(value as string) || "Pending extraction"}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Documents */}
        <div className="card">
          <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div className="card-title">Documents</div>
              <div className="card-desc">{claim.documents.length} file(s) uploaded</div>
            </div>
            <Link href="/claims/new" className="btn btn-secondary btn-sm">
              <Plus size={13} /> Add
            </Link>
          </div>
          {claim.documents.length === 0 ? (
            <p style={{ color: "var(--text-muted)", fontSize: 13 }}>No documents uploaded.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {claim.documents.map((doc) => (
                <div
                  key={doc.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "10px 12px",
                    borderRadius: 10,
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <FileText size={16} style={{ color: "#f59e0b", flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 12.5, color: "var(--text-primary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {doc.file_name}
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>
                      {formatFileSize(doc.file_size)} • {doc.status}
                      {doc.confidence_score > 0 && ` • ${formatConfidence(doc.confidence_score)} confidence`}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Extracted Entities */}
      {extractedEntities.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-header">
            <div className="card-title">Extracted Clinical Data</div>
            <div className="card-desc">AI-extracted entities from the discharge summary</div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <EntityGroup title="Diagnoses" entities={byType.diagnosis || []} />
            <EntityGroup title="Medications" entities={byType.medication || []} />
            <EntityGroup title="Procedures" entities={byType.procedure || []} />
            <EntityGroup title="Investigations" entities={byType.investigation || []} />
          </div>
        </div>
      )}

      {/* ICD Mapping */}
      {diagnoses.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-header">
            <div className="card-title">ICD-10 Mapping</div>
            <div className="card-desc">Click the edit icon to manually override any code</div>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Diagnosis</th>
                <th>ICD-10 Code</th>
                <th>Description</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {diagnoses.map((diag) => (
                <DiagnosisRow key={diag.id} diag={diag} claimId={id} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Report preview */}
      {report?.is_generated && (
        <div className="card">
          <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div className="card-title">ISCS Report</div>
              <div className="card-desc">Indian Standard Clinical Summary — ready for download</div>
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <Link href={`/reports/${report!.id}`} className="btn btn-secondary btn-sm">
                View Report
              </Link>
              <a href={api.reports.downloadUrl(report!.id)} download className="btn btn-primary btn-sm">
                <Download size={13} /> Download PDF
              </a>
            </div>
          </div>
          <div
            style={{
              padding: 16,
              borderRadius: 12,
              background: "rgba(16,185,129,0.06)",
              border: "1px solid rgba(16,185,129,0.2)",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <CheckCircle2 size={20} style={{ color: "var(--success)", flexShrink: 0 }} />
            <div>
              <p style={{ fontSize: 13.5, fontWeight: 600, color: "var(--text-primary)" }}>
                Report generated successfully
              </p>
              <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
                Generated on {formatDate(report!.created_at)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
