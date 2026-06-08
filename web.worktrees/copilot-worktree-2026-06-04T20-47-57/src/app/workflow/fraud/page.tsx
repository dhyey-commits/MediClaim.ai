"use client";

import { Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from "recharts";
import { fraudHeatmap, fraudSignals } from "@/lib/mock-data";
import { WorkflowShell } from "@/components/workflow-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function FraudWorkflowPage() {
  return (
    <WorkflowShell
      step="8"
      title="AI Fraud Detection"
      subtitle="Analyze risk score, anomalies, missing evidence, and suspicious patterns with visual risk maps and severity signals."
      actions={[{ label: "Back to dashboard", href: "/dashboard" }]}
    >
      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Risk signal heatmap</CardTitle>
          </CardHeader>
          <CardContent className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fraudHeatmap} layout="vertical">
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="area" width={140} />
                <Tooltip />
                <Bar dataKey="score" radius={[0, 10, 10, 0]}>
                  {fraudHeatmap.map((entry) => (
                    <Cell key={entry.area} fill={entry.score > 75 ? "#fb7185" : entry.score > 60 ? "#f59e0b" : "#38bdf8"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Anomaly findings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {fraudSignals.map((signal) => (
              <div key={signal.title} className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
                <div className="flex items-center justify-between">
                  <p className="font-medium">{signal.title}</p>
                  <span className="text-sm text-slate-500 dark:text-slate-300">{signal.value}</span>
                </div>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-300">Risk score: {signal.score}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </WorkflowShell>
  );
}
