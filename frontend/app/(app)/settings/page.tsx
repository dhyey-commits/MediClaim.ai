"use client";

import { Settings, Key, Bell, Shield, Database } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="animate-fade-in" style={{ maxWidth: 720 }}>
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Platform configuration and integrations</p>
      </div>

      {/* Environment Status */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Environment Status</div>
          <div className="card-desc">Current integration configuration</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[
            {
              label: "Database",
              value: "PostgreSQL (connected)",
              status: "ok",
              icon: Database,
              desc: "Automatic table creation enabled",
            },
            {
              label: "File Storage",
              value: "Local disk (uploads/)",
              status: "ok",
              icon: Shield,
              desc: "Files stored in api/uploads/{claim_id}/",
            },
            {
              label: "AI Extraction",
              value: process.env.NEXT_PUBLIC_OPENAI_KEY ? "GPT-4o Vision" : "Simulation Mode",
              status: process.env.NEXT_PUBLIC_OPENAI_KEY ? "ok" : "warn",
              icon: Key,
              desc: "Set OPENAI_API_KEY in api/.env to enable real extraction",
            },
            {
              label: "Authentication",
              value: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ? "Clerk (active)" : "Dev bypass mode",
              status: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ? "ok" : "warn",
              icon: Shield,
              desc: "Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY to enable auth",
            },
          ].map(({ label, value, status, icon: Icon, desc }) => (
            <div
              key={label}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                padding: "14px 16px",
                borderRadius: 12,
                background: "rgba(255,255,255,0.03)",
                border: "1px solid var(--border)",
              }}
            >
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  background: status === "ok" ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <Icon size={18} style={{ color: status === "ok" ? "var(--success)" : "var(--warning)" }} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 13.5, fontWeight: 600, color: "var(--text-primary)" }}>{label}</span>
                  <span
                    style={{
                      fontSize: 11.5,
                      padding: "2px 8px",
                      borderRadius: 6,
                      background: status === "ok" ? "rgba(16,185,129,0.1)" : "rgba(245,158,11,0.1)",
                      color: status === "ok" ? "var(--success)" : "var(--warning)",
                    }}
                  >
                    {value}
                  </span>
                </div>
                <p style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 3 }}>{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* API Keys */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">Configuration</div>
          <div className="card-desc">Environment variables in <code style={{ fontSize: 11, color: "var(--brand-400)" }}>api/.env</code></div>
        </div>
        <div
          style={{
            background: "rgba(0,0,0,0.3)",
            borderRadius: 12,
            padding: 16,
            fontFamily: "monospace",
            fontSize: 12.5,
            lineHeight: 2,
            color: "var(--text-secondary)",
            border: "1px solid var(--border)",
          }}
        >
          <div><span style={{ color: "#94a3b8" }}># Database</span></div>
          <div><span style={{ color: "#10b981" }}>DATABASE_URL</span>=postgresql+asyncpg://mediclaim:mediclaim@localhost:5432/mediclaim</div>
          <div style={{ marginTop: 8 }}><span style={{ color: "#94a3b8" }}># AI Extraction (optional)</span></div>
          <div><span style={{ color: "#f59e0b" }}>OPENAI_API_KEY</span>=sk-... (leave empty for simulation)</div>
          <div style={{ marginTop: 8 }}><span style={{ color: "#94a3b8" }}># Auth (optional)</span></div>
          <div><span style={{ color: "#a78bfa" }}>NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</span>=pk_...</div>
          <div><span style={{ color: "#a78bfa" }}>CLERK_SECRET_KEY</span>=sk_...</div>
          <div style={{ marginTop: 8 }}><span style={{ color: "#94a3b8" }}># Storage (optional — local disk default)</span></div>
          <div><span style={{ color: "#60a5fa" }}>AWS_ACCESS_KEY_ID</span>=...</div>
          <div><span style={{ color: "#60a5fa" }}>AWS_SECRET_ACCESS_KEY</span>=...</div>
          <div><span style={{ color: "#60a5fa" }}>AWS_S3_BUCKET</span>=mediclaim-uploads</div>
        </div>
      </div>

      {/* Quick links */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Resources</div>
        </div>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">
            API Docs (Swagger)
          </a>
          <a href="http://localhost:8000/redoc" target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">
            ReDoc
          </a>
        </div>
      </div>
    </div>
  );
}
