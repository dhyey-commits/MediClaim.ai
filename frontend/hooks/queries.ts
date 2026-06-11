/**
 * React Query hooks — every page uses these, no raw fetches in components.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api";

// ─────────────────────────────────────────────
// Dashboard
// ─────────────────────────────────────────────
export function useAnalytics() {
  return useQuery({
    queryKey: ["analytics"],
    queryFn: api.analytics.overview,
    refetchInterval: 30_000,
  });
}

// ─────────────────────────────────────────────
// Claims
// ─────────────────────────────────────────────
export function useClaims() {
  return useQuery({
    queryKey: ["claims"],
    queryFn: api.claims.list,
  });
}

export function useClaim(id: string) {
  return useQuery({
    queryKey: ["claims", id],
    queryFn: () => api.claims.get(id),
    enabled: !!id,
  });
}

export function useCreateClaim() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.claims.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["claims"] }),
  });
}

export function useUploadDocuments(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (files: File[]) => api.claims.upload(claimId, files),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId] });
      qc.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}

export function useTriggerOcr(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.claims.triggerOcr(claimId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["claims", claimId] }),
  });
}

export function useOcrResults(claimId: string) {
  return useQuery({
    queryKey: ["claims", claimId, "ocr"],
    queryFn: () => api.claims.getOcrResults(claimId),
    enabled: !!claimId,
  });
}

export function useTriggerExtraction(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.claims.triggerExtraction(claimId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["claims", claimId] }),
  });
}

export function useExtractionResult(claimId: string) {
  return useQuery({
    queryKey: ["claims", claimId, "extraction"],
    queryFn: () => api.claims.getExtraction(claimId),
    enabled: !!claimId,
  });
}

export function useUpdateExtraction(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Parameters<typeof api.claims.updateExtraction>[1]) => api.claims.updateExtraction(claimId, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId, "extraction"] });
      qc.invalidateQueries({ queryKey: ["claims", claimId] });
    },
  });
}

export function useIcdMap(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.claims.icdMap(claimId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["claims", claimId] }),
  });
}

export function useGenerateReport(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.claims.generateReport(claimId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId] });
      qc.invalidateQueries({ queryKey: ["reports"] });
    },
  });
}

export function useOverrideIcd(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ diagnosisId, icdCode }: { diagnosisId: string; icdCode: string }) =>
      api.claims.overrideIcd(claimId, diagnosisId, icdCode),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["claims", claimId] }),
  });
}

// ─────────────────────────────────────────────
// Documents
// ─────────────────────────────────────────────
export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: api.documents.list,
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: ["documents", id],
    queryFn: () => api.documents.get(id),
    enabled: !!id,
  });
}

// ─────────────────────────────────────────────
// Reports
// ─────────────────────────────────────────────
export function useReports() {
  return useQuery({
    queryKey: ["reports"],
    queryFn: api.reports.list,
  });
}

export function useReport(id: string) {
  return useQuery({
    queryKey: ["reports", id],
    queryFn: () => api.reports.get(id),
    enabled: !!id,
  });
}
