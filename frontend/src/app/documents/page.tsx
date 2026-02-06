"use client";

import { useState, useRef } from "react";
import { useApi } from "@/hooks/useApi";
import { documents } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import DataTable from "@/components/ui/DataTable";
import StatusBadge from "@/components/ui/StatusBadge";
import { Upload, FileText, Loader2 } from "lucide-react";
import type { Document } from "@/lib/types";

export default function DocumentsPage() {
  const { data: docsData, refetch } = useApi<{ documents: Document[]; total: number }>(
    () => documents.list()
  );
  const [uploading, setUploading] = useState(false);
  const [extracting, setExtracting] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const docs = docsData?.documents || [];

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await documents.upload(file);
      refetch();
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleExtract = async (docId: string) => {
    setExtracting(docId);
    try {
      await documents.extract(docId);
      refetch();
    } finally {
      setExtracting(null);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes >= 1_000_000) return `${(bytes / 1_000_000).toFixed(1)} MB`;
    if (bytes >= 1_000) return `${(bytes / 1_000).toFixed(1)} KB`;
    return `${bytes} B`;
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Documents</h1>
          <p className="text-sm text-slate-500 mt-1">Upload and process financial documents</p>
        </div>
        <div>
          <input ref={fileRef} type="file" className="hidden" onChange={handleUpload}
            accept=".pdf,.docx,.xlsx,.csv,.txt" />
          <button onClick={() => fileRef.current?.click()} className="btn-primary" disabled={uploading}>
            {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            Upload Document
          </button>
        </div>
      </div>

      <DataTable
        columns={[
          { key: "filename", header: "Filename", render: (d: Document) => (
            <div className="flex items-center gap-3">
              <FileText className="h-5 w-5 text-slate-400 shrink-0" />
              <div>
                <p className="font-medium text-slate-900 truncate max-w-xs">{d.filename}</p>
                <p className="text-xs text-slate-400">{d.file_type.toUpperCase()} &middot; {formatSize(d.file_size)}</p>
              </div>
            </div>
          )},
          { key: "document_type", header: "Type", render: (d: Document) => d.document_type ? (
            <span className="capitalize text-sm">{d.document_type.replace(/_/g, " ")}</span>
          ) : <span className="text-slate-400">—</span> },
          { key: "upload_date", header: "Uploaded", render: (d: Document) => formatDate(d.upload_date) },
          { key: "extraction_count", header: "Extractions", className: "text-right" },
          { key: "processing_status", header: "Status", render: (d: Document) => <StatusBadge status={d.processing_status} /> },
          { key: "actions", header: "", render: (d: Document) => (
            d.processing_status === "pending" || d.processing_status === "failed" ? (
              <button
                onClick={(e) => { e.stopPropagation(); handleExtract(d.id); }}
                className="btn-secondary text-xs py-1 px-3"
                disabled={extracting === d.id}
              >
                {extracting === d.id ? <Loader2 className="h-3 w-3 animate-spin" /> : "Extract"}
              </button>
            ) : null
          )},
        ]}
        data={docs}
        emptyMessage="No documents uploaded. Upload your first financial document."
      />
    </div>
  );
}
