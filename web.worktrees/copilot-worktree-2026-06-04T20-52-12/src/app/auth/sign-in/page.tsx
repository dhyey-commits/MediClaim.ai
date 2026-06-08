"use client";

import { FormEvent, useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const demoRoles = [
  "Hospital Admin",
  "Doctor",
  "Medical Coder",
  "Insurance Reviewer",
  "TPA Executive",
  "Super Admin",
];

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@mediclaim.ai");
  const [role, setRole] = useState(demoRoles[0]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    const result = await signIn("credentials", {
      redirect: false,
      email,
      role,
    });
    setLoading(false);
    if (!result?.error) {
      router.push("/dashboard");
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-xl items-center px-4 py-10 sm:px-6">
      <Card className="glass-strong w-full rounded-[2rem] border-0">
        <CardHeader>
          <Badge variant="outline" className="w-fit">
            Auth.js
          </Badge>
          <CardTitle className="mt-4 text-3xl">Sign in to MediClaim AI</CardTitle>
          <CardDescription className="text-base leading-7">
            Demo login with role-based identity for hospital, coding, insurer, and admin workflows.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <label className="block text-sm">
              <span className="mb-2 block text-slate-600 dark:text-slate-300">Email</span>
              <input
                className="w-full rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm dark:border-white/10 dark:bg-white/5"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                type="email"
                required
              />
            </label>
            <label className="block text-sm">
              <span className="mb-2 block text-slate-600 dark:text-slate-300">Role</span>
              <select
                className="w-full rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm dark:border-white/10 dark:bg-white/5"
                value={role}
                onChange={(event) => setRole(event.target.value)}
              >
                {demoRoles.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <Button className="w-full" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
