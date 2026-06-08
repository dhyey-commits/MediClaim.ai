"use client";

import { FormEvent, useMemo, useState } from "react";
import { Bot, SendHorizonal, Sparkles } from "lucide-react";
import { copilotThreads } from "@/lib/mock-data";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function CopilotPage() {
  const [messages, setMessages] = useState(copilotThreads);
  const [prompt, setPrompt] = useState("");
  const [sending, setSending] = useState(false);
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

  const canSend = useMemo(() => prompt.trim().length > 0 && !sending, [prompt, sending]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = prompt.trim();
    if (!content) {
      return;
    }
    setPrompt("");
    setSending(true);
    setMessages((prev) => [...prev, { role: "User", message: content }]);
    try {
      const response = await fetch(`${apiBase}/copilot/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content, context: { source: "web-copilot" } }),
      });
      const data = response.ok ? await response.json() : null;
      const reply = data?.message || "I can help summarize this case and suggest missing evidence for claim readiness.";
      setMessages((prev) => [...prev, { role: "MediClaim Copilot", message: reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: "MediClaim Copilot", message: "Connection issue detected. I can still guide coding, validation, and insurer notes locally." }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card className="glass-strong rounded-[2rem] border-0">
          <CardHeader>
            <Badge variant="outline" className="w-fit">
              MediClaim Copilot
            </Badge>
            <CardTitle className="mt-4 text-3xl">Clinical claim assistant</CardTitle>
            <CardDescription className="text-base leading-7">
              Explain ICD codes, suggest missing documents, summarize records, and clarify rejection reasons.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              "Explain ICD-10 code meaning",
              "Find missing evidence",
              "Draft insurer summary",
              "Summarize discharge note",
            ].map((item) => (
              <div key={item} className="rounded-2xl border border-slate-200/70 bg-white/80 px-4 py-3 text-sm dark:border-white/10 dark:bg-white/5">
                {item}
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="glass-strong min-h-[72vh] rounded-[2rem] border-0">
          <CardHeader className="border-b border-white/40 dark:border-white/5">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-600 text-white">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <CardTitle>MediClaim Copilot</CardTitle>
                <CardDescription>ChatGPT-style clinical workflow assistant</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex min-h-[60vh] flex-col gap-4 p-6">
            <div className="flex-1 space-y-4 rounded-3xl bg-slate-50/80 p-5 dark:bg-white/5">
              {messages.map((item, index) => (
                <div key={index} className={`flex ${index % 2 === 0 ? "justify-start" : "justify-end"}`}>
                  <div className={`max-w-2xl rounded-3xl px-4 py-3 text-sm leading-6 ${index % 2 === 0 ? "bg-white text-slate-700 dark:bg-slate-900 dark:text-slate-100" : "bg-sky-600 text-white"}`}>
                    <p className="mb-1 text-xs font-semibold uppercase tracking-[0.24em] opacity-70">{item.role}</p>
                    {item.message}
                  </div>
                </div>
              ))}
            </div>
            <form onSubmit={onSubmit} className="rounded-3xl border border-slate-200/70 bg-white/90 p-4 dark:border-white/10 dark:bg-slate-950/70">
              <div className="flex items-center gap-3">
                <Sparkles className="h-4 w-4 text-sky-600 dark:text-sky-300" />
                <p className="text-sm text-slate-500 dark:text-slate-300">Ask about ICD codes, missing documents, or insurer notes.</p>
              </div>
              <div className="mt-3 flex items-center gap-3">
                <input
                  className="flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:border-white/10 dark:bg-white/5 dark:text-slate-300"
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Ask MediClaim Copilot anything about the record..."
                />
                <Button className="rounded-2xl px-5" type="submit" disabled={!canSend}>
                  <SendHorizonal className="mr-2 h-4 w-4" />
                  {sending ? "Sending" : "Send"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
