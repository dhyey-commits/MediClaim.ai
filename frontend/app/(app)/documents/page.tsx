"use client";

import Link from "next/link";
import { FolderOpen, FileText, Image } from "lucide-react";
import { useDocuments } from "@/hooks/queries";
import { formatDate, formatFileSize } from "@/lib/utils";

const DOC_STATUS_COLOR: Record<string, string> = {
  PENDING: "#94a3b8",
  OCR_PROCESSING: "#f59e0b",
  OCR_COMPLETE: "#10b981",
  FAILED: "#ef4444",
};

export default function DocumentsPage() {
  const { data: documents, isLoading } = useDocuments();

  return (
    <div className="animate-fade-in" style={{ maxWidth: 1000 }}>
      <div className="page-header">
        <h1 className="page-title">Documents</h1>
        <p className="page-subtitle">
          {isLoading ? "Loading..." : `${documents?.length || 0} uploaded documents`}
        </p>
      </div>

      <div className="card">
        {isLoading ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 64 }} />
            ))}
          </div>
        ) : !documents?.length ? (
          <div style={{ textAlign: "center", padding: "52px 0" }}>
            <FolderOpen size={44} style={{ color: "var(--text-muted)", margin: "0 auto 14px" }} />
            <p style={{ color: "var(--text-primary)", fontWeight: 600, marginBottom: 6 }}>No documents yet</p>
            <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 16 }}>
              Upload documents by creating a new claim
            </p>
            <Link href="/claims/new" className="btn btn-primary" style={{ display: "inline-flex" }}>
              Upload Documents
            </Link>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>File</th>
                <th>Type</th>
                <th>Claim</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Size</th>
                <th>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} onClick={() => (window.location.href = `/claims/${doc.claim_id}`)}>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      {doc.file_type?.includes("pdf") ? (
                        <FileText size={15} style={{ color: "#f59e0b", flexShrink: 0 }} />
                      ) : (
                        <Image size={15} style={{ color: "#0ea5e9", flexShrink: 0 }} />
                      )}
                      <span
                        style={{
                          maxWidth: 200,
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                          fontSize: 13,
                        }}
                      >
                        {doc.file_name}
                      </span>
                    </div>
                  </td>
                  <td style={{ fontSize: 12, color: "var(--text-muted)" }}>
                    {doc.file_type?.split("/")[1]?.toUpperCase() || "—"}
                  </td>
                  <td>
                    {doc.claim_number ? (
                      <code
                        style={{
                          fontSize: 12,
                          color: "var(--brand-400)",
                          background: "rgba(14,165,233,0.08)",
                          padding: "2px 6px",
                          borderRadius: 5,
                        }}
                      >
                        {doc.claim_number}
                      </code>
                    ) : (
                      <span style={{ color: "var(--text-muted)" }}>—</span>
                    )}
                  </td>
                  <td>
                    <span
                      style={{
                        fontSize: 11.5,
                        fontWeight: 600,
                        color: DOC_STATUS_COLOR[doc.status] || "var(--text-muted)",
                        background: `${DOC_STATUS_COLOR[doc.status] || "#94a3b8"}15`,
                        padding: "2px 8px",
                        borderRadius: 6,
                      }}
                    >
                      {doc.status}
                    </span>
                  </td>
                  <td>
                    {doc.confidence_score > 0 ? (
                      <span style={{ fontSize: 12.5, color: "var(--text-primary)" }}>
                        {Math.round(doc.confidence_score * 100)}%
                      </span>
                    ) : (
                      <span style={{ color: "var(--text-muted)" }}>—</span>
                    )}
                  </td>
                  <td style={{ fontSize: 12.5, color: "var(--text-muted)" }}>
                    {formatFileSize(doc.file_size)}
                  </td>
                  <td style={{ fontSize: 12, color: "var(--text-muted)" }}>
                    {formatDate(doc.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
