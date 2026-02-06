"use client";

import { useState } from "react";
import { useApi } from "@/hooks/useApi";
import { portfolio, valuation as valApi } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import DataTable from "@/components/ui/DataTable";
import StatusBadge from "@/components/ui/StatusBadge";
import Modal from "@/components/ui/Modal";
import { Calculator, Plus } from "lucide-react";
import type { Company, Fund, Valuation } from "@/lib/types";

export default function ValuationPage() {
  const { data: companiesData } = useApi<{ companies: Company[]; total: number }>(
    () => portfolio.listCompanies()
  );
  const { data: valuationsData, refetch } = useApi<{ valuations: Valuation[]; total: number }>(
    () => valApi.list()
  );
  const [showCreate, setShowCreate] = useState(false);
  const [showDetail, setShowDetail] = useState<Valuation | null>(null);
  const [form, setForm] = useState({
    company_id: "",
    valuation_date: new Date().toISOString().split("T")[0],
    method: "dcf",
    base_revenue: "",
    base_ebitda: "",
    discount_rate: "0.10",
    terminal_growth_rate: "0.025",
    projection_years: "5",
    revenue_growth: "0.10,0.10,0.08,0.08,0.06",
    ebitda_margins: "0.25,0.26,0.27,0.28,0.28",
    net_debt: "0",
  });

  const companies = companiesData?.companies || [];
  const valuations = valuationsData?.valuations || [];

  const companyMap = new Map(companies.map((c) => [c.id, c.name]));

  const handleRun = async () => {
    const inputs: Record<string, any> = {};
    if (form.method === "dcf") {
      inputs.base_revenue = parseFloat(form.base_revenue);
      inputs.base_ebitda = parseFloat(form.base_ebitda);
      inputs.discount_rate = parseFloat(form.discount_rate);
      inputs.terminal_growth_rate = parseFloat(form.terminal_growth_rate);
      inputs.projection_years = parseInt(form.projection_years);
      inputs.revenue_growth_rates = form.revenue_growth.split(",").map(Number);
      inputs.ebitda_margins = form.ebitda_margins.split(",").map(Number);
      inputs.net_debt = parseFloat(form.net_debt);
    }
    await valApi.run({
      company_id: form.company_id,
      valuation_date: form.valuation_date,
      method: form.method,
      inputs,
    });
    setShowCreate(false);
    refetch();
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Valuation Workspace</h1>
          <p className="text-sm text-slate-500 mt-1">Run DCF, comps, and sensitivity analyses</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          <Calculator className="h-4 w-4" /> New Valuation
        </button>
      </div>

      <DataTable
        columns={[
          { key: "company", header: "Company", render: (v: Valuation) => (
            <span className="font-medium">{companyMap.get(v.company_id) || v.company_id.slice(0, 8)}</span>
          )},
          { key: "valuation_date", header: "Date", render: (v: Valuation) => formatDate(v.valuation_date) },
          { key: "method", header: "Method", render: (v: Valuation) => (
            <span className="badge bg-indigo-100 text-indigo-800 uppercase text-xs">
              {v.method.replace(/_/g, " ")}
            </span>
          )},
          { key: "enterprise_value", header: "Enterprise Value", render: (v: Valuation) => (
            v.enterprise_value ? formatCurrency(v.enterprise_value) : "—"
          ), className: "text-right font-semibold" },
          { key: "equity_value", header: "Equity Value", render: (v: Valuation) => (
            v.equity_value ? formatCurrency(v.equity_value) : "—"
          ), className: "text-right" },
          { key: "implied_multiple", header: "Implied Multiple", render: (v: Valuation) => (
            v.implied_multiple ? `${v.implied_multiple.toFixed(1)}x` : "—"
          ), className: "text-right" },
          { key: "status", header: "Status", render: (v: Valuation) => <StatusBadge status={v.status} /> },
        ]}
        data={valuations}
        onRowClick={(v) => setShowDetail(v)}
        emptyMessage="No valuations run yet. Create your first valuation."
      />

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Run DCF Valuation" wide>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Company</label>
              <select className="input" value={form.company_id} onChange={(e) => setForm({ ...form, company_id: e.target.value })}>
                <option value="">Select company...</option>
                {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Valuation Date</label>
              <input className="input" type="date" value={form.valuation_date}
                onChange={(e) => setForm({ ...form, valuation_date: e.target.value })} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Base Revenue ($)</label>
              <input className="input" type="number" value={form.base_revenue}
                onChange={(e) => setForm({ ...form, base_revenue: e.target.value })} />
            </div>
            <div>
              <label className="label">Base EBITDA ($)</label>
              <input className="input" type="number" value={form.base_ebitda}
                onChange={(e) => setForm({ ...form, base_ebitda: e.target.value })} />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Discount Rate (WACC)</label>
              <input className="input" type="number" step="0.01" value={form.discount_rate}
                onChange={(e) => setForm({ ...form, discount_rate: e.target.value })} />
            </div>
            <div>
              <label className="label">Terminal Growth</label>
              <input className="input" type="number" step="0.005" value={form.terminal_growth_rate}
                onChange={(e) => setForm({ ...form, terminal_growth_rate: e.target.value })} />
            </div>
            <div>
              <label className="label">Net Debt ($)</label>
              <input className="input" type="number" value={form.net_debt}
                onChange={(e) => setForm({ ...form, net_debt: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="label">Revenue Growth Rates (comma-separated)</label>
            <input className="input" value={form.revenue_growth}
              onChange={(e) => setForm({ ...form, revenue_growth: e.target.value })} placeholder="0.10,0.10,0.08,0.08,0.06" />
          </div>
          <div>
            <label className="label">EBITDA Margins (comma-separated)</label>
            <input className="input" value={form.ebitda_margins}
              onChange={(e) => setForm({ ...form, ebitda_margins: e.target.value })} placeholder="0.25,0.26,0.27,0.28,0.28" />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleRun} disabled={!form.company_id}>
              <Calculator className="h-4 w-4" /> Run Valuation
            </button>
          </div>
        </div>
      </Modal>

      {/* Detail Modal */}
      <Modal open={!!showDetail} onClose={() => setShowDetail(null)} title="Valuation Results" wide>
        {showDetail && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="rounded-lg bg-slate-50 p-4 text-center">
                <p className="text-xs font-medium text-slate-500">Enterprise Value</p>
                <p className="text-xl font-bold text-slate-900 mt-1">
                  {showDetail.enterprise_value ? formatCurrency(showDetail.enterprise_value) : "—"}
                </p>
              </div>
              <div className="rounded-lg bg-slate-50 p-4 text-center">
                <p className="text-xs font-medium text-slate-500">Equity Value</p>
                <p className="text-xl font-bold text-slate-900 mt-1">
                  {showDetail.equity_value ? formatCurrency(showDetail.equity_value) : "—"}
                </p>
              </div>
              <div className="rounded-lg bg-slate-50 p-4 text-center">
                <p className="text-xs font-medium text-slate-500">Implied EV/EBITDA</p>
                <p className="text-xl font-bold text-slate-900 mt-1">
                  {showDetail.implied_multiple ? `${showDetail.implied_multiple.toFixed(1)}x` : "—"}
                </p>
              </div>
            </div>

            {showDetail.outputs?.projections && (
              <div>
                <h3 className="text-sm font-semibold text-slate-700 mb-2">Cash Flow Projections</h3>
                <div className="overflow-x-auto rounded-lg border border-slate-200">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-slate-50 text-xs uppercase text-slate-500">
                        <th className="px-4 py-2 text-left">Year</th>
                        <th className="px-4 py-2 text-right">Revenue</th>
                        <th className="px-4 py-2 text-right">EBITDA</th>
                        <th className="px-4 py-2 text-right">FCF</th>
                        <th className="px-4 py-2 text-right">PV(FCF)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {showDetail.outputs.projections.map((p: any) => (
                        <tr key={p.year}>
                          <td className="px-4 py-2">Year {p.year}</td>
                          <td className="px-4 py-2 text-right font-mono">{formatCurrency(p.revenue)}</td>
                          <td className="px-4 py-2 text-right font-mono">{formatCurrency(p.ebitda)}</td>
                          <td className="px-4 py-2 text-right font-mono">{formatCurrency(p.fcf)}</td>
                          <td className="px-4 py-2 text-right font-mono">{formatCurrency(p.pv_fcf)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {showDetail.outputs?.terminal_value && (
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="rounded-lg border border-slate-200 p-3">
                  <span className="text-slate-500">Terminal Value: </span>
                  <span className="font-semibold">{formatCurrency(showDetail.outputs.terminal_value)}</span>
                </div>
                <div className="rounded-lg border border-slate-200 p-3">
                  <span className="text-slate-500">PV(Terminal): </span>
                  <span className="font-semibold">{formatCurrency(showDetail.outputs.pv_terminal_value)}</span>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
