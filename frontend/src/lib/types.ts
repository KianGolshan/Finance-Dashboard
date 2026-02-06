export interface Fund {
  id: string;
  name: string;
  vintage_year: number;
  strategy: string;
  aum: number | null;
  currency: string;
  status: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  company_count: number;
  total_invested: number;
  total_value: number;
}

export interface Company {
  id: string;
  fund_id: string;
  name: string;
  sector: string;
  geography: string;
  investment_date: string;
  exit_date: string | null;
  initial_investment: number;
  current_valuation: number;
  ownership_pct: number;
  currency: string;
  status: string;
  description: string | null;
  moic: number;
  created_at: string;
  updated_at: string;
}

export interface FinancialMetric {
  id: string;
  company_id: string;
  period_date: string;
  metric_type: string;
  value: number;
  currency: string;
  source: string;
  notes: string | null;
  created_at: string;
}

export interface Document {
  id: string;
  company_id: string | null;
  filename: string;
  file_type: string;
  file_size: number;
  document_type: string | null;
  processing_status: string;
  extracted_data: Record<string, any> | null;
  page_count: number | null;
  error_message: string | null;
  upload_date: string;
  extraction_count: number;
}

export interface Extraction {
  id: string;
  document_id: string;
  field_name: string;
  field_value: string;
  field_type: string;
  confidence_score: number;
  extraction_method: string;
  page_number: number | null;
  context_snippet: string | null;
  validated: boolean;
  validated_by: string | null;
  created_at: string;
}

export interface Valuation {
  id: string;
  company_id: string;
  valuation_date: string;
  method: string;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  enterprise_value: number | null;
  equity_value: number | null;
  implied_multiple: number | null;
  currency: string;
  status: string;
  notes: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Scenario {
  id: string;
  company_id: string;
  name: string;
  description: string | null;
  assumptions: Record<string, any>;
  results: Record<string, any>;
  created_by: string;
  created_at: string;
}

export interface Report {
  id: string;
  name: string;
  report_type: string;
  entity_id: string | null;
  entity_type: string | null;
  parameters: Record<string, any>;
  output_path: string | null;
  output_format: string;
  status: string;
  error_message: string | null;
  created_by: string;
  created_at: string;
}

export interface AuditLog {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  changes: Record<string, any>;
  user_id: string;
  timestamp: string;
}

export interface PortfolioSummary {
  total_nav: number;
  total_invested: number;
  total_realized: number;
  unrealized_gain: number;
  gross_moic: number;
  fund_count: number;
  company_count: number;
  active_companies: number;
  sector_breakdown: Array<{ sector: string; count: number; value: number }>;
  geography_breakdown: Array<{ geography: string; count: number; value: number }>;
  vintage_breakdown: Array<{ vintage_year: number; count: number; value: number }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}
