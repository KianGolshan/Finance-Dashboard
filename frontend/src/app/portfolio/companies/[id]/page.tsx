"use client";

import { useParams } from "next/navigation";
import { useApi } from "@/hooks/useApi";
import { portfolio, monitoring } from "@/lib/api";
import { formatCurrency, formatMOIC, formatPercent, formatDate, sectorLabel } from "@/lib/utils";
import MetricCard from "@/components/ui/MetricCard";
import StatusBadge from "@/components/ui/StatusBadge";
import { Building2, DollarSign, TrendingUp, Calendar } from "lucide-react";
import type { Company, FinancialMetric } from "@/lib/types";

export default function CompanyDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: company, loading } = useApi<Company>(() => portfolio.getCompany(id), [id]);
  const { data: metricsData } = useApi<{ metrics: FinancialMetric[]; total: number }>(
    () => monitoring.listMetrics(id),
    [id]
  );

  if (loading || !company) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>;
  }

  const metrics = metricsData?.metrics || [];
  const latestMetrics: Record<string, FinancialMetric> = {};
  for (const m of metrics) {
    if (!latestMetrics[m.metric_type] || m.period_date > latestMetrics[m.metric_type].period_date) {
      latestMetrics[m.metric_type] = m;
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900">{company.name}</h1>
            <StatusBadge status={company.status} />
          </div>
          <p className="mt-1 text-sm text-slate-500">
            {sectorLabel(company.sector)} &middot; {company.geography}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard title="Current Valuation" value={formatCurrency(company.current_valuation)} icon={DollarSign} />
        <MetricCard title="Cost Basis" value={formatCurrency(company.initial_investment)} icon={Building2} />
        <MetricCard title="MOIC" value={formatMOIC(company.moic)} icon={TrendingUp}
          change={company.moic > 1 ? company.moic - 1 : -(1 - company.moic)} />
        <MetricCard title="Ownership" value={formatPercent(company.ownership_pct / 100, 1)}
          subtitle={`Invested ${formatDate(company.investment_date)}`} icon={Calendar} />
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-slate-900">Financial Metrics</h2>
        </div>
        <div className="card-body">
          {Object.keys(latestMetrics).length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-400">
              No financial metrics recorded yet. Upload a document or add metrics manually.
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
              {Object.entries(latestMetrics).map(([type, metric]) => (
                <div key={type} className="rounded-lg border border-slate-100 p-4">
                  <p className="text-xs font-medium uppercase text-slate-400">
                    {type.replace(/_/g, " ")}
                  </p>
                  <p className="mt-1 text-lg font-bold text-slate-900">
                    {formatCurrency(metric.value)}
                  </p>
                  <p className="text-xs text-slate-400">{formatDate(metric.period_date)}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {company.description && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-semibold text-slate-900">Investment Thesis</h2>
          </div>
          <div className="card-body">
            <p className="text-sm leading-relaxed text-slate-600">{company.description}</p>
          </div>
        </div>
      )}
    </div>
  );
}
