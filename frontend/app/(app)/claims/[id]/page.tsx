"use client";

import { useState, useEffect } from "react";
import { use } from "react";
import Link from "next/link";
import {
  CheckCircle2, Clock, Circle,
  FileText, RefreshCw, Edit2, Check, X, Loader2, AlertTriangle, Plus, Download, ScanText, Copy, BrainCircuit
} from "lucide-react";
import { useClaim, useOverrideIcd, useTriggerOcr, useOcrResults, useTriggerExtraction, useExtractionResult, useStartReview, useUpdateReview, useApproveClaim, useClaimAudit, useSuggestIcd, useIcdRecommendations, useAcceptIcd, useRejectIcd } from "@/hooks/queries";
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
  { status: "UNDER_REVIEW", label: "Reviewing" },
  { status: "APPROVED", label: "Approved" },
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

function ReviewPanel({ claimId, extraction, status }: { claimId: string; extraction: any; status: string }) {
  const startReview = useStartReview(claimId);
  const updateReview = useUpdateReview(claimId);
  const approveClaim = useApproveClaim(claimId);

  const [data, setData] = useState({
    patient_name: extraction.patient_name || "",
    age: extraction.age || "",
    gender: extraction.gender || "",
    admission_date: extraction.admission_date || "",
    discharge_date: extraction.discharge_date || "",
    chief_complaint: extraction.chief_complaint || "",
    diagnosis_json: JSON.stringify(extraction.diagnosis_json || [], null, 2),
    procedures_json: JSON.stringify(extraction.procedures_json || [], null, 2),
    medications_json: JSON.stringify(extraction.medications_json || [], null, 2),
    investigations_json: JSON.stringify(extraction.investigations_json || [], null, 2),
  });

  const handleStartReview = async () => {
    try {
      await startReview.mutateAsync();
      toast.success("Review started");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Failed to start review");
    }
  };

  const handleSave = async () => {
    try {
      await updateReview.mutateAsync({
        patient_name: data.patient_name,
        age: data.age,
        gender: data.gender,
        admission_date: data.admission_date,
        discharge_date: data.discharge_date,
        chief_complaint: data.chief_complaint,
        diagnosis_json: JSON.parse(data.diagnosis_json),
        procedures_json: JSON.parse(data.procedures_json),
        medications_json: JSON.parse(data.medications_json),
        investigations_json: JSON.parse(data.investigations_json),
      });
      toast.success("Changes saved");
    } catch (e) {
      toast.error("Failed to save (check JSON formatting)");
    }
  };

  const handleApprove = async () => {
    try {
      await approveClaim.mutateAsync();
      toast.success("Claim approved!");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Failed to approve claim");
    }
  };

  const isLocked = extraction.is_approved || status === "APPROVED";
  const isReviewing = status === "UNDER_REVIEW";
  const canStartReview = status === "EXTRACTION_COMPLETE";
  const handleChange = (field: string, val: string) => setData(prev => ({ ...prev, [field]: val }));

  return (
    <div className="card" style={{ marginBottom: 20, border: isLocked ? "1px solid var(--success)" : undefined }}>
      <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div className="card-title">Clinical Data Review Panel</div>
          <div className="card-desc" style={{ display: 'flex', gap: 12, marginTop: 4 }}>
            <span>Reviewer: {extraction.reviewed_by || "—"}</span>
            <span>Reviewed: {extraction.reviewed_at ? new Date(extraction.reviewed_at + 'Z').toLocaleString() : "—"}</span>
            <span>Approved: {extraction.approved_at ? new Date(extraction.approved_at + 'Z').toLocaleString() : "—"}</span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          {canStartReview && (
            <button onClick={handleStartReview} className="btn btn-primary btn-sm" disabled={startReview.isPending}>
              {startReview.isPending ? <Loader2 size={13} className="animate-spin" /> : <Edit2 size={13} />} Start Review
            </button>
          )}
          {isReviewing && (
            <>
              <button onClick={handleSave} className="btn btn-secondary btn-sm" disabled={updateReview.isPending}>
                {updateReview.isPending ? <Loader2 size={13} className="animate-spin" /> : <Check size={13} />} Save Edits
              </button>
              <button onClick={handleApprove} className="btn btn-primary btn-sm" disabled={approveClaim.isPending} style={{ background: "var(--success)" }}>
                <CheckCircle2 size={13} /> Approve & Lock
              </button>
            </>
          )}
          {isLocked && (
            <span style={{ fontSize: 13, color: "var(--success)", display: "flex", alignItems: "center", gap: 6 }}>
              <CheckCircle2 size={14} /> Approved
            </span>
          )}
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Patient Name</label>
          <input className="input" value={data.patient_name} onChange={e => handleChange("patient_name", e.target.value)} disabled={!isReviewing} />
          
          <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Age</label>
          <input className="input" value={data.age} onChange={e => handleChange("age", e.target.value)} disabled={!isReviewing} />
          
          <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Gender</label>
          <input className="input" value={data.gender} onChange={e => handleChange("gender", e.target.value)} disabled={!isReviewing} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Admission Date</label>
          <input className="input" value={data.admission_date} onChange={e => handleChange("admission_date", e.target.value)} disabled={!isReviewing} />
          
          <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Discharge Date</label>
          <input className="input" value={data.discharge_date} onChange={e => handleChange("discharge_date", e.target.value)} disabled={!isReviewing} />
          
          <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Chief Complaint</label>
          <input className="input" value={data.chief_complaint} onChange={e => handleChange("chief_complaint", e.target.value)} disabled={!isReviewing} />
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
           <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Diagnoses (JSON)</label>
           <textarea className="input" rows={6} value={data.diagnosis_json} onChange={e => handleChange("diagnosis_json", e.target.value)} disabled={!isReviewing} style={{ fontFamily: "monospace", fontSize: 11 }} />
           
           <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Procedures (JSON)</label>
           <textarea className="input" rows={6} value={data.procedures_json} onChange={e => handleChange("procedures_json", e.target.value)} disabled={!isReviewing} style={{ fontFamily: "monospace", fontSize: 11 }} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
           <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Medications (JSON)</label>
           <textarea className="input" rows={6} value={data.medications_json} onChange={e => handleChange("medications_json", e.target.value)} disabled={!isReviewing} style={{ fontFamily: "monospace", fontSize: 11 }} />
           
           <label style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>Investigations (JSON)</label>
           <textarea className="input" rows={6} value={data.investigations_json} onChange={e => handleChange("investigations_json", e.target.value)} disabled={!isReviewing} style={{ fontFamily: "monospace", fontSize: 11 }} />
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// ICD Recommendation Panel
// ─────────────────────────────────────────────

function IcdRecommendationPanel({ claimId, status }: { claimId: string; status: string }) {
  const suggest = useSuggestIcd(claimId);
  const { data: recs, isLoading } = useIcdRecommendations(claimId);
  const accept = useAcceptIcd(claimId);
  const reject = useRejectIcd(claimId);

  if (status !== "APPROVED" && status !== "ICD_MAPPED" && status !== "REPORT_GENERATED") {
    return null;
  }

  const handleSuggest = async () => {
    try {
      await suggest.mutateAsync();
      toast.success("ICD Suggestions generated");
    } catch {
      toast.error("Failed to generate suggestions");
    }
  };

  const handleAccept = async (recId: string) => {
    try {
      await accept.mutateAsync(recId);
      toast.success("Accepted ICD code");
    } catch {
      toast.error("Failed to accept ICD code");
    }
  };

  const handleReject = async (recId: string) => {
    try {
      await reject.mutateAsync(recId);
      toast.success("Rejected ICD code");
    } catch {
      toast.error("Failed to reject ICD code");
    }
  };

  if (isLoading) return <div className="skeleton" style={{ height: 100 }} />;

  const hasRecs = recs && recs.length > 0;
  
  // Group by diagnosis text
  const byDiagnosis: Record<string, any[]> = {};
  if (hasRecs) {
     recs.forEach(r => {
        (byDiagnosis[r.diagnosis_text] = byDiagnosis[r.diagnosis_text] || []).push(r);
     });
  }

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div className="card-title">ICD-10 Recommendations</div>
          <div className="card-desc">Review and accept AI-suggested ICD-10 codes</div>
        </div>
        {!hasRecs && (
          <button 
            className="btn btn-primary btn-sm" 
            onClick={handleSuggest} 
            disabled={suggest.isPending}
          >
            {suggest.isPending ? <Loader2 size={13} className="animate-spin" /> : <BrainCircuit size={13} />}
            Generate Suggestions
          </button>
        )}
      </div>
      
      {hasRecs && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {Object.entries(byDiagnosis).map(([diagText, suggestions], idx) => {
             const accepted = suggestions.find(s => s.status === "ACCEPTED");
             return (
               <div key={idx} style={{ padding: 16, background: "rgba(255,255,255,0.02)", borderRadius: 12, border: "1px solid var(--border)" }}>
                 <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", marginBottom: 12 }}>
                   {diagText}
                 </div>
                 
                 {accepted ? (
                    <div style={{ display: "flex", alignItems: "center", gap: 8, padding: 12, background: "rgba(16,185,129,0.1)", borderRadius: 8, border: "1px solid rgba(16,185,129,0.2)" }}>
                      <CheckCircle2 size={16} style={{ color: "var(--success)" }} />
                      <span style={{ fontSize: 12.5, color: "var(--success)", fontWeight: 600 }}>SELECTED:</span>
                      <code style={{ fontSize: 13, color: "var(--brand-400)" }}>{accepted.icd_code}</code>
                      <span style={{ fontSize: 12, color: "var(--text-primary)" }}>{accepted.description}</span>
                    </div>
                 ) : (
                   <table className="data-table" style={{ margin: 0 }}>
                     <thead>
                       <tr>
                         <th style={{ width: 100 }}>Code</th>
                         <th>Description</th>
                         <th style={{ width: 120 }}>Confidence</th>
                         <th style={{ width: 140 }}>Action</th>
                       </tr>
                     </thead>
                     <tbody>
                       {suggestions.filter(s => s.status !== "REJECTED").map(s => (
                         <tr key={s.id}>
                           <td><code style={{ fontSize: 12, color: "var(--brand-400)" }}>{s.icd_code}</code></td>
                           <td style={{ fontSize: 12 }}>{s.description}</td>
                           <td><ConfidenceBar score={s.confidence} /></td>
                           <td>
                             <div style={{ display: "flex", gap: 6 }}>
                               <button 
                                 className="btn btn-primary btn-sm" 
                                 onClick={() => handleAccept(s.id)}
                                 disabled={accept.isPending || reject.isPending}
                                 style={{ background: "rgba(16,185,129,0.15)", color: "var(--success)" }}
                               >
                                 Accept
                               </button>
                               <button 
                                 className="btn btn-secondary btn-sm"
                                 onClick={() => handleReject(s.id)}
                                 disabled={accept.isPending || reject.isPending}
                                 style={{ color: "var(--danger)" }}
                               >
                                 Reject
                               </button>
                             </div>
                           </td>
                         </tr>
                       ))}
                       {suggestions.filter(s => s.status !== "REJECTED").length === 0 && (
                          <tr><td colSpan={4} style={{ textAlign: "center", padding: 16, color: "var(--text-muted)" }}>All suggestions rejected.</td></tr>
                       )}
                     </tbody>
                   </table>
                 )}
               </div>
             )
          })}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────
// Main Page
// ─────────────────────────────────────────────

export default function ClaimDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: claim, isLoading, refetch } = useClaim(id);
  const triggerOcr = useTriggerOcr(id);
  const { data: ocrResults, refetch: refetchOcr } = useOcrResults(id);
  const triggerExtraction = useTriggerExtraction(id);
  const { data: extractionResult, refetch: refetchExtraction } = useExtractionResult(id);
  const { data: auditLogs, refetch: refetchAudit } = useClaimAudit(id);

  const isProcessingOcr = claim?.status === "OCR_PROCESSING";
  const isProcessingExt = claim?.status === "EXTRACTION_PROCESSING";

  useEffect(() => {
    if (isProcessingOcr || isProcessingExt) {
      const interval = setInterval(() => {
        refetch();
        if (isProcessingOcr) refetchOcr();
        if (isProcessingExt) refetchExtraction();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isProcessingOcr, isProcessingExt, refetch, refetchOcr, refetchExtraction]);

  const handleRunOcr = async () => {
    try {
      await triggerOcr.mutateAsync();
      toast.success("OCR started in background");
      refetch();
    } catch (err) {
      toast.error("Failed to start OCR");
    }
  };

  const handleRunExtraction = async () => {
    try {
      await triggerExtraction.mutateAsync();
      toast.success("Extraction started in background");
      refetch();
    } catch (err) {
      toast.error("Failed to start extraction");
    }
  };

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
            <div style={{ display: "flex", gap: 10 }}>
              {(claim.status === "OCR_COMPLETE" || claim.status === "EXTRACTION_FAILED") && (
                <button
                  onClick={handleRunExtraction}
                  className="btn btn-primary btn-sm"
                  disabled={triggerExtraction.isPending || isProcessingExt}
                  style={{ background: "var(--brand-500)" }}
                >
                  {triggerExtraction.isPending || isProcessingExt ? <Loader2 size={13} className="animate-spin" /> : <BrainCircuit size={13} />}
                  {isProcessingExt ? "Extracting..." : "Run Extraction"}
                </button>
              )}
              {(claim.status === "DOCUMENT_UPLOADED" || claim.status === "OCR_FAILED") && (
                <button
                  onClick={handleRunOcr}
                  className="btn btn-primary btn-sm"
                  disabled={triggerOcr.isPending || isProcessingOcr}
                >
                  {triggerOcr.isPending || isProcessingOcr ? <Loader2 size={13} className="animate-spin" /> : <ScanText size={13} />}
                  {isProcessingOcr ? "Processing..." : "Run OCR"}
                </button>
              )}
              <Link href="/claims/new" className="btn btn-secondary btn-sm">
                <Plus size={13} /> Add
              </Link>
            </div>
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

      {/* Raw OCR Text Display */}
      {ocrResults && ocrResults.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div className="card-title">Extracted Raw Text</div>
              <div className="card-desc">Raw text extracted by PaddleOCR</div>
            </div>
            <button
              onClick={() => {
                const fullText = ocrResults.map(r => `--- Page ${r.page_number} ---\n${r.raw_text}`).join('\n\n');
                const blob = new Blob([fullText], { type: "text/plain" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `claim_${claim.claim_number}_ocr.txt`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="btn btn-secondary btn-sm"
            >
              <Download size={13} /> Download All Text
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {ocrResults.map((res, idx) => (
              <div key={idx} style={{ padding: 16, background: "rgba(255,255,255,0.02)", borderRadius: 12, border: "1px solid var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase" }}>
                    Document ID: {res.document_id.slice(0, 8)} • Page {res.page_number} • Status: {res.status || "COMPLETED"}
                  </div>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(res.raw_text);
                      toast.success(`Page ${res.page_number} copied to clipboard`);
                    }}
                    className="btn btn-ghost btn-sm"
                    title="Copy to clipboard"
                  >
                    <Copy size={13} />
                  </button>
                </div>
                <pre style={{ fontSize: 12, color: "var(--text-primary)", whiteSpace: "pre-wrap", margin: 0, fontFamily: "inherit" }}>
                  {res.raw_text || <span style={{ color: "var(--text-muted)", fontStyle: "italic" }}>No text found on this page.</span>}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extraction Panel */}
      {extractionResult && (
        <ReviewPanel claimId={id} extraction={extractionResult} status={claim.status} />
      )}

      {/* Difference View */}
      {(claim.status === "UNDER_REVIEW" || claim.status === "APPROVED") && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-header">
            <div className="card-title">Review Difference View</div>
            <div className="card-desc">Compare original extracted fields with human edits</div>
          </div>
          <div style={{ display: "flex", gap: 20 }}>
             <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 8, textTransform: "uppercase" }}>Edited Fields</div>
                {!auditLogs || auditLogs.filter(a => a.action === "FIELD_EDITED").length === 0 ? (
                  <p style={{ fontSize: 13, color: "var(--text-muted)" }}>No fields have been edited yet.</p>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {auditLogs.filter(a => a.action === "FIELD_EDITED").map((log, i) => {
                      const fieldKey = Object.keys(log.old_value)[0];
                      const oldVal = typeof log.old_value[fieldKey] === "object" ? JSON.stringify(log.old_value[fieldKey]) : log.old_value[fieldKey];
                      const newVal = typeof log.new_value[fieldKey] === "object" ? JSON.stringify(log.new_value[fieldKey]) : log.new_value[fieldKey];
                      return (
                        <div key={i} style={{ padding: 12, background: "rgba(255,255,255,0.02)", borderRadius: 8, border: "1px solid var(--border)" }}>
                           <div style={{ fontSize: 11, fontWeight: 600, color: "var(--brand-400)", marginBottom: 6 }}>{fieldKey.toUpperCase()}</div>
                           <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                              <div style={{ flex: 1, padding: 8, background: "rgba(239, 68, 68, 0.1)", color: "var(--text-primary)", fontSize: 12, borderRadius: 6 }}>
                                <span style={{ color: "var(--danger)", fontWeight: 600, fontSize: 10, display: "block", marginBottom: 2 }}>EXTRACTED</span>
                                {oldVal || "null"}
                              </div>
                              <Check style={{ color: "var(--text-muted)", flexShrink: 0 }} size={14} />
                              <div style={{ flex: 1, padding: 8, background: "rgba(16, 185, 129, 0.1)", color: "var(--text-primary)", fontSize: 12, borderRadius: 6 }}>
                                <span style={{ color: "var(--success)", fontWeight: 600, fontSize: 10, display: "block", marginBottom: 2 }}>EDITED</span>
                                {newVal || "null"}
                              </div>
                           </div>
                        </div>
                      )
                    })}
                  </div>
                )}
             </div>
          </div>
        </div>
      )}

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

      {/* ICD Recommendations */}
      <IcdRecommendationPanel claimId={id} status={claim.status} />

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
