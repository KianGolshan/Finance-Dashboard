"use client";

import { useState } from "react";
import { useApi } from "@/hooks/useApi";
import { documents } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import DataTable from "@/components/ui/DataTable";
import StatusBadge from "@/components/ui/StatusBadge";
import { CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import type { Document, Extraction } from "@/lib/types";

export default function ExtractionPage() {
  const { data: docsData } = useApi<{ documents: Document[]; total: number }>(
    () => documents.list({ status: "completed" })
  );
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const { data: extractionsData, refetch } = useApi<{ extractions: Extraction[]; total: number }>(
    () => selectedDoc ? documents.getExtractions(selectedDoc) : Promise.resolve({ extractions: [], total: 0 }),
    [selectedDoc]
  );

  const docs = docsData?.documents || [];
  const extractions = extractionsData?.extractions || [];

  const handleValidate = async (id: string, validated: boolean) => {
    await documents.validateExtraction(id, { validated, validated_by: "analyst" });
    refetch();
  };

  const confidenceIcon = (score: number) => {
    if (score >= 0.8) return <CheckCircle className="h-4 w-4 text-emerald-500" />;
    if (score >= 0.5) return <AlertTriangle className="h-4 w-4 text-amber-500" />;
    return <XCircle className="h-4 w-4 text-red-500" />;
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Data Extraction</h1>
        <p className="text-sm text-slate-500 mt-1">Review and validate extracted financial data</p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-4">
          <div className="card">
            <div className="card-header">
              <h2 className="text-sm font-semibold text-slate-700">Processed Documents</h2>
            </div>
            <div className="divide-y divide-slate-100">
              {docs.length === 0 ? (
                <p className="p-6 text-sm text-slate-400 text-center">No processed documents</p>
              ) : docs.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => setSelectedDoc(doc.id)}
                  className={`w-full px-4 py-3 text-left transition-colors hover:bg-slate-50 ${
                    selectedDoc === doc.id ? "bg-brand-50 border-l-2 border-brand-500" : ""
                  }`}
                >
                  <p className="text-sm font-medium text-slate-900 truncate">{doc.filename}</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {doc.extraction_count} fields &middot; {formatDate(doc.upload_date)}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="col-span-8">
          {!selectedDoc ? (
            <div className="card p-12 text-center">
              <p className="text-slate-400">Select a document to review extractions</p>
            </div>
          ) : (
            <DataTable
              columns={[
                { key: "field_name", header: "Field", render: (e: Extraction) => (
                  <span className="font-medium capitalize">{e.field_name.replace(/_/g, " ")}</span>
                )},
                { key: "field_value", header: "Value", render: (e: Extraction) => (
                  <span className="font-mono text-sm">{e.field_value}</span>
                )},
                { key: "confidence_score", header: "Confidence", render: (e: Extraction) => (
                  <div className="flex items-center gap-2">
                    {confidenceIcon(e.confidence_score)}
                    <span className="text-sm">{(e.confidence_score * 100).toFixed(0)}%</span>
                  </div>
                )},
                { key: "extraction_method", header: "Method", render: (e: Extraction) => (
                  <StatusBadge status={e.extraction_method} />
                )},
                { key: "validated", header: "Status", render: (e: Extraction) => (
                  e.validated ? (
                    <span className="badge bg-emerald-100 text-emerald-800">Validated</span>
                  ) : (
                    <div className="flex gap-1">
                      <button onClick={() => handleValidate(e.id, true)}
                        className="rounded p-1 text-emerald-600 hover:bg-emerald-50" title="Approve">
                        <CheckCircle className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleValidate(e.id, false)}
                        className="rounded p-1 text-red-600 hover:bg-red-50" title="Reject">
                        <XCircle className="h-4 w-4" />
                      </button>
                    </div>
                  )
                )},
              ]}
              data={extractions}
              emptyMessage="No extractions for this document"
            />
          )}
        </div>
      </div>
    </div>
  );
}
