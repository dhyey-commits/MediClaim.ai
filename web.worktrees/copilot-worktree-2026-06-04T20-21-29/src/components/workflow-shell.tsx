"use client";

import Link from "next/link";
import { ReactNode } from "react";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import { workflowNav } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

type WorkflowShellProps = {
  step: string;
  title: string;
  subtitle: string;
  actions?: Array<{ label: string; href: string }>;
  children: ReactNode;
};

export function WorkflowShell({ step, title, subtitle, actions = [], children }: WorkflowShellProps) {
  return (
    <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <aside className="glass-strong sticky top-6 hidden h-[calc(100vh-3rem)] rounded-[2rem] p-5 lg:block">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-700 dark:text-sky-300">MediClaim AI flow</p>
          <p className="mt-3 text-lg font-semibold">Clinical documentation pipeline</p>
          <div className="mt-7 space-y-2">
            {workflowNav.map((item) => {
              const active = item.label.startsWith(step);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between rounded-2xl px-4 py-3 text-sm transition ${
                    active
                      ? "bg-sky-600 text-white"
                      : "bg-white/70 text-slate-600 hover:bg-white dark:bg-white/5 dark:text-slate-300"
                  }`}
                >
                  <span>{item.label}</span>
                  {active ? <CheckCircle2 className="h-4 w-4" /> : <ArrowRight className="h-4 w-4" />}
                </Link>
              );
            })}
          </div>
          <div className="mt-8 rounded-3xl bg-slate-950 p-4 text-white dark:bg-white dark:text-slate-950">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300 dark:text-slate-500">Platform story</p>
            <p className="mt-2 text-sm leading-6">
              Hospital records to AI standardization, ISCS, coding, claim readiness, and insurance processing.
            </p>
          </div>
        </aside>

        <section className="space-y-6">
          <Card className="glass-strong rounded-[2rem] border-0">
            <CardHeader>
              <Badge variant="outline" className="w-fit">
                Step {step}
              </Badge>
              <CardTitle className="mt-4 text-3xl">{title}</CardTitle>
              <CardDescription className="max-w-3xl text-base leading-7">{subtitle}</CardDescription>
            </CardHeader>
            {!!actions.length && (
              <CardContent className="flex flex-wrap gap-3 pt-0">
                {actions.map((action) => (
                  <Button key={action.href} asChild variant="outline">
                    <Link href={action.href}>{action.label}</Link>
                  </Button>
                ))}
              </CardContent>
            )}
          </Card>

          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
            {children}
          </motion.div>
        </section>
      </div>
    </main>
  );
}
