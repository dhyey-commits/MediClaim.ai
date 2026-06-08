"use client";

import Link from "next/link";
import { Plus, TrendingUp, FileText, BarChart3, FolderOpen, Clock } from "lucide-react";
import { useAnalytics, useClaims } from "@/hooks/queries";
import { formatDate, STATUS_BADGE_CLASS, STATUS_LABELS } from "@/lib/utils";

function MetricCard({
  label,
  value,
  icon: Icon,
  color,
  sub,
}: {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
  sub?: string;
}) {
  return (
    <div className="glass-card" style={{ padding: "20px 22px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <span style={{ fontSize: 12.5, color: "var(--text-secondary)", fontWeight: 500 }}>{label}</span>
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: `${color}18`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Icon size={16} style={{ color }} />
        </div>
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: "-0.02em", color: "var(--text-primary)" }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 11.5, color: "var(--text-muted)", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

export default function DashboardPage() {
  const { data: analytics, isLoading: analyticsLoading } = useAnalytics();
  const { data: claims, isLoading: claimsLoading } = useClaims();

  const recentClaims = analytics?.recent_claims || claims?.slice(0, 5) || [];

  return (
    <div className="animate-fade-in" style={{ maxWidth: 1200 }}>
      {/* Page header */}
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Overview of your clinical documentation pipeline</p>
        </div>
        <Link href="/claims/new" className="btn btn-primary">
          <Plus size={16} />
          New Claim
        </Link>
      </div>

      {/* Metrics */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 16,
          marginBottom: 28,
        }}
      >
        <MetricCard
          label="Total Claims"
          value={analyticsLoading ? "—" : (analytics?.total_claims ?? 0)}
          icon={FileText}
          color="#0ea5e9"
          sub="All time"
        />
        <MetricCard
          label="Claims Processed"
          value={analyticsLoading ? "—" : (analytics?.claims_processed ?? 0)}
          icon={TrendingUp}
          color="#10b981"
          sub="Extraction complete"
        />
        <MetricCard
          label="Reports Generated"
          value={analyticsLoading ? "—" : (analytics?.reports_generated ?? 0)}
          icon={BarChart3}
          color="#6366f1"
          sub="ISCS reports"
        />
        <MetricCard
          label="Total Documents"
          value={analyticsLoading ? "—" : (analytics?.total_documents ?? 0)}
          icon={FolderOpen}
          color="#f59e0b"
          sub="Uploaded files"
        />
      </div>

      {/* Status breakdown + Recent claims */}
      <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20 }}>
        {/* Status Pipeline */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">Claim Pipeline</div>
            <div className="card-desc">Status breakdown across all claims</div>
          </div>
          {analyticsLoading ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[...Array(6)].map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 42 }} />
              ))}
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {Object.entries(analytics?.status_breakdown || {}).map(([status, count]) => (
                <div
                  key={status}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "10px 14px",
                    borderRadius: 10,
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <span className={STATUS_BADGE_CLASS[status] || "badge badge-draft"}>
                    {STATUS_LABELS[status] || status}
                  </span>
                  <span style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)" }}>
                    {count}
                  </span>
                </div>
              ))}
              {(!analytics?.status_breakdown || Object.keys(analytics.status_breakdown).length === 0) && (
                <div style={{ textAlign: "center", padding: "24px 0", color: "var(--text-muted)", fontSize: 13 }}>
                  No claims yet. <Link href="/claims/new" style={{ color: "var(--brand-400)" }}>Create your first claim →</Link>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Recent Claims */}
        <div className="card">
          <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div className="card-title">Recent Claims</div>
              <div className="card-desc">Latest activity in your pipeline</div>
            </div>
            <Link href="/claims" style={{ fontSize: 12.5, color: "var(--brand-400)", textDecoration: "none" }}>
              View all →
            </Link>
          </div>

          {claimsLoading || analyticsLoading ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 52 }} />
              ))}
            </div>
          ) : recentClaims.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px 0" }}>
              <FileText size={40} style={{ color: "var(--text-muted)", margin: "0 auto 12px" }} />
              <p style={{ color: "var(--text-muted)", fontSize: 13 }}>No claims yet</p>
              <Link href="/claims/new" className="btn btn-primary btn-sm" style={{ marginTop: 12, display: "inline-flex" }}>
                <Plus size={14} /> Create first claim
              </Link>
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Claim #</th>
                  <th>Patient</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {recentClaims.map((claim) => (
                  <tr key={claim.id} onClick={() => window.location.href = `/claims/${claim.id}`}>
                    <td style={{ fontFamily: "monospace", fontSize: 12.5, color: "var(--brand-400)" }}>
                      {claim.claim_number}
                    </td>
                    <td>{claim.patient_name || <span style={{ color: "var(--text-muted)" }}>—</span>}</td>
                    <td>
                      <span className={STATUS_BADGE_CLASS[claim.status] || "badge badge-draft"}>
                        {STATUS_LABELS[claim.status] || claim.status}
                      </span>
                    </td>
                    <td style={{ color: "var(--text-muted)", fontSize: 12.5 }}>
                      {formatDate(claim.created_at)}
                    </td>
                    <td>
                      <Link
                        href={`/claims/${claim.id}`}
                        style={{ color: "var(--brand-400)", fontSize: 12, textDecoration: "none" }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        Open →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div style={{ marginTop: 20, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
        {[
          { href: "/claims/new", label: "Upload Discharge Summary", desc: "Start a new claim from a hospital document", icon: Plus, color: "#0ea5e9" },
          { href: "/documents", label: "Browse Documents", desc: "View all uploaded clinical documents", icon: FolderOpen, color: "#6366f1" },
          { href: "/reports", label: "Download Reports", desc: "Access generated ISCS PDF reports", icon: BarChart3, color: "#10b981" },
        ].map(({ href, label, desc, icon: Icon, color }) => (
          <Link
            key={href}
            href={href}
            style={{ textDecoration: "none" }}
          >
            <div
              className="glass-card"
              style={{ padding: "18px 20px", display: "flex", alignItems: "flex-start", gap: 14 }}
            >
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  background: `${color}18`,
                  border: `1px solid ${color}30`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <Icon size={18} style={{ color }} />
              </div>
              <div>
                <div style={{ fontSize: 13.5, fontWeight: 600, color: "var(--text-primary)", marginBottom: 3 }}>{label}</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{desc}</div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
