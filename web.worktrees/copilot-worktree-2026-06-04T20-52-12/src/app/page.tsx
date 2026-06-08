"use client";

import Link from "next/link";
import { ArrowRight, BadgeCheck, ShieldCheck, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { landingStats, workflowSteps, productCapabilities, testimonials, pricingPlans, faqs } from "@/lib/mock-data";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { HeroVisual } from "@/components/sections/hero-visual";
import { ThemeToggle } from "@/components/theme-toggle";

export default function Home() {
  return (
    <main className="relative overflow-hidden">
      <div className="absolute inset-x-0 top-0 -z-10 h-[36rem] bg-[radial-gradient(circle_at_top,rgba(30,136,255,0.18),transparent_45%),linear-gradient(180deg,rgba(15,23,42,0.02),transparent)]" />
      <div className="grid-noise absolute inset-0 -z-20 opacity-[0.24] dark:opacity-[0.12]" />

      <section className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 pb-12 pt-6 lg:px-8">
        <header className="glass-strong sticky top-4 z-40 flex items-center justify-between rounded-3xl px-5 py-4 shadow-[0_20px_70px_rgba(15,23,42,0.08)]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-700 dark:text-sky-300">
              MediClaim AI
            </p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
              India&apos;s first Clinical Documentation Standardization Platform
            </p>
          </div>
          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-600 md:flex dark:text-slate-300">
            <Link href="#features">Features</Link>
            <Link href="#workflow">Workflow</Link>
            <Link href="#pricing">Pricing</Link>
            <Link href="#faq">FAQ</Link>
            <Link href="#contact">Contact</Link>
          </nav>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Button variant="ghost" asChild className="hidden sm:inline-flex">
              <Link href="/dashboard">Open Demo</Link>
            </Button>
            <Button asChild>
              <Link href="/dashboard">
                Launch Platform <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </header>

        <div className="grid flex-1 items-center gap-14 py-14 lg:grid-cols-[1.1fr_0.9fr] lg:py-20">
          <div className="max-w-3xl">
            <Badge className="mb-5 border-sky-200 bg-sky-50/90 text-sky-800 hover:bg-sky-100 dark:border-sky-400/20 dark:bg-sky-400/10 dark:text-sky-200">
              <Sparkles className="mr-2 h-3.5 w-3.5" />
              OCR, coding, validation, and claim readiness in one flow
            </Badge>
            <motion.h1
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55 }}
              className="max-w-4xl text-balance text-5xl font-semibold tracking-tight text-slate-950 sm:text-6xl lg:text-7xl dark:text-white"
            >
              Transform clinical notes into insurance-ready claims in minutes.
            </motion.h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
              MediClaim AI standardizes hospital records into ISCS reports, maps diagnoses to ICD-10,
              SNOMED CT, CPT, and RxNorm, and produces a claim packet with validation, fraud signals,
              and a copilot that helps every role move faster.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Button size="lg" asChild>
                <Link href="/dashboard">
                  Explore the platform <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="secondary" asChild>
                <Link href="/copilot">Meet MediClaim Copilot</Link>
              </Button>
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                Accessibility and audit-first by design
              </div>
            </div>

            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              {landingStats.map((stat) => (
                <Card key={stat.label} className="glass rounded-3xl border-0">
                  <CardHeader className="pb-2">
                    <CardDescription>{stat.label}</CardDescription>
                    <CardTitle className="text-3xl">{stat.value}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm text-slate-500 dark:text-slate-300">
                    {stat.description}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          <HeroVisual />
        </div>

        <section id="features" className="grid gap-6 py-8 lg:grid-cols-3">
          {productCapabilities.map((item) => (
            <Card key={item.title} className="glass rounded-3xl border-0">
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-100 text-sky-700 dark:bg-sky-400/15 dark:text-sky-200">
                  <item.icon className="h-5 w-5" />
                </div>
                <CardTitle>{item.title}</CardTitle>
                <CardDescription className="text-base leading-7">{item.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </section>

        <section id="workflow" className="py-16">
          <div className="mb-8 max-w-2xl">
            <Badge variant="outline" className="border-sky-200 bg-white/80 text-sky-700 dark:border-sky-400/20 dark:bg-slate-900/80 dark:text-sky-200">
              Product flow
            </Badge>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
              Hospital records
              <span className="mx-2 text-slate-400">→</span>
              AI standardization
              <span className="mx-2 text-slate-400">→</span>
              ISCS
              <span className="mx-2 text-slate-400">→</span>
              claim readiness
            </h2>
          </div>
          <div className="grid gap-4 lg:grid-cols-4">
            {workflowSteps.map((step, index) => (
              <Card key={step.title} className="glass rounded-3xl border-0">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <Badge className="rounded-full bg-sky-100 text-sky-700 dark:bg-sky-400/10 dark:text-sky-200">
                      Step {index + 1}
                    </Badge>
                    <BadgeCheck className="h-4 w-4 text-emerald-500" />
                  </div>
                  <CardTitle className="mt-4">{step.title}</CardTitle>
                  <CardDescription className="text-base leading-7">{step.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </section>

        <section className="grid gap-6 py-8 lg:grid-cols-[1.1fr_0.9fr]">
          <Card className="glass rounded-3xl border-0 p-0">
            <CardHeader className="border-b border-white/50 p-6 dark:border-white/5">
              <Badge variant="outline" className="w-fit">
                ROI calculator
              </Badge>
              <CardTitle className="mt-4 text-2xl">A single claim analyst can process more hospitals per shift.</CardTitle>
              <CardDescription className="text-base leading-7">
                Use AI extraction and validation to reduce manual review time, improve documentation completeness,
                and surface issues before the insurer sees them.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4 p-6 sm:grid-cols-3">
              {[
                ["65%", "less manual triage"],
                ["3.2x", "faster claim prep"],
                ["18%", "higher first-pass acceptance"],
              ].map(([value, label]) => (
                <div key={label} className="rounded-2xl bg-slate-950 p-5 text-white shadow-lg dark:bg-white dark:text-slate-950">
                  <p className="text-3xl font-semibold">{value}</p>
                  <p className="mt-2 text-sm text-slate-300 dark:text-slate-600">{label}</p>
                </div>
              ))}
            </CardContent>
          </Card>
          <Card className="glass rounded-3xl border-0">
            <CardHeader>
              <Badge variant="outline" className="w-fit">
                Trusted by every role
              </Badge>
              <CardTitle className="mt-4 text-2xl">Role-based permissions for hospitals, TPAs, and insurers.</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                "Hospital Admin",
                "Doctor",
                "Medical Coder",
                "Insurance Reviewer",
                "TPA Executive",
                "Super Admin",
              ].map((role) => (
                <div key={role} className="flex items-center justify-between rounded-2xl border border-slate-200/70 bg-white/80 px-4 py-3 text-sm dark:border-white/10 dark:bg-white/5">
                  <span>{role}</span>
                  <span className="text-sky-600 dark:text-sky-300">Permissioned</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </section>

        <section id="pricing" className="py-12">
          <h2 className="text-3xl font-semibold tracking-tight">Enterprise pricing</h2>
          <div className="mt-6 grid gap-6 lg:grid-cols-3">
            {pricingPlans.map((plan) => (
              <Card key={plan.name} className={`rounded-3xl border-0 ${plan.featured ? "glass-strong" : "glass"}`}>
                <CardHeader>
                  <Badge className="w-fit">{plan.name}</Badge>
                  <CardTitle className="mt-4 text-2xl">{plan.price}</CardTitle>
                  <CardDescription className="text-base leading-7">{plan.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3 text-sm text-slate-600 dark:text-slate-300">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3">
                        <ShieldCheck className="mt-0.5 h-4 w-4 text-emerald-500" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section className="grid gap-6 py-12 lg:grid-cols-2">
          {testimonials.map((item) => (
            <Card key={item.name} className="glass rounded-3xl border-0">
              <CardHeader>
                <CardDescription className="text-base leading-7">{item.quote}</CardDescription>
                <CardTitle className="mt-4 text-lg">{item.name}</CardTitle>
                <CardDescription>{item.title}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </section>

        <section id="faq" className="py-12">
          <h2 className="text-3xl font-semibold tracking-tight">Frequently asked questions</h2>
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            {faqs.map((faq) => (
              <Card key={faq.question} className="glass rounded-3xl border-0">
                <CardHeader>
                  <CardTitle className="text-lg">{faq.question}</CardTitle>
                  <CardDescription className="text-base leading-7">{faq.answer}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </section>

        <section id="contact" className="py-12">
          <Card className="glass rounded-3xl border-0">
            <CardHeader>
              <Badge variant="outline" className="w-fit">
                Contact
              </Badge>
              <CardTitle className="mt-4 text-3xl">Talk to our healthcare transformation team</CardTitle>
              <CardDescription className="text-base leading-7">
                Share your current documentation volume, insurer network, and turnaround goals. We will map a deployment plan for your hospitals and TPA operations.
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl bg-white/90 p-5 text-sm dark:bg-white/5">
                <p className="font-medium">Email</p>
                <p className="mt-1 text-slate-500 dark:text-slate-300">hello@mediclaim.ai</p>
              </div>
              <div className="rounded-2xl bg-white/90 p-5 text-sm dark:bg-white/5">
                <p className="font-medium">Sales</p>
                <p className="mt-1 text-slate-500 dark:text-slate-300">+91 80 4000 2200</p>
              </div>
              <div className="rounded-2xl bg-white/90 p-5 text-sm dark:bg-white/5">
                <p className="font-medium">HQ</p>
                <p className="mt-1 text-slate-500 dark:text-slate-300">Bengaluru, India</p>
              </div>
            </CardContent>
          </Card>
        </section>

        <section className="py-10">
          <div className="glass-strong flex flex-col items-start justify-between gap-6 rounded-[2rem] px-8 py-10 lg:flex-row lg:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-sky-700 dark:text-sky-300">
                Ready for deployment
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight">Start with the dashboard, copilot, and claim workflow.</h2>
            </div>
            <div className="flex gap-3">
              <Button variant="secondary" asChild>
                <Link href="/dashboard">View demo dashboards</Link>
              </Button>
              <Button asChild>
                <Link href="/copilot">Open MediClaim Copilot</Link>
              </Button>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
