"use client";

import { motion } from "framer-motion";
import { claimStatuses, medicalTimeline, featureBlocks } from "@/lib/mock-data";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function HeroVisual() {
  return (
    <div className="relative">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65, delay: 0.12 }}
        className="glass-strong relative overflow-hidden rounded-[2rem] border-0 p-5 shadow-2xl shadow-sky-500/10"
      >
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.14),transparent_28%),radial-gradient(circle_at_bottom_left,rgba(14,165,233,0.12),transparent_32%)]" />
        <div className="relative grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
          <Card className="rounded-[1.5rem] border border-white/40 bg-white/90 dark:border-white/10 dark:bg-slate-950/80">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardDescription>Document processing</CardDescription>
                  <CardTitle className="mt-2 text-2xl">Real-time AI workflow</CardTitle>
                </div>
                <Badge variant="secondary">97% confidence</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {medicalTimeline.map((item) => (
                <div key={item.time} className="flex gap-4 rounded-2xl border border-slate-200/70 bg-slate-50/80 p-4 dark:border-white/10 dark:bg-white/5">
                  <div className="min-w-14 font-mono text-xs text-slate-500">{item.time}</div>
                  <div>
                    <p className="font-medium text-slate-950 dark:text-white">{item.label}</p>
                    <p className="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-300">{item.detail}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <div className="grid gap-4">
            <Card className="rounded-[1.5rem] border-0 bg-slate-950 text-white shadow-xl dark:bg-white dark:text-slate-950">
              <CardHeader>
                <CardDescription className="text-slate-300 dark:text-slate-600">Claim readiness</CardDescription>
                <CardTitle className="text-4xl">92 / 100</CardTitle>
                <CardDescription className="text-slate-300 dark:text-slate-600">Validation passed for signature, timeline, and evidence completeness.</CardDescription>
              </CardHeader>
            </Card>

            <Card className="rounded-[1.5rem] border-0 bg-white/90 dark:bg-white/5">
              <CardHeader>
                <CardDescription>Claim pipeline</CardDescription>
                <CardTitle className="text-2xl">Draft to approved</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {claimStatuses.map((status) => (
                  <div key={status.label} className="flex items-center gap-3">
                    <div className={`h-3 w-3 rounded-full ${status.color}`} />
                    <div className="flex-1 text-sm text-slate-600 dark:text-slate-300">{status.label}</div>
                    <div className="font-mono text-sm">{status.count}</div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="relative mt-4 grid gap-4 lg:grid-cols-5">
          {featureBlocks.slice(0, 5).map((feature) => (
            <Card key={feature.title} className="rounded-[1.35rem] border border-white/50 bg-white/80 p-4 dark:border-white/10 dark:bg-white/5 lg:col-span-1">
              <feature.icon className="h-5 w-5 text-sky-600 dark:text-sky-300" />
              <h4 className="mt-3 text-sm font-semibold">{feature.title}</h4>
            </Card>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
