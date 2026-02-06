"use client";

import { useState } from "react";
import { useApi } from "@/hooks/useApi";
import { reports as reportsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import DataTable from "@/components/ui/DataTable";
import StatusBadge from "@/components/ui/StatusBadge";
import Modal from "@/components/ui/Modal";
import { FileText, Plus, Download } from "lucide-react";
import type { Report, AuditLog } from "@/lib/types";

export default function ReportsPage() {
  const { data: reportsData, refetch } = useApi<{ reports: Report[]; total: number }>(
    () => reportsApi.list()
  );
  const { data: auditData } = useApi<{ logs: AuditLog[]; total: number }>(
    () => reportsApi.getAuditLog()
  );
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    name: "",
    report_type: "portfolio_summary",
    output_format: "pdf",
  });
  const [tab, setTab] = useState<"reports" | "audit">("reports");

  const reportsList = reportsData?.reports || [];
  const auditLogs = auditData?.logs || [];

  const handleCreate = async () => {
    await reportsApi.create(form);
    setShowCreate(false);
    setForm({ name: "", report_type: "portfolio_summary", output_format: "pdf" });
    refetch();
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Reports</h1>
          <p className="text-sm text-slate-500 mt-1">Generate audit-ready reports and review activity</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          <Plus className="h-4 w-4" /> Generate Report
        </button>
      </div>

      <div className="flex gap-1 rounded-lg bg-slate-100 p-1 w-fit">
        <button
          onClick={() => setTab("reports")}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === "reports" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Reports
        </button>
        <button
          onClick={() => setTab("audit")}
          className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === "audit" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Audit Log
        </button>
      </div>

      {tab === "reports" ? (
        <DataTable
          columns={[
            { key: "name", header: "Report Name", render: (r: Report) => (
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-slate-400" />
                <span className="font-medium text-slate-900">{r.name}</span>
              </div>
            )},
            { key: "report_type", header: "Type", render: (r: Report) => (
              <span className="capitalize">{r.report_type.replace(/_/g, " ")}</span>
            )},
            { key: "output_format", header: "Format", render: (r: Report) => (
              <span className="badge bg-slate-100 text-slate-700 uppercase">{r.output_format}</span>
            )},
            { key: "status", header: "Status", render: (r: Report) => <StatusBadge status={r.status} /> },
            { key: "created_by", header: "Created By" },
            { key: "created_at", header: "Date", render: (r: Report) => formatDate(r.created_at) },
            { key: "actions", header: "", render: (r: Report) => (
              r.output_path ? (
                <button className="btn-secondary text-xs py-1 px-3">
                  <Download className="h-3 w-3" /> Download
                </button>
              ) : null
            )},
          ]}
          data={reportsList}
          emptyMessage="No reports generated yet."
        />
      ) : (
        <DataTable
          columns={[
            { key: "timestamp", header: "Time", render: (l: AuditLog) => formatDate(l.timestamp) },
            { key: "action", header: "Action", render: (l: AuditLog) => (
              <span className="badge bg-slate-100 text-slate-700">{l.action}</span>
            )},
            { key: "entity_type", header: "Entity Type", render: (l: AuditLog) => (
              <span className="capitalize">{l.entity_type}</span>
            )},
            { key: "entity_id", header: "Entity ID", render: (l: AuditLog) => (
              <span className="font-mono text-xs">{l.entity_id.slice(0, 8)}...</span>
            )},
            { key: "user_id", header: "User" },
            { key: "changes", header: "Details", render: (l: AuditLog) => (
              <span className="text-xs text-slate-500 truncate max-w-xs block">
                {JSON.stringify(l.changes).slice(0, 80)}
              </span>
            )},
          ]}
          data={auditLogs}
          emptyMessage="No audit events recorded."
        />
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Generate Report">
        <div className="space-y-4">
          <div>
            <label className="label">Report Name</label>
            <input className="input" value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="e.g. Q4 2024 Portfolio Review" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Report Type</label>
              <select className="input" value={form.report_type}
                onChange={(e) => setForm({ ...form, report_type: e.target.value })}>
                <option value="portfolio_summary">Portfolio Summary</option>
                <option value="company_tearsheet">Company Tearsheet</option>
                <option value="valuation_report">Valuation Report</option>
                <option value="quarterly_review">Quarterly Review</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <div>
              <label className="label">Output Format</label>
              <select className="input" value={form.output_format}
                onChange={(e) => setForm({ ...form, output_format: e.target.value })}>
                <option value="pdf">PDF</option>
                <option value="xlsx">Excel</option>
                <option value="csv">CSV</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleCreate} disabled={!form.name}>
              Generate
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
