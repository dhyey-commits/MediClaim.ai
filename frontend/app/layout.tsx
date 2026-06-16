import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Providers } from "@/components/providers";
import { ClerkAxiosInterceptor } from "@/components/clerk-axios-interceptor";
import { MockAxiosInterceptor } from "@/components/mock-axios-interceptor";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "MediClaim AI | Clinical Documentation Standardization Platform",
  description:
    "Convert Indian hospital discharge summaries into standardized insurance-ready ISCS reports with AI-powered OCR, ICD-10 mapping, and clinical extraction.",
};

function ConditionalClerkProvider({ children }: { children: React.ReactNode }) {
  const hasClerk = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

  if (hasClerk) {
    // Dynamic import to avoid errors when keys aren't set
    const { ClerkProvider } = require("@clerk/nextjs");
    return (
      <ClerkProvider
        publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!}
        signInUrl="/auth/sign-in"
        signUpUrl="/auth/sign-up"
        afterSignInUrl="/dashboard"
        afterSignUpUrl="/dashboard"
      >
        <ClerkAxiosInterceptor>
          {children}
        </ClerkAxiosInterceptor>
      </ClerkProvider>
    );
  }

  return (
    <MockAxiosInterceptor>
      {children}
    </MockAxiosInterceptor>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ConditionalClerkProvider>
      <html lang="en" className={`${inter.variable} h-full`} suppressHydrationWarning>
        <body className="h-full" style={{ background: "#0a0f1e", color: "white" }}>
          <Providers>{children}</Providers>
        </body>
      </html>
    </ConditionalClerkProvider>
  );
}
