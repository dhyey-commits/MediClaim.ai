"use client";

import { use } from "react";
import Link from "next/link";
import { Download, ArrowLeft, CheckCircle2 } from "lucide-react";
import { useReport } from "@/hooks/queries";
import { api } from "@/services/api";
import { formatDate } from "@/lib/utils";

interface ISCSSection {
  title: string;
  content: string[];
}

export default function ReportDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: report, isLoading } = useReport(id);

  if (isLoading) {
    return (
      <div style={{ maxWidth: 800 }}>
        {[...Array(6)].map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 100, marginBottom: 14 }} />
        ))}
      </div>
    );
  }

  if (!report) {
    return (
      <div style={{ textAlign: "center", padding: 60 }}>
        <p style={{ color: "var(--text-muted)" }}>Report not found</p>
        <Link href="/reports" className="btn btn-secondary btn-sm" style={{ marginTop: 12, display: "inline-flex" }}>
          Back to reports
        </Link>
      </div>
    );
  }

  const sections: ISCSSection[] = (report.report_data as { sections?: ISCSSection[] } | null)?.sections || [];

  return (
    <div className="animate-fade-in" style={{ maxWidth: 820 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <Link href="/reports" className="btn btn-ghost btn-sm" style={{ padding: "4px 6px" }}>
              <ArrowLeft size={16} />
            </Link>
            <h1 className="page-title" style={{ fontSize: 20 }}>ISCS Report</h1>
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
          </div>
          <p className="page-subtitle">
            {report.claim_number && `Claim ${report.claim_number} • `}
            {report.patient_name && `${report.patient_name} • `}
            Generated {formatDate(report.created_at)}
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <Link href={`/claims/${report.claim_id}`} className="btn btn-secondary btn-sm">
            View Claim
          </Link>
          {report.is_generated && (
            <a href={api.reports.downloadUrl(report.id)} download className="btn btn-primary btn-sm">
              <Download size={14} /> Download PDF
            </a>
          )}
        </div>
      </div>

      {/* Status banner */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "14px 18px",
          borderRadius: 14,
          background: "rgba(16,185,129,0.08)",
          border: "1px solid rgba(16,185,129,0.25)",
          marginBottom: 24,
        }}
      >
        <CheckCircle2 size={20} style={{ color: "var(--success)", flexShrink: 0 }} />
        <div>
          <p style={{ fontSize: 13.5, fontWeight: 600 }}>Indian Standard Clinical Summary — Version {report.version}</p>
          <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
            This report meets ISCS v1.0 standards for insurance claim submission
          </p>
        </div>
      </div>

      {/* Report sections */}
      {sections.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {sections.map((section, i) => (
            <div key={i} className="card">
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  marginBottom: 14,
                  paddingBottom: 12,
                  borderBottom: "1px solid var(--border)",
                }}
              >
                <div
                  style={{
                    width: 6,
                    height: 20,
                    borderRadius: 3,
                    background: "linear-gradient(to bottom, #0ea5e9, #6366f1)",
                    flexShrink: 0,
                  }}
                />
                <h2 style={{ fontSize: 14, fontWeight: 700, color: "var(--text-primary)" }}>
                  {section.title}
                </h2>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {section.content.map((line, j) => (
                  <div
                    key={j}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: 10,
                      padding: "8px 12px",
                      borderRadius: 10,
                      background: "rgba(255,255,255,0.02)",
                    }}
                  >
                    <span style={{ color: "var(--brand-400)", fontSize: 10, marginTop: 3, flexShrink: 0 }}>●</span>
                    <span style={{ fontSize: 13.5, color: "var(--text-primary)", lineHeight: 1.5 }}>{line}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card" style={{ textAlign: "center", padding: 40 }}>
          <p style={{ color: "var(--text-muted)" }}>Report data not available</p>
        </div>
      )}
    </div>
  );
}
