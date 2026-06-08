"use client";

import { Bell, Search, User } from "lucide-react";
import { AppBreadcrumb } from "./app-sidebar";

// Conditionally use Clerk hooks only when configured
let ClerkUserButton: React.ComponentType<{ appearance?: object }> | null = null;
try {
  if (process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    const clerk = require("@clerk/nextjs");
    ClerkUserButton = clerk.UserButton;
  }
} catch {
  ClerkUserButton = null;
}

export function AppTopbar() {
  return (
    <header className="app-topbar">
      {/* Breadcrumb */}
      <div style={{ flex: 1 }}>
        <AppBreadcrumb />
      </div>

      {/* Search */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          background: "rgba(255,255,255,0.05)",
          border: "1px solid var(--border)",
          borderRadius: 10,
          padding: "6px 12px",
          minWidth: 200,
        }}
      >
        <Search size={14} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
        <input
          placeholder="Search claims..."
          style={{
            background: "transparent",
            border: "none",
            outline: "none",
            fontSize: 13,
            color: "var(--text-primary)",
            width: "100%",
          }}
        />
      </div>

      {/* Notifications */}
      <button
        style={{
          width: 36,
          height: 36,
          borderRadius: 10,
          background: "rgba(255,255,255,0.05)",
          border: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          position: "relative",
          flexShrink: 0,
        }}
      >
        <Bell size={16} style={{ color: "var(--text-secondary)" }} />
        <span
          style={{
            position: "absolute",
            top: 6,
            right: 6,
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: "#0ea5e9",
            border: "1.5px solid #0a0f1e",
          }}
        />
      </button>

      {/* User */}
      {ClerkUserButton ? (
        <ClerkUserButton
          appearance={{
            elements: { avatarBox: { width: 34, height: 34 } },
          }}
        />
      ) : (
        <div
          style={{
            width: 34,
            height: 34,
            borderRadius: "50%",
            background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <User size={16} color="white" />
        </div>
      )}
    </header>
  );
}
