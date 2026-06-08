import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function formatConfidence(score: number): string {
  return `${Math.round(score * 100)}%`;
}

export const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Draft",
  DOCUMENT_UPLOADED: "Uploaded",
  OCR_COMPLETE: "OCR Done",
  EXTRACTION_COMPLETE: "Extracted",
  ICD_MAPPED: "ICD Mapped",
  REPORT_GENERATED: "Report Ready",
};

export const STATUS_BADGE_CLASS: Record<string, string> = {
  DRAFT: "badge badge-draft",
  DOCUMENT_UPLOADED: "badge badge-uploaded",
  OCR_COMPLETE: "badge badge-ocr",
  EXTRACTION_COMPLETE: "badge badge-extraction",
  ICD_MAPPED: "badge badge-icd",
  REPORT_GENERATED: "badge badge-report",
};