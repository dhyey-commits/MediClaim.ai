import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json"
  }
});

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: any = {},
): Promise<T> {
  try {
    const res = await apiClient({
      url: path,
      method: options.method || "GET",
      data: options.body ? (typeof options.body === "string" ? JSON.parse(options.body) : options.body) : undefined,
      headers: options.headers,
    });
    return res.data;
  } catch (error: any) {
    if (error.response) {
      throw new ApiError(error.response.status, error.response.data?.detail || `HTTP ${error.response.status}`);
    }
    throw error;
  }
}

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────

export interface ClaimListItem {
  id: string;
  claim_number: string;
  patient_name: string | null;
  status: string;
  document_count: number;
  created_at: string;
}

export interface DocumentOut {
  id: string;
  file_name: string;
  file_type: string | null;
  file_size: number | null;
  status: string;
  confidence_score: number;
  created_at: string;
}

export interface DiagnosisOut {
  id: string;
  description: string;
  icd_code: string | null;
  icd_description: string | null;
  confidence: number;
  is_primary: boolean;
  is_manually_overridden: boolean;
}

export interface ExtractedEntityOut {
  id: string;
  entity_type: string;
  value: string;
  confidence: number;
}

export interface ReportOut {
  id: string;
  report_type: string;
  is_generated: boolean;
  created_at: string;
}

export interface ClaimDetail {
  id: string;
  claim_number: string;
  patient_name: string | null;
  patient_age: number | null;
  patient_gender: string | null;
  patient_uhid: string | null;
  admission_date: string | null;
  discharge_date: string | null;
  chief_complaint: string | null;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  documents: DocumentOut[];
  diagnoses?: DiagnosisOut[];
  extracted_entities?: ExtractedEntityOut[];
  report?: ReportOut | null;
}

export interface OCRResultOut {
  document_id: string;
  page_number: number;
  raw_text: string;
  status: string;
}

export interface ExtractionResultOut {
  id: string;
  claim_id: string;
  patient_name: string | null;
  age: string | null;
  gender: string | null;
  admission_date: string | null;
  discharge_date: string | null;
  chief_complaint: string | null;
  diagnosis_json: any[] | null;
  procedures_json: any[] | null;
  medications_json: any[] | null;
  investigations_json: any[] | null;
  confidence_score: number;
  is_approved: boolean;
}

export interface DocumentDetail {
  id: string;
  claim_id: string;
  claim_number: string | null;
  file_name: string;
  file_type: string | null;
  file_size: number | null;
  status: string;
  extracted_text: string | null;
  confidence_score: number;
  page_count: number;
  created_at: string;
}

export interface ReportListItem {
  id: string;
  claim_id: string;
  claim_number: string | null;
  patient_name: string | null;
  report_type: string;
  is_generated: boolean;
  created_at: string;
}

export interface ReportDetail extends ReportListItem {
  report_data: Record<string, unknown> | null;
  version: number;
}

export interface AnalyticsOverview {
  total_claims: number;
  claims_processed: number;
  reports_generated: number;
  total_documents: number;
  average_processing_time_minutes: number;
  approval_rate: number;
  fraud_alerts: number;
  status_breakdown: Record<string, number>;
  recent_claims: ClaimListItem[];
}

// ─────────────────────────────────────────────
// Claims
// ─────────────────────────────────────────────

export const api = {
  claims: {
    list: () => request<ClaimListItem[]>("/claims"),
    create: (body: { patient_name?: string; notes?: string }) =>
      request<{ id: string; claim_number: string; status: string }>("/claims", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    get: (id: string) => request<ClaimDetail>(`/claims/${id}`),
    upload: async (id: string, files: File[]) => {
      const form = new FormData();
      files.forEach((f) => form.append("files", f));
      try {
        const res = await apiClient.post(`/claims/${id}/upload`, form, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        return res.data;
      } catch (error: any) {
        if (error.response) {
          throw new ApiError(error.response.status, error.response.data?.detail || "Upload failed");
        }
        throw error;
      }
    },
    extract: (id: string) =>
      request<{
        claim_id: string;
        status: string;
        patient_name: string;
        entities_extracted: number;
        confidence_scores: Record<string, number>;
      }>(`/claims/${id}/extract`, { method: "POST" }),
    icdMap: (id: string) =>
      request<{
        claim_id: string;
        status: string;
        mappings: { diagnosis: string; icd_code: string; confidence: number }[];
      }>(`/claims/${id}/icd-map`, { method: "POST" }),
    generateReport: (id: string) =>
      request<{
        claim_id: string;
        report_id: string;
        status: string;
        pdf_size_kb: number;
      }>(`/claims/${id}/generate-report`, { method: "POST" }),
    overrideIcd: (claimId: string, diagnosisId: string, icdCode: string) =>
      request(`/claims/${claimId}/diagnoses/${diagnosisId}/override`, {
        method: "PATCH",
        body: JSON.stringify({ icd_code: icdCode }),
      }),
    triggerOcr: (id: string) =>
      request<{ message: string; status: string }>(`/claims/${id}/ocr`, { method: "POST" }),
    getOcrResults: (id: string) => request<OCRResultOut[]>(`/claims/${id}/ocr`),
    triggerExtraction: (id: string) =>
      request<{ message: string; status: string }>(`/claims/${id}/extract`, { method: "POST" }),
    getExtraction: (id: string) => request<ExtractionResultOut>(`/claims/${id}/extraction`),
    updateExtraction: (id: string, body: Partial<ExtractionResultOut>) =>
      request<ExtractionResultOut>(`/claims/${id}/extraction`, { method: "PATCH", body: JSON.stringify(body) }),
  },

  documents: {
    list: () => request<DocumentDetail[]>("/documents"),
    get: (id: string) => request<DocumentDetail>(`/documents/${id}`),
  },

  reports: {
    list: () => request<ReportListItem[]>("/reports"),
    get: (id: string) => request<ReportDetail>(`/reports/${id}`),
    downloadUrl: (id: string) => `${API_BASE}/reports/${id}/download`,
  },

  analytics: {
    overview: () => request<AnalyticsOverview>("/analytics/overview"),
  },
};
