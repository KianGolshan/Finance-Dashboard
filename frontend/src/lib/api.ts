const BASE_URL = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Portfolio
export const portfolio = {
  getSummary: () => request<any>("/portfolio/summary"),
  listFunds: (skip = 0, limit = 50) => request<any>(`/portfolio/funds?skip=${skip}&limit=${limit}`),
  getFund: (id: string) => request<any>(`/portfolio/funds/${id}`),
  createFund: (data: any) => request<any>("/portfolio/funds", { method: "POST", body: JSON.stringify(data) }),
  updateFund: (id: string, data: any) => request<any>(`/portfolio/funds/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteFund: (id: string) => request<void>(`/portfolio/funds/${id}`, { method: "DELETE" }),

  listCompanies: (params?: { fund_id?: string; status?: string; skip?: number; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.fund_id) qs.set("fund_id", params.fund_id);
    if (params?.status) qs.set("status", params.status);
    qs.set("skip", String(params?.skip ?? 0));
    qs.set("limit", String(params?.limit ?? 50));
    return request<any>(`/portfolio/companies?${qs}`);
  },
  getCompany: (id: string) => request<any>(`/portfolio/companies/${id}`),
  createCompany: (data: any) => request<any>("/portfolio/companies", { method: "POST", body: JSON.stringify(data) }),
  updateCompany: (id: string, data: any) => request<any>(`/portfolio/companies/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

// Documents
export const documents = {
  list: (params?: { company_id?: string; status?: string }) => {
    const qs = new URLSearchParams();
    if (params?.company_id) qs.set("company_id", params.company_id);
    if (params?.status) qs.set("status", params.status);
    return request<any>(`/documents?${qs}`);
  },
  get: (id: string) => request<any>(`/documents/${id}`),
  upload: async (file: File, companyId?: string, documentType?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    if (companyId) formData.append("company_id", companyId);
    if (documentType) formData.append("document_type", documentType);
    const res = await fetch(`${BASE_URL}/documents/upload`, { method: "POST", body: formData });
    if (!res.ok) throw new Error("Upload failed");
    return res.json();
  },
  extract: (id: string) => request<any>(`/documents/${id}/extract`, { method: "POST" }),
  getExtractions: (id: string) => request<any>(`/documents/${id}/extractions`),
  validateExtraction: (id: string, data: any) => request<any>(`/documents/extractions/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

// Monitoring
export const monitoring = {
  createMetric: (data: any) => request<any>("/monitoring/metrics", { method: "POST", body: JSON.stringify(data) }),
  listMetrics: (companyId: string, params?: { metric_type?: string }) => {
    const qs = new URLSearchParams();
    if (params?.metric_type) qs.set("metric_type", params.metric_type);
    return request<any>(`/monitoring/metrics/${companyId}?${qs}`);
  },
  getTimeSeries: (companyId: string, metricType: string) =>
    request<any>(`/monitoring/metrics/${companyId}/timeseries?metric_type=${metricType}`),
  createScenario: (data: any) => request<any>("/monitoring/scenarios", { method: "POST", body: JSON.stringify(data) }),
  listScenarios: (companyId: string) => request<any>(`/monitoring/scenarios/${companyId}`),
};

// Valuation
export const valuation = {
  run: (data: any) => request<any>("/valuation/run", { method: "POST", body: JSON.stringify(data) }),
  list: (companyId?: string) => {
    const qs = companyId ? `?company_id=${companyId}` : "";
    return request<any>(`/valuation${qs}`);
  },
  get: (id: string) => request<any>(`/valuation/${id}`),
  addOverride: (id: string, data: any) => request<any>(`/valuation/${id}/overrides`, { method: "POST", body: JSON.stringify(data) }),
};

// Reports
export const reports = {
  create: (data: any) => request<any>("/reports", { method: "POST", body: JSON.stringify(data) }),
  list: () => request<any>("/reports"),
  get: (id: string) => request<any>(`/reports/${id}`),
  getAuditLog: (params?: { entity_type?: string; entity_id?: string }) => {
    const qs = new URLSearchParams();
    if (params?.entity_type) qs.set("entity_type", params.entity_type);
    if (params?.entity_id) qs.set("entity_id", params.entity_id);
    return request<any>(`/reports/audit-log?${qs}`);
  },
};
