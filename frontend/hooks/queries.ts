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

export function useSuggestIcd(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.claims.suggestIcd(claimId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId, "icd"] });
      qc.invalidateQueries({ queryKey: ["claims", claimId, "audit"] });
    },
  });
}

export function useIcdRecommendations(claimId: string) {
  return useQuery({
    queryKey: ["claims", claimId, "icd"],
    queryFn: () => api.claims.getIcd(claimId),
    enabled: !!claimId,
  });
}

export function useAcceptIcd(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (recId: string) => api.claims.acceptIcd(claimId, recId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId, "icd"] });
      qc.invalidateQueries({ queryKey: ["claims", claimId, "audit"] });
    },
  });
}

export function useRejectIcd(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (recId: string) => api.claims.rejectIcd(claimId, recId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId, "icd"] });
      qc.invalidateQueries({ queryKey: ["claims", claimId, "audit"] });
    },
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

export function useStartReview(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.claims.startReview(claimId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId] });
    },
  });
}

export function useUpdateReview(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Parameters<typeof api.claims.updateReview>[1]) => api.claims.updateReview(claimId, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId, "extraction"] });
      qc.invalidateQueries({ queryKey: ["claims", claimId] });
    },
  });
}

export function useApproveClaim(claimId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.claims.approveClaim(claimId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["claims", claimId, "extraction"] });
      qc.invalidateQueries({ queryKey: ["claims", claimId] });
      qc.invalidateQueries({ queryKey: ["claims", claimId, "audit"] });
    },
  });
}

export function useClaimAudit(claimId: string) {
  return useQuery({
    queryKey: ["claims", claimId, "audit"],
    queryFn: () => api.claims.getAudit(claimId),
    enabled: !!claimId,
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
