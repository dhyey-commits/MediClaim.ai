import { validationChecks } from "@/lib/mock-data";
import { WorkflowShell } from "@/components/workflow-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ValidationWorkflowPage() {
  return (
    <WorkflowShell
      step="5"
      title="Validation Engine"
      subtitle="Run completeness, conflict, signature, documentation, and insurance compliance checks to generate claim readiness score."
      actions={[{ label: "Generate ISCS", href: "/workflow/iscs" }]}
    >
      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Claim readiness score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-3xl bg-slate-950 p-8 text-white dark:bg-white dark:text-slate-950">
              <p className="text-sm text-slate-300 dark:text-slate-600">Current score</p>
              <p className="mt-2 text-6xl font-semibold">92</p>
              <p className="mt-2 text-sm text-emerald-400 dark:text-emerald-600">Excellent insurer readiness</p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Validation checks</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {validationChecks.map((check) => (
              <div key={check.title} className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-medium">{check.title}</p>
                  <Badge variant={check.status === "Warning" ? "secondary" : "outline"}>{check.status}</Badge>
                </div>
                <p className="mt-2 text-sm text-slate-500 dark:text-slate-300">{check.detail}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </WorkflowShell>
  );
}
