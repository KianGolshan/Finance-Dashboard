"use client";

import { useState } from "react";
import { useApi } from "@/hooks/useApi";
import { portfolio, monitoring } from "@/lib/api";
import { formatCurrency, formatDate, sectorLabel } from "@/lib/utils";
import MetricCard from "@/components/ui/MetricCard";
import DataTable from "@/components/ui/DataTable";
import Modal from "@/components/ui/Modal";
import { Activity, TrendingUp, BarChart3, Plus } from "lucide-react";
import type { Company, Scenario, PortfolioSummary } from "@/lib/types";

export default function MonitoringPage() {
  const { data: summary } = useApi<PortfolioSummary>(() => portfolio.getSummary());
  const { data: companiesData } = useApi<{ companies: Company[]; total: number }>(
    () => portfolio.listCompanies()
  );
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [showScenario, setShowScenario] = useState(false);
  const [scenarioForm, setScenarioForm] = useState({
    name: "",
    base_revenue: "",
    revenue_growth: "0.15",
    ebitda_margin: "0.25",
    exit_multiple: "12",
    projection_years: "5",
    initial_investment: "",
    ownership_pct: "1.0",
  });
  const { data: scenarios, refetch: refetchScenarios } = useApi<Scenario[]>(
    () => selectedCompany ? monitoring.listScenarios(selectedCompany) : Promise.resolve([]),
    [selectedCompany]
  );

  const companies = companiesData?.companies || [];

  const handleCreateScenario = async () => {
    if (!selectedCompany) return;
    await monitoring.createScenario({
      company_id: selectedCompany,
      name: scenarioForm.name,
      assumptions: {
        base_revenue: parseFloat(scenarioForm.base_revenue),
        revenue_growth: parseFloat(scenarioForm.revenue_growth),
        ebitda_margin: parseFloat(scenarioForm.ebitda_margin),
        exit_multiple: parseFloat(scenarioForm.exit_multiple),
        projection_years: parseInt(scenarioForm.projection_years),
        initial_investment: parseFloat(scenarioForm.initial_investment),
        ownership_pct: parseFloat(scenarioForm.ownership_pct),
      },
    });
    setShowScenario(false);
    refetchScenarios();
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Portfolio Monitoring</h1>
          <p className="text-sm text-slate-500 mt-1">Track KPIs and run scenario analyses</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <MetricCard title="Active Companies" value={String(summary?.active_companies || 0)} icon={Activity} />
        <MetricCard title="Total NAV" value={formatCurrency(summary?.total_nav || 0)} icon={TrendingUp} />
        <MetricCard title="Gross MOIC" value={`${(summary?.gross_moic || 0).toFixed(2)}x`} icon={BarChart3} />
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-5">
          <div className="card">
            <div className="card-header flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-700">Companies</h2>
            </div>
            <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
              {companies.map((c) => (
                <button
                  key={c.id}
                  onClick={() => setSelectedCompany(c.id)}
                  className={`w-full px-4 py-3 text-left transition-colors hover:bg-slate-50 ${
                    selectedCompany === c.id ? "bg-brand-50 border-l-2 border-brand-500" : ""
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-900">{c.name}</p>
                      <p className="text-xs text-slate-400">{sectorLabel(c.sector)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-slate-900">{formatCurrency(c.current_valuation)}</p>
                      <p className={`text-xs font-medium ${c.moic >= 1 ? "text-emerald-600" : "text-red-600"}`}>{c.moic.toFixed(2)}x</p>
                    </div>
                  </div>
                </button>
              ))}
              {companies.length === 0 && (
                <p className="p-6 text-sm text-slate-400 text-center">No companies to monitor</p>
              )}
            </div>
          </div>
        </div>

        <div className="col-span-7 space-y-6">
          {selectedCompany ? (
            <>
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-900">Scenario Analysis</h2>
                <button onClick={() => setShowScenario(true)} className="btn-primary text-sm">
                  <Plus className="h-4 w-4" /> New Scenario
                </button>
              </div>
              <DataTable
                columns={[
                  { key: "name", header: "Scenario", render: (s: Scenario) => <span className="font-medium">{s.name}</span> },
                  { key: "moic", header: "MOIC", render: (s: Scenario) => (
                    <span className="font-semibold">{s.results?.moic?.toFixed(2) || "—"}x</span>
                  ), className: "text-right" },
                  { key: "irr", header: "IRR", render: (s: Scenario) => (
                    <span>{s.results?.irr ? `${(s.results.irr * 100).toFixed(1)}%` : "—"}</span>
                  ), className: "text-right" },
                  { key: "exit_ev", header: "Exit EV", render: (s: Scenario) => (
                    formatCurrency(s.results?.exit_enterprise_value || 0)
                  ), className: "text-right" },
                  { key: "created_at", header: "Created", render: (s: Scenario) => formatDate(s.created_at) },
                ]}
                data={scenarios || []}
                emptyMessage="No scenarios yet. Create one to model outcomes."
              />
            </>
          ) : (
            <div className="card p-12 text-center">
              <p className="text-slate-400">Select a company to view scenarios and metrics</p>
            </div>
          )}
        </div>
      </div>

      <Modal open={showScenario} onClose={() => setShowScenario(false)} title="Create Scenario" wide>
        <div className="space-y-4">
          <div>
            <label className="label">Scenario Name</label>
            <input className="input" value={scenarioForm.name}
              onChange={(e) => setScenarioForm({ ...scenarioForm, name: e.target.value })}
              placeholder="e.g. Base Case, Upside, Downside" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Base Revenue ($)</label>
              <input className="input" type="number" value={scenarioForm.base_revenue}
                onChange={(e) => setScenarioForm({ ...scenarioForm, base_revenue: e.target.value })} />
            </div>
            <div>
              <label className="label">Revenue Growth Rate</label>
              <input className="input" type="number" step="0.01" value={scenarioForm.revenue_growth}
                onChange={(e) => setScenarioForm({ ...scenarioForm, revenue_growth: e.target.value })} />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">EBITDA Margin</label>
              <input className="input" type="number" step="0.01" value={scenarioForm.ebitda_margin}
                onChange={(e) => setScenarioForm({ ...scenarioForm, ebitda_margin: e.target.value })} />
            </div>
            <div>
              <label className="label">Exit Multiple</label>
              <input className="input" type="number" step="0.5" value={scenarioForm.exit_multiple}
                onChange={(e) => setScenarioForm({ ...scenarioForm, exit_multiple: e.target.value })} />
            </div>
            <div>
              <label className="label">Projection Years</label>
              <input className="input" type="number" value={scenarioForm.projection_years}
                onChange={(e) => setScenarioForm({ ...scenarioForm, projection_years: e.target.value })} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Initial Investment ($)</label>
              <input className="input" type="number" value={scenarioForm.initial_investment}
                onChange={(e) => setScenarioForm({ ...scenarioForm, initial_investment: e.target.value })} />
            </div>
            <div>
              <label className="label">Ownership %</label>
              <input className="input" type="number" step="0.01" value={scenarioForm.ownership_pct}
                onChange={(e) => setScenarioForm({ ...scenarioForm, ownership_pct: e.target.value })} />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button className="btn-secondary" onClick={() => setShowScenario(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleCreateScenario} disabled={!scenarioForm.name}>
              Run Scenario
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
