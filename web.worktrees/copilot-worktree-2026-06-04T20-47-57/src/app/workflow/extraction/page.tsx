import { extractionConfidence, medicalTimeline } from "@/lib/mock-data";
import { WorkflowShell } from "@/components/workflow-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ExtractionWorkflowPage() {
  return (
    <WorkflowShell
      step="3"
      title="Clinical Extraction"
      subtitle="Extract patient details, symptoms, diagnosis, procedures, investigations, medications, and admission/discharge details with confidence scoring."
      actions={[{ label: "Review coding", href: "/workflow/coding" }]}
    >
      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Extracted clinical timeline</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {medicalTimeline.map((event) => (
              <div key={event.time} className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500 dark:text-slate-300">{event.time}</p>
                <p className="mt-1 font-medium">{event.label}</p>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-300">{event.detail}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Confidence matrix</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {extractionConfidence.map((row) => (
              <div key={row.field} className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
                <div className="flex items-center justify-between text-sm">
                  <p className="font-medium">{row.field}</p>
                  <p>{Math.round(row.confidence * 100)}%</p>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                  <div className="h-full rounded-full bg-sky-500" style={{ width: `${Math.round(row.confidence * 100)}%` }} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </WorkflowShell>
  );
}
