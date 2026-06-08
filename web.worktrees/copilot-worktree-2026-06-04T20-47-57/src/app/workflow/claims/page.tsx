import { claimPackets, claimPipeline, insurers } from "@/lib/mock-data";
import { WorkflowShell } from "@/components/workflow-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ClaimsWorkflowPage() {
  return (
    <WorkflowShell
      step="7"
      title="Claim Generation"
      subtitle="Generate insurer-ready claim packets for private insurers and government schemes with full claim status pipeline tracking."
      actions={[{ label: "Open fraud analysis", href: "/workflow/fraud" }]}
    >
      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Insurer network</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            {insurers.map((insurer) => (
              <div key={insurer} className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 text-sm dark:border-white/10 dark:bg-white/5">
                {insurer}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Claim status pipeline</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {claimPipeline.map((stage) => (
              <Badge key={stage} variant="outline">
                {stage}
              </Badge>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card className="glass mt-6 rounded-[2rem] border-0">
        <CardHeader>
          <CardTitle>Insurer-ready packet list</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {claimPackets.map((packet) => (
            <div key={packet.id} className="grid gap-3 rounded-2xl border border-slate-200/70 bg-white/80 p-4 text-sm dark:border-white/10 dark:bg-white/5 md:grid-cols-[0.9fr_1.2fr_0.8fr_0.8fr]">
              <p className="font-medium">{packet.id}</p>
              <p>{packet.insurer}</p>
              <Badge variant="outline">{packet.status}</Badge>
              <p className="text-slate-500 dark:text-slate-300">{packet.amount}</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </WorkflowShell>
  );
}
