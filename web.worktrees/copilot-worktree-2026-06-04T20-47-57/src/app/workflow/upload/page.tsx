import { UploadCloud } from "lucide-react";
import { uploadDocumentTypes, uploadQueue } from "@/lib/mock-data";
import { WorkflowShell } from "@/components/workflow-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function UploadWorkflowPage() {
  return (
    <WorkflowShell
      step="1"
      title="Document Upload"
      subtitle="Accept PDFs, scans, prescriptions, lab reports, and radiology files with drag-drop, bulk intake, progress tracking, and OCR status."
      actions={[{ label: "Open OCR processing", href: "/workflow/processing" }]}
    >
      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Bulk upload zone</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-3xl border border-dashed border-sky-300 bg-sky-50/80 p-12 text-center dark:border-sky-400/20 dark:bg-sky-400/10">
              <UploadCloud className="mx-auto h-9 w-9 text-sky-600 dark:text-sky-300" />
              <p className="mt-4 text-lg font-medium">Drag and drop records</p>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-300">PDFs, images, discharge summaries, prescriptions, labs, and radiology reports</p>
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              {uploadDocumentTypes.map((type) => (
                <Badge key={type} variant="outline">
                  {type}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="glass rounded-[2rem] border-0">
          <CardHeader>
            <CardTitle>Upload queue</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {uploadQueue.map((file) => (
              <div key={file.name} className="rounded-2xl border border-slate-200/70 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <p className="font-medium">{file.name}</p>
                  <span className="text-slate-500 dark:text-slate-300">{file.status}</span>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                  <div className="h-full rounded-full bg-sky-500" style={{ width: `${file.progress}%` }} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </WorkflowShell>
  );
}
