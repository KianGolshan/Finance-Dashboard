"use client";

import { useState } from "react";
import { useApi } from "@/hooks/useApi";
import { portfolio } from "@/lib/api";
import { formatCurrency, formatMOIC } from "@/lib/utils";
import MetricCard from "@/components/ui/MetricCard";
import DataTable from "@/components/ui/DataTable";
import StatusBadge from "@/components/ui/StatusBadge";
import Modal from "@/components/ui/Modal";
import { DollarSign, TrendingUp, Building2, PieChart, Plus } from "lucide-react";
import type { Fund, PortfolioSummary } from "@/lib/types";

export default function PortfolioPage() {
  const { data: summary } = useApi<PortfolioSummary>(() => portfolio.getSummary());
  const { data: fundsData, refetch } = useApi<{ funds: Fund[]; total: number }>(() => portfolio.listFunds());
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", vintage_year: 2024, strategy: "buyout", aum: "" });

  const handleCreate = async () => {
    await portfolio.createFund({
      ...form,
      aum: form.aum ? parseFloat(form.aum) : null,
    });
    setShowCreate(false);
    setForm({ name: "", vintage_year: 2024, strategy: "buyout", aum: "" });
    refetch();
  };

  const funds = fundsData?.funds || [];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Portfolio Overview</h1>
          <p className="text-sm text-slate-500 mt-1">Aggregate performance across all funds</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          <Plus className="h-4 w-4" /> New Fund
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total NAV"
          value={formatCurrency(summary?.total_nav || 0)}
          subtitle={`${summary?.active_companies || 0} active companies`}
          icon={DollarSign}
        />
        <MetricCard
          title="Total Invested"
          value={formatCurrency(summary?.total_invested || 0)}
          subtitle={`Across ${summary?.fund_count || 0} funds`}
          icon={Building2}
        />
        <MetricCard
          title="Unrealized Gain"
          value={formatCurrency(summary?.unrealized_gain || 0)}
          change={summary?.total_invested ? (summary.unrealized_gain / summary.total_invested) : 0}
          icon={TrendingUp}
        />
        <MetricCard
          title="Gross MOIC"
          value={formatMOIC(summary?.gross_moic || 0)}
          subtitle={`${summary?.company_count || 0} total companies`}
          icon={PieChart}
        />
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Funds</h2>
        <DataTable
          columns={[
            { key: "name", header: "Fund Name", render: (f: Fund) => <span className="font-medium text-slate-900">{f.name}</span> },
            { key: "vintage_year", header: "Vintage" },
            { key: "strategy", header: "Strategy", render: (f: Fund) => <span className="capitalize">{f.strategy.replace(/_/g, " ")}</span> },
            { key: "aum", header: "AUM", render: (f: Fund) => f.aum ? formatCurrency(f.aum) : "—", className: "text-right" },
            { key: "company_count", header: "Companies", className: "text-right" },
            { key: "total_invested", header: "Invested", render: (f: Fund) => formatCurrency(f.total_invested), className: "text-right" },
            { key: "total_value", header: "Current Value", render: (f: Fund) => formatCurrency(f.total_value), className: "text-right" },
            { key: "status", header: "Status", render: (f: Fund) => <StatusBadge status={f.status} /> },
          ]}
          data={funds}
          emptyMessage="No funds yet. Create your first fund to get started."
        />
      </div>

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Fund">
        <div className="space-y-4">
          <div>
            <label className="label">Fund Name</label>
            <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Growth Equity Fund III" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Vintage Year</label>
              <input className="input" type="number" value={form.vintage_year} onChange={(e) => setForm({ ...form, vintage_year: parseInt(e.target.value) })} />
            </div>
            <div>
              <label className="label">Strategy</label>
              <select className="input" value={form.strategy} onChange={(e) => setForm({ ...form, strategy: e.target.value })}>
                <option value="buyout">Buyout</option>
                <option value="growth_equity">Growth Equity</option>
                <option value="venture_capital">Venture Capital</option>
                <option value="credit">Credit</option>
                <option value="real_assets">Real Assets</option>
                <option value="secondaries">Secondaries</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">AUM ($)</label>
            <input className="input" type="number" value={form.aum} onChange={(e) => setForm({ ...form, aum: e.target.value })} placeholder="e.g. 500000000" />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleCreate} disabled={!form.name}>Create Fund</button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
