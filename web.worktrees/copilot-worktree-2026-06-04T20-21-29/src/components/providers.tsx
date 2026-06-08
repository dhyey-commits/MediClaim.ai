"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient());
  const ThemeProviderAny = ThemeProvider as unknown as React.ComponentType<{
    attribute?: string;
    defaultTheme?: string;
    enableSystem?: boolean;
    children: React.ReactNode;
  }>;

  return (
    <ThemeProviderAny attribute="data-theme" defaultTheme="light" enableSystem={false}>
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    </ThemeProviderAny>
  );
}