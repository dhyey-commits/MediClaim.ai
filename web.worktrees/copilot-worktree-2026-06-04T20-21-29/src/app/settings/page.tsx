import { microsaasFeatures } from "@/lib/mock-data";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function SettingsPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <Card className="glass-strong rounded-[2rem] border-0">
        <CardHeader>
          <Badge variant="outline" className="w-fit">
            Micro-SaaS Operations
          </Badge>
          <CardTitle className="mt-4 text-3xl">Settings, governance, and integrations</CardTitle>
          <CardDescription className="max-w-3xl text-base leading-7">
            Configure organization controls, API access, webhooks, notifications, and immutable audit behaviors for enterprise healthcare workflows.
          </CardDescription>
        </CardHeader>
      </Card>

      <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {microsaasFeatures.map((feature) => (
          <Card key={feature.title} className="glass rounded-[1.75rem] border-0">
            <CardHeader>
              <CardTitle className="text-lg">{feature.title}</CardTitle>
              <CardDescription className="text-sm leading-6">{feature.detail}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </section>
    </main>
  );
}
