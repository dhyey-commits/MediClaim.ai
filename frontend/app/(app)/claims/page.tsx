"use client";

import Link from "next/link";
import { Plus, FileText, Search } from "lucide-react";
import { useClaims } from "@/hooks/queries";
import { formatDate, STATUS_BADGE_CLASS, STATUS_LABELS } from "@/lib/utils";
import { useState } from "react";

export default function ClaimsPage() {
  const { data: claims, isLoading } = useClaims();
  const [search, setSearch] = useState("");

  const filtered = (claims || []).filter((c) => {
    const q = search.toLowerCase();
    return (
      !q ||
      c.claim_number.toLowerCase().includes(q) ||
      (c.patient_name || "").toLowerCase().includes(q) ||
      c.status.toLowerCase().includes(q)
    );
  });

  return (
    <div className="animate-fade-in" style={{ maxWidth: 1100 }}>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 className="page-title">Claims</h1>
          <p className="page-subtitle">
            {isLoading ? "Loading..." : `${claims?.length || 0} total claims`}
          </p>
        </div>
        <Link href="/claims/new" className="btn btn-primary">
          <Plus size={16} /> New Claim
        </Link>
      </div>

      {/* Search */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <Search size={15} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
          <input
            className="input"
            style={{ border: "none", background: "transparent", padding: "4px 0" }}
            placeholder="Search by claim number, patient name, or status..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="card">
        {isLoading ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 52 }} />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: "center", padding: "52px 0" }}>
            <FileText size={44} style={{ color: "var(--text-muted)", margin: "0 auto 14px" }} />
            <p style={{ color: "var(--text-primary)", fontWeight: 600, marginBottom: 6 }}>
              {search ? "No matching claims" : "No claims yet"}
            </p>
            <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 16 }}>
              {search ? "Try a different search term" : "Upload a hospital discharge summary to get started"}
            </p>
            {!search && (
              <Link href="/claims/new" className="btn btn-primary" style={{ display: "inline-flex" }}>
                <Plus size={15} /> Create first claim
              </Link>
            )}
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Claim #</th>
                <th>Patient Name</th>
                <th>Status</th>
                <th>Documents</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((claim) => (
                <tr
                  key={claim.id}
                  onClick={() => (window.location.href = `/claims/${claim.id}`)}
                >
                  <td>
                    <code
                      style={{
                        fontSize: 12.5,
                        color: "var(--brand-400)",
                        background: "rgba(14,165,233,0.08)",
                        padding: "2px 8px",
                        borderRadius: 6,
                      }}
                    >
                      {claim.claim_number}
                    </code>
                  </td>
                  <td>
                    {claim.patient_name || (
                      <span style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
                        Pending extraction
                      </span>
                    )}
                  </td>
                  <td>
                    <span className={STATUS_BADGE_CLASS[claim.status] || "badge badge-draft"}>
                      {STATUS_LABELS[claim.status] || claim.status}
                    </span>
                  </td>
                  <td>
                    <span
                      style={{
                        fontSize: 12.5,
                        color: claim.document_count > 0 ? "var(--text-primary)" : "var(--text-muted)",
                      }}
                    >
                      {claim.document_count} file{claim.document_count !== 1 ? "s" : ""}
                    </span>
                  </td>
                  <td style={{ color: "var(--text-muted)", fontSize: 12.5 }}>
                    {formatDate(claim.created_at)}
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <Link
                      href={`/claims/${claim.id}`}
                      className="btn btn-secondary btn-sm"
                    >
                      Open
                    </Link>
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
