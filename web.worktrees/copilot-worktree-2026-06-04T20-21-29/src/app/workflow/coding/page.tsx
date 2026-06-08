import { codingReviewRows } from "@/lib/mock-data";
import { WorkflowShell } from "@/components/workflow-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CodingWorkflowPage() {
  return (
    <WorkflowShell
      step="4"
      title="Medical Coding Engine"
      subtitle="Auto-map extracted findings to ICD-10, SNOMED CT, CPT, and RxNorm with confidence scoring and manual override."
      actions={[{ label: "Open validation", href: "/workflow/validation" }]}
    >
      <Card className="glass rounded-[2rem] border-0">
        <CardHeader>
          <CardTitle>Coding review dashboard</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {codingReviewRows.map((row) => (
            <div key={`${row.system}-${row.code}`} className="grid gap-3 rounded-2xl border border-slate-200/70 bg-white/80 p-4 text-sm dark:border-white/10 dark:bg-white/5 md:grid-cols-[1.2fr_0.8fr_0.7fr_0.7fr_0.6fr]">
              <div>
                <p className="font-medium">{row.diagnosis}</p>
                <p className="text-slate-500 dark:text-slate-300">{row.system}</p>
              </div>
              <p className="font-mono">{row.code}</p>
              <p>{Math.round(row.confidence * 100)}%</p>
              <Badge variant={row.override === "Yes" ? "secondary" : "outline"}>{row.override === "Yes" ? "Manual override" : "AI suggested"}</Badge>
              <p className="text-sky-700 dark:text-sky-300">Review</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </WorkflowShell>
  );
}
