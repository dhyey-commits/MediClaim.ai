"use client";

import Link from "next/link";
import { useMemo } from "react";
import { Area, AreaChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart, LineChart, Line } from "recharts";
import { Activity, Bell, Bot, Building2, CheckCircle2, FileText, LayoutDashboard, ShieldAlert, UploadCloud } from "lucide-react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import {
  auditEvents,
  chartData,
  claimPipeline,
  dashboardMetrics,
  fraudSignals,
  inboxItems,
  stakeholders,
} from "@/lib/mock-data";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function DashboardShell() {
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

  const analyticsQuery = useQuery({
    queryKey: ["analytics-overview"],
    queryFn: async () => {
      const response = await fetch(`${apiBase}/analytics/overview`, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Failed to fetch analytics");
      }
      return (await response.json()) as {
        total_claims: number;
        approval_rate: number;
        average_processing_time_minutes: number;
        claim_value_inr: number;
        fraud_alerts: number;
      };
    },
    retry: 1,
  });

  const packetsQuery = useQuery({
    queryKey: ["claim-packets"],
    queryFn: async () => {
      const response = await fetch(`${apiBase}/claims/packets`, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Failed to fetch claim packets");
      }
      return (await response.json()) as Array<{ packet_id: string }>;
    },
    retry: 1,
  });

  const metrics = useMemo(() => {
    if (!analyticsQuery.data) {
      return dashboardMetrics;
    }
    const approved = `${(analyticsQuery.data.approval_rate * 100).toFixed(1)}%`;
    return [
      { label: "Total claims", value: analyticsQuery.data.total_claims.toLocaleString("en-IN"), delta: packetsQuery.data ? `${packetsQuery.data.length} packet(s)` : "+18.4%" },
      { label: "Approval rate", value: approved, delta: "+2.1%" },
      { label: "Avg. processing time", value: `${analyticsQuery.data.average_processing_time_minutes.toFixed(1)}m`, delta: "-24%" },
      { label: "Fraud alerts", value: String(analyticsQuery.data.fraud_alerts), delta: "-11%" },
    ];
  }, [analyticsQuery.data, packetsQuery.data]);

  return (
    <div className="mx-auto min-h-screen max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <aside className="glass-strong sticky top-6 hidden h-[calc(100vh-3rem)] flex-col rounded-[2rem] p-5 lg:flex">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-700 dark:text-sky-300">MediClaim AI</p>
            <p className="mt-2 text-lg font-semibold">Clinical documentation operations</p>
          </div>
          <nav className="mt-8 space-y-2 text-sm">
            {[
              [LayoutDashboard, "Executive Dashboard", "/dashboard"],
              [UploadCloud, "Upload Queue", "/workflow/upload"],
              [FileText, "ISCS Reports", "/workflow/iscs"],
              [ShieldAlert, "Fraud Signals", "/workflow/fraud"],
              [Bot, "Copilot", "/copilot"],
            ].map(([Icon, label, href]) => (
              <Link
                key={label as string}
                href={href as string}
                className="flex items-center gap-3 rounded-2xl px-4 py-3 text-slate-600 hover:bg-white/70 dark:text-slate-300 dark:hover:bg-white/8"
              >
                <Icon className="h-4 w-4" />
                <span>{label as string}</span>
              </Link>
            ))}
          </nav>
          <div className="mt-auto rounded-3xl bg-slate-950 p-4 text-white dark:bg-white dark:text-slate-950">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Building2 className="h-4 w-4" />
              Claims network
            </div>
            <div className="mt-3 space-y-2 text-sm text-slate-300 dark:text-slate-600">
              {stakeholders.map((item) => (
                <div key={item} className="flex items-center justify-between">
                  <span>{item}</span>
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                </div>
              ))}
            </div>
          </div>
        </aside>

        <main className="space-y-6 pb-12">
          <header className="glass-strong flex flex-col gap-4 rounded-[2rem] px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <Badge variant="outline">Executive dashboard</Badge>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight">Claim operations, coding, and risk in one control surface.</h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-300">
                Monitor documentation intake, claim readiness, approval trends, and fraud signals across hospitals and insurers.
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline">View audit trail</Button>
              <Button>Generate ISCS</Button>
            </div>
          </header>

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {metrics.map((metric) => (
              <Card key={metric.label} className="glass rounded-[1.75rem] border-0">
                <CardHeader>
                  <CardDescription>{metric.label}</CardDescription>
                  <CardTitle className="text-3xl">{metric.value}</CardTitle>
                  <CardDescription className="text-emerald-500">{metric.delta}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </section>

          <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <Card className="glass rounded-[2rem] border-0">
              <CardHeader>
                <CardTitle>Approval and claim volume</CardTitle>
                <CardDescription>Trends across the last six months.</CardDescription>
              </CardHeader>
              <CardContent className="h-[340px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="claimsFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.35} />
                        <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.02} />
                      </linearGradient>
                      <linearGradient id="approvalsFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0f172a" stopOpacity={0.45} />
                        <stop offset="95%" stopColor="#0f172a" stopOpacity={0.02} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="claims" stroke="#0ea5e9" fill="url(#claimsFill)" strokeWidth={2} />
                    <Area type="monotone" dataKey="approvals" stroke="#0f172a" fill="url(#approvalsFill)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="glass rounded-[2rem] border-0">
              <CardHeader>
                <CardTitle>Claim pipeline</CardTitle>
                <CardDescription>Current distribution of claim states.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {claimPipeline.map((stage, index) => (
                  <motion.div key={stage} initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }} className="flex items-center gap-3 rounded-2xl border border-slate-200/70 bg-white/80 px-4 py-3 dark:border-white/10 dark:bg-white/5">
                    <div className="h-8 w-8 rounded-full bg-sky-100 text-center text-sm font-semibold leading-8 text-sky-700 dark:bg-sky-400/10 dark:text-sky-200">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{stage}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{150 - index * 17} active items</p>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </section>

          <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
            <Card className="glass rounded-[2rem] border-0">
              <CardHeader>
                <CardTitle>Fraud analysis</CardTitle>
                <CardDescription>Risk score, anomalies, and suspicious patterns.</CardDescription>
              </CardHeader>
              <CardContent className="h-[320px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={fraudSignals} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.12} />
                    <XAxis type="number" hide />
                    <YAxis type="category" dataKey="title" width={150} />
                    <Tooltip />
                    <Bar dataKey="score" radius={[0, 12, 12, 0]}>
                      {fraudSignals.map((entry) => (
                        <Cell key={entry.title} fill={entry.value === "High" ? "#fb7185" : entry.value === "Medium" ? "#f59e0b" : "#60a5fa"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="glass rounded-[2rem] border-0">
              <CardHeader>
                <CardTitle>Operational inbox</CardTitle>
                <CardDescription>Notifications and review items by role.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {inboxItems.map((item) => (
                  <div key={item.text} className="flex items-start gap-3 rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
                    <Bell className="mt-0.5 h-4 w-4 text-sky-600 dark:text-sky-300" />
                    <div>
                      <p className="text-sm font-medium">{item.role}</p>
                      <p className="text-sm text-slate-500 dark:text-slate-300">{item.text}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </section>

          <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
            <Card className="glass rounded-[2rem] border-0">
              <CardHeader>
                <CardTitle>Audit trail</CardTitle>
                <CardDescription>Immutable activity log for governance and compliance.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {auditEvents.map((event) => (
                  <div key={event.action} className="flex items-start justify-between rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
                    <div>
                      <p className="text-sm font-medium">{event.user}</p>
                      <p className="text-sm text-slate-500 dark:text-slate-300">{event.action}</p>
                    </div>
                    <span className="text-xs text-slate-400">{event.time}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="glass rounded-[2rem] border-0">
              <CardHeader>
                <CardTitle>Upload and review queue</CardTitle>
                <CardDescription>Bulk intake, OCR status, and claim packet export readiness.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-3xl border border-dashed border-sky-300 bg-sky-50/80 p-6 text-center dark:border-sky-400/20 dark:bg-sky-400/10">
                  <UploadCloud className="mx-auto h-8 w-8 text-sky-600 dark:text-sky-300" />
                  <p className="mt-4 font-medium">Drop PDFs, scans, prescriptions, or lab reports here</p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">Bulk upload, progress tracking, and OCR status updates</p>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <Button variant="outline" className="justify-between rounded-2xl">
                    <span>Claim packet</span>
                    <FileText className="h-4 w-4" />
                  </Button>
                  <Button variant="secondary" className="justify-between rounded-2xl">
                    <span>Copilot explain</span>
                    <Bot className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex items-center justify-between rounded-2xl bg-slate-950 px-4 py-4 text-white dark:bg-white dark:text-slate-950">
                  <div>
                    <p className="text-sm text-slate-300 dark:text-slate-600">Claim readiness score</p>
                    <p className="text-3xl font-semibold">92</p>
                  </div>
                  <Activity className="h-8 w-8 text-sky-300 dark:text-sky-600" />
                </div>
              </CardContent>
            </Card>
          </section>

          <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
            <Card className="glass rounded-[2rem] border-0">
              <CardHeader>
                <CardTitle>Hospital performance</CardTitle>
                <CardDescription>Claims, approval rate, and turnaround by organization.</CardDescription>
              </CardHeader>
              <CardContent className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.12} />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="approvals" stroke="#0f172a" strokeWidth={3} dot={false} />
                    <Line type="monotone" dataKey="claims" stroke="#0ea5e9" strokeWidth={3} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="glass rounded-[2rem] border-0">
              <CardHeader>
                <CardTitle>Partner distribution</CardTitle>
                <CardDescription>Insurer and scheme readiness by channel.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-5 lg:grid-cols-[220px_1fr]">
                <div className="h-[220px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={[
                        { name: "Star Health", value: 24 },
                        { name: "Niva Bupa", value: 19 },
                        { name: "ICICI Lombard", value: 18 },
                        { name: "HDFC Ergo", value: 16 },
                        { name: "Care Health", value: 23 },
                      ]} dataKey="value" nameKey="name" innerRadius={54} outerRadius={86} paddingAngle={3}>
                        {["#0ea5e9", "#22c55e", "#6366f1", "#f59e0b", "#14b8a6"].map((color) => (
                          <Cell key={color} fill={color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-3">
                  {[
                    ["Star Health", "Ready for submission"],
                    ["Niva Bupa", "Validation in progress"],
                    ["ICICI Lombard", "Manual review required"],
                    ["Government schemes", "Ruleset configured"],
                  ].map(([name, status]) => (
                    <div key={name} className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 text-sm dark:border-white/10 dark:bg-white/5">
                      <p className="font-medium">{name}</p>
                      <p className="mt-1 text-slate-500 dark:text-slate-300">{status}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </section>
        </main>
      </div>
    </div>
  );
}