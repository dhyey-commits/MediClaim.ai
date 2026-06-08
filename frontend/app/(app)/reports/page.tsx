"use client";

import Link from "next/link";
import { BarChart3, Download, Eye, CheckCircle2 } from "lucide-react";
import { useReports } from "@/hooks/queries";
import { formatDate } from "@/lib/utils";
import { api } from "@/services/api";

export default function ReportsPage() {
  const { data: reports, isLoading } = useReports();

  return (
    <div className="animate-fade-in" style={{ maxWidth: 1000 }}>
      <div className="page-header">
        <h1 className="page-title">Reports</h1>
        <p className="page-subtitle">
          {isLoading ? "Loading..." : `${reports?.length || 0} ISCS reports generated`}
        </p>
      </div>

      <div className="card">
        {isLoading ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[...Array(4)].map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 64 }} />
            ))}
          </div>
        ) : !reports?.length ? (
          <div style={{ textAlign: "center", padding: "52px 0" }}>
            <BarChart3 size={44} style={{ color: "var(--text-muted)", margin: "0 auto 14px" }} />
            <p style={{ color: "var(--text-primary)", fontWeight: 600, marginBottom: 6 }}>No reports yet</p>
            <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 16 }}>
              Complete the full claim workflow to generate an ISCS report
            </p>
            <Link href="/claims" className="btn btn-secondary" style={{ display: "inline-flex" }}>
              View Claims
            </Link>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Claim #</th>
                <th>Patient</th>
                <th>Type</th>
                <th>Status</th>
                <th>Generated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report.id}>
                  <td>
                    {report.claim_number ? (
                      <code
                        style={{
                          fontSize: 12.5,
                          color: "var(--brand-400)",
                          background: "rgba(14,165,233,0.08)",
                          padding: "2px 8px",
                          borderRadius: 6,
                        }}
                      >
                        {report.claim_number}
                      </code>
                    ) : (
                      <span style={{ color: "var(--text-muted)" }}>—</span>
                    )}
                  </td>
                  <td>{report.patient_name || <span style={{ color: "var(--text-muted)" }}>—</span>}</td>
                  <td>
                    <span
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        letterSpacing: "0.05em",
                        color: "#6366f1",
                        background: "rgba(99,102,241,0.12)",
                        padding: "2px 8px",
                        borderRadius: 6,
                      }}
                    >
                      {report.report_type}
                    </span>
                  </td>
                  <td>
                    {report.is_generated ? (
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <CheckCircle2 size={14} style={{ color: "var(--success)" }} />
                        <span style={{ fontSize: 12.5, color: "var(--success)" }}>Generated</span>
                      </div>
                    ) : (
                      <span style={{ fontSize: 12.5, color: "var(--text-muted)" }}>Pending</span>
                    )}
                  </td>
                  <td style={{ fontSize: 12.5, color: "var(--text-muted)" }}>
                    {formatDate(report.created_at)}
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <div style={{ display: "flex", gap: 8 }}>
                      <Link href={`/reports/${report.id}`} className="btn btn-secondary btn-sm">
                        <Eye size={13} /> View
                      </Link>
                      {report.is_generated && (
                        <a
                          href={api.reports.downloadUrl(report.id)}
                          download
                          className="btn btn-primary btn-sm"
                        >
                          <Download size={13} /> PDF
                        </a>
                      )}
                    </div>
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
