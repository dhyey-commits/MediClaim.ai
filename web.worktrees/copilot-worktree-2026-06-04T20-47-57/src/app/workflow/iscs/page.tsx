import { FileDown, FileText, Link2 } from "lucide-react";
import { demoIcdCodes, demoPatients } from "@/lib/mock-data";
import { WorkflowShell } from "@/components/workflow-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function IscsWorkflowPage() {
  return (
    <WorkflowShell
      step="6"
      title="ISCS Generator"
      subtitle="Generate an Indian Standard Clinical Summary with clinical timeline, diagnosis, investigations, procedures, medication summary, coding, and insurance notes."
      actions={[{ label: "Generate claim packet", href: "/workflow/claims" }]}
    >
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Indian Standard Clinical Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
              <p className="text-sm font-medium">Patient information</p>
              {demoPatients.map((patient) => (
                <p key={patient.name} className="mt-2 text-sm text-slate-500 dark:text-slate-300">
                  {patient.name}, {patient.age} years, diagnosis: {patient.diagnosis}
                </p>
              ))}
            </div>
            <div className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
              <p className="text-sm font-medium">ICD mapping</p>
              {demoIcdCodes.map((code) => (
                <p key={code.code} className="mt-2 text-sm text-slate-500 dark:text-slate-300">
                  {code.code}: {code.label}
                </p>
              ))}
            </div>
            <div className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
              <p className="text-sm font-medium">Insurance notes</p>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-300">Readiness score 92/100. Signature verification pending for one consultant note.</p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Export and share</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-between rounded-2xl">
              <span>Export PDF</span>
              <FileDown className="h-4 w-4" />
            </Button>
            <Button variant="outline" className="w-full justify-between rounded-2xl">
              <span>Export Word</span>
              <FileText className="h-4 w-4" />
            </Button>
            <Button variant="secondary" className="w-full justify-between rounded-2xl">
              <span>Share link</span>
              <Link2 className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>
    </WorkflowShell>
  );
}
