import { Activity } from "lucide-react";
import { ocrStages } from "@/lib/mock-data";
import { WorkflowShell } from "@/components/workflow-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ProcessingWorkflowPage() {
  return (
    <WorkflowShell
      step="2"
      title="OCR Processing"
      subtitle="Real-time AI processing tracker across OCR extraction, entity detection, diagnosis parsing, coding, validation, and report generation."
      actions={[{ label: "View extraction", href: "/workflow/extraction" }]}
    >
      <Card className="glass rounded-[2rem] border-0">
        <CardHeader>
          <CardTitle>Live processing pipeline</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {ocrStages.map((stage, index) => {
            const completed = index < 4;
            const inProgress = index === 4;
            return (
              <div key={stage} className="rounded-2xl border border-slate-200/70 bg-white/80 px-4 py-4 dark:border-white/10 dark:bg-white/5">
                <div className="flex items-center justify-between text-sm">
                  <p className="font-medium">{stage}</p>
                  <span className="text-slate-500 dark:text-slate-300">{completed ? "Completed" : inProgress ? "In Progress" : "Queued"}</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                  <div
                    className={`h-full rounded-full ${completed ? "bg-emerald-500" : inProgress ? "bg-sky-500" : "bg-slate-400"}`}
                    style={{ width: `${completed ? 100 : inProgress ? 58 : 10}%` }}
                  />
                </div>
              </div>
            );
          })}
          <div className="mt-4 flex items-center gap-2 text-sm text-sky-700 dark:text-sky-200">
            <Activity className="h-4 w-4" />
            Streaming status updates from OCR and NLP workers
          </div>
        </CardContent>
      </Card>
    </WorkflowShell>
  );
}
