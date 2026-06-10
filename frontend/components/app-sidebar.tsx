"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  FolderOpen,
  BarChart3,
  Settings,
  Activity,
  ChevronRight,
  Stethoscope,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/claims", label: "Claims", icon: FileText },
  { href: "/documents", label: "Documents", icon: FolderOpen },
  { href: "/reports", label: "Reports", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

// Breadcrumb labels per path segment
const BREADCRUMB_LABELS: Record<string, string> = {
  dashboard: "Dashboard",
  claims: "Claims",
  new: "New Claim",
  documents: "Documents",
  reports: "Reports",
  settings: "Settings",
};

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="app-sidebar">
      {/* Logo */}
      <div className="p-5 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 10,
              background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <Stethoscope size={18} color="white" />
          </div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, letterSpacing: "-0.01em" }}>
              MediClaim AI
            </div>
            <div style={{ fontSize: 10.5, color: "var(--text-muted)", marginTop: 1 }}>
              Clinical Platform
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-3 flex-1 space-y-1">
        <div
          style={{
            fontSize: 10,
            fontWeight: 600,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--text-muted)",
            padding: "8px 10px 4px",
          }}
        >
          Navigation
        </div>
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const isActive =
            pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
          return (
            <Link key={href} href={href} className={`nav-item ${isActive ? "active" : ""}`}>
              <Icon size={16} />
              <span>{label}</span>
              {isActive && (
                <ChevronRight
                  size={13}
                  style={{ marginLeft: "auto", opacity: 0.6 }}
                />
              )}
            </Link>
          );
        })}
      </nav>


    </aside>
  );
}

export function AppBreadcrumb() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  return (
    <nav style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <Link
        href="/dashboard"
        style={{
          fontSize: 12.5,
          color: "var(--text-muted)",
          textDecoration: "none",
          transition: "color 0.15s",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-secondary)")}
        onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-muted)")}
      >
        Home
      </Link>
      {segments.map((seg, i) => {
        const isLast = i === segments.length - 1;
        const label = BREADCRUMB_LABELS[seg] || seg.slice(0, 8) + (seg.length > 8 ? "…" : "");
        return (
          <span key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <ChevronRight size={12} style={{ color: "var(--text-muted)" }} />
            {isLast ? (
              <span style={{ fontSize: 12.5, color: "var(--text-primary)", fontWeight: 500 }}>
                {label}
              </span>
            ) : (
              <Link
                href={`/${segments.slice(0, i + 1).join("/")}`}
                style={{ fontSize: 12.5, color: "var(--text-muted)", textDecoration: "none" }}
              >
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
