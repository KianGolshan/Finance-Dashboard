"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useApi } from "@/hooks/useApi";
import { portfolio } from "@/lib/api";
import { formatCurrency, formatMOIC, formatPercent, formatDate, sectorLabel } from "@/lib/utils";
import DataTable from "@/components/ui/DataTable";
import StatusBadge from "@/components/ui/StatusBadge";
import Modal from "@/components/ui/Modal";
import { Plus } from "lucide-react";
import type { Company, Fund } from "@/lib/types";

export default function CompaniesPage() {
  const router = useRouter();
  const { data: companiesData, refetch } = useApi<{ companies: Company[]; total: number }>(
    () => portfolio.listCompanies()
  );
  const { data: fundsData } = useApi<{ funds: Fund[]; total: number }>(() => portfolio.listFunds());
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    fund_id: "",
    name: "",
    sector: "technology",
    geography: "North America",
    investment_date: new Date().toISOString().split("T")[0],
    initial_investment: "",
    current_valuation: "",
    ownership_pct: "",
  });

  const companies = companiesData?.companies || [];
  const funds = fundsData?.funds || [];

  const handleCreate = async () => {
    await portfolio.createCompany({
      ...form,
      initial_investment: parseFloat(form.initial_investment),
      current_valuation: parseFloat(form.current_valuation),
      ownership_pct: parseFloat(form.ownership_pct),
    });
    setShowCreate(false);
    refetch();
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Portfolio Companies</h1>
          <p className="text-sm text-slate-500 mt-1">{companies.length} companies across all funds</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          <Plus className="h-4 w-4" /> Add Company
        </button>
      </div>

      <DataTable
        columns={[
          { key: "name", header: "Company", render: (c: Company) => (
            <div>
              <p className="font-medium text-slate-900">{c.name}</p>
              <p className="text-xs text-slate-400">{sectorLabel(c.sector)}</p>
            </div>
          )},
          { key: "geography", header: "Geography" },
          { key: "investment_date", header: "Invested", render: (c: Company) => formatDate(c.investment_date) },
          { key: "initial_investment", header: "Cost Basis", render: (c: Company) => formatCurrency(c.initial_investment), className: "text-right" },
          { key: "current_valuation", header: "Current Value", render: (c: Company) => formatCurrency(c.current_valuation), className: "text-right" },
          { key: "ownership_pct", header: "Ownership", render: (c: Company) => formatPercent(c.ownership_pct / 100), className: "text-right" },
          { key: "moic", header: "MOIC", render: (c: Company) => (
            <span className={c.moic >= 1 ? "text-emerald-600 font-semibold" : "text-red-600 font-semibold"}>
              {formatMOIC(c.moic)}
            </span>
          ), className: "text-right" },
          { key: "status", header: "Status", render: (c: Company) => <StatusBadge status={c.status} /> },
        ]}
        data={companies}
        onRowClick={(c) => router.push(`/portfolio/companies/${c.id}`)}
        emptyMessage="No companies yet. Add your first portfolio company."
      />

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Portfolio Company" wide>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Company Name</label>
              <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div>
              <label className="label">Fund</label>
              <select className="input" value={form.fund_id} onChange={(e) => setForm({ ...form, fund_id: e.target.value })}>
                <option value="">Select fund...</option>
                {funds.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Sector</label>
              <select className="input" value={form.sector} onChange={(e) => setForm({ ...form, sector: e.target.value })}>
                {["technology","healthcare","financials","industrials","consumer","energy","real_estate","materials","telecom","utilities"].map((s) => (
                  <option key={s} value={s}>{sectorLabel(s)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Geography</label>
              <input className="input" value={form.geography} onChange={(e) => setForm({ ...form, geography: e.target.value })} />
            </div>
            <div>
              <label className="label">Investment Date</label>
              <input className="input" type="date" value={form.investment_date} onChange={(e) => setForm({ ...form, investment_date: e.target.value })} />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Initial Investment ($)</label>
              <input className="input" type="number" value={form.initial_investment} onChange={(e) => setForm({ ...form, initial_investment: e.target.value })} />
            </div>
            <div>
              <label className="label">Current Valuation ($)</label>
              <input className="input" type="number" value={form.current_valuation} onChange={(e) => setForm({ ...form, current_valuation: e.target.value })} />
            </div>
            <div>
              <label className="label">Ownership (%)</label>
              <input className="input" type="number" value={form.ownership_pct} onChange={(e) => setForm({ ...form, ownership_pct: e.target.value })} />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleCreate} disabled={!form.name || !form.fund_id}>Add Company</button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
