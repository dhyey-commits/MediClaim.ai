"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { UploadCloud, X, FileText, Image, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { useCreateClaim } from "@/hooks/queries";
import { api } from "@/services/api";
import { formatFileSize } from "@/lib/utils";
import { toast } from "sonner";

const ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/jpg", "image/png", "image/tiff"];
const MAX_SIZE = 20 * 1024 * 1024; // 20 MB

interface SelectedFile {
  file: File;
  id: string;
  progress: number;
  status: "pending" | "uploading" | "done" | "error";
  error?: string;
}

export default function NewClaimPage() {
  const router = useRouter();
  const [files, setFiles] = useState<SelectedFile[]>([]);
  const [patientName, setPatientName] = useState("");
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const createClaim = useCreateClaim();

  const onDrop = useCallback((accepted: File[], rejected: import('react-dropzone').FileRejection[]) => {
    const newFiles: SelectedFile[] = accepted.map((f) => ({
      file: f,
      id: Math.random().toString(36).slice(2),
      progress: 0,
      status: "pending",
    }));
    setFiles((prev) => [...prev, ...newFiles]);

    rejected.forEach((r) => {
      toast.error(`${r.file.name}: ${r.errors[0]?.message || "Invalid file"}`);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    onDrop: onDrop as any,
    accept: { "application/pdf": [".pdf"], "image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "image/tiff": [".tiff"] },
    maxSize: MAX_SIZE,
    multiple: true,
  });

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleSubmit = async () => {
    if (files.length === 0) {
      toast.error("Please add at least one document");
      return;
    }
    setIsSubmitting(true);

    try {
      // 1. Create claim
      const claim = await createClaim.mutateAsync({ patient_name: patientName || undefined, notes: notes || undefined });

      // 2. Upload each file with progress simulation
      const fileObjects = files.map((f) => f.file);

      setFiles((prev) => prev.map((f) => ({ ...f, status: "uploading", progress: 30 })));

      await api.claims.upload(claim.id, fileObjects);

      setFiles((prev) => prev.map((f) => ({ ...f, status: "done", progress: 100 })));
      toast.success("Documents uploaded! Redirecting to claim...");

      setTimeout(() => router.push(`/claims/${claim.id}`), 800);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Upload failed";
      toast.error(message);
      setFiles((prev) => prev.map((f) => ({ ...f, status: "error", error: message })));
      setIsSubmitting(false);
    }
  };

  const fileIcon = (type: string) => {
    if (type.includes("pdf")) return <FileText size={18} style={{ color: "#f59e0b" }} />;
    return <Image size={18} style={{ color: "#0ea5e9" }} />;
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: 760 }}>
      <div className="page-header">
        <h1 className="page-title">New Claim</h1>
        <p className="page-subtitle">Upload a hospital discharge summary to begin the AI processing workflow</p>
      </div>

      {/* Optional patient info */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Claim Details</div>
          <div className="card-desc">Optional — will be auto-extracted from documents</div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
              Patient Name (optional)
            </label>
            <input
              className="input"
              placeholder="e.g. Ramesh Kumar"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
              Notes (optional)
            </label>
            <input
              className="input"
              placeholder="Any additional context..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
        </div>
      </div>

      {/* Drop zone */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Upload Documents</div>
          <div className="card-desc">PDF, JPEG, PNG, TIFF — max 20 MB per file</div>
        </div>

        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? "drag-over" : ""}`}
          style={isSubmitting ? { pointerEvents: "none", opacity: 0.6 } : {}}
        >
          <input {...(getInputProps() as React.InputHTMLAttributes<HTMLInputElement>)} />
          <UploadCloud
            size={40}
            style={{
              color: isDragActive ? "var(--brand-400)" : "var(--text-muted)",
              margin: "0 auto 14px",
              display: "block",
              transition: "color 0.2s",
            }}
          />
          <p style={{ fontSize: 15, fontWeight: 600, color: "var(--text-primary)", marginBottom: 6 }}>
            {isDragActive ? "Drop files here" : "Drag & drop your discharge summary"}
          </p>
          <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
            or click to browse • Multiple files supported
          </p>
        </div>

        {/* File list */}
        {files.length > 0 && (
          <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 10 }}>
            {files.map((f) => (
              <div
                key={f.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "12px 14px",
                  borderRadius: 12,
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid var(--border)",
                }}
              >
                {fileIcon(f.file.type)}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 500, color: "var(--text-primary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {f.file.name}
                  </div>
                  <div style={{ fontSize: 11.5, color: "var(--text-muted)", marginTop: 2 }}>
                    {formatFileSize(f.file.size)}
                  </div>
                  {f.status === "uploading" && (
                    <div className="confidence-bar" style={{ marginTop: 6 }}>
                      <div
                        className="confidence-fill confidence-high"
                        style={{ width: `${f.progress}%` }}
                      />
                    </div>
                  )}
                </div>
                <div style={{ flexShrink: 0 }}>
                  {f.status === "pending" && !isSubmitting && (
                    <button onClick={() => removeFile(f.id)} className="btn btn-ghost btn-sm" style={{ padding: "4px 6px" }}>
                      <X size={14} />
                    </button>
                  )}
                  {f.status === "uploading" && <Loader2 size={16} style={{ color: "var(--brand-400)", animation: "spin 1s linear infinite" }} />}
                  {f.status === "done" && <CheckCircle2 size={16} style={{ color: "var(--success)" }} />}
                  {f.status === "error" && <AlertCircle size={16} style={{ color: "var(--danger)" }} />}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Submit */}
      <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
        <button
          onClick={() => router.back()}
          className="btn btn-secondary"
          disabled={isSubmitting}
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          className="btn btn-primary"
          disabled={files.length === 0 || isSubmitting}
        >
          {isSubmitting ? (
            <>
              <span className="spinner" style={{ width: 16, height: 16 }} />
              Uploading...
            </>
          ) : (
            <>
              <UploadCloud size={16} />
              Upload & Create Claim
            </>
          )}
        </button>
      </div>
    </div>
  );
}
