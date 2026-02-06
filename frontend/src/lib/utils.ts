import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number, currency = "USD"): string {
  if (Math.abs(value) >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(1)}B`;
  }
  if (Math.abs(value) >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(value) >= 1_000) {
    return `$${(value / 1_000).toFixed(1)}K`;
  }
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(value);
}

export function formatNumber(value: number, decimals = 1): string {
  if (Math.abs(value) >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(decimals)}B`;
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(decimals)}M`;
  if (Math.abs(value) >= 1_000) return `${(value / 1_000).toFixed(decimals)}K`;
  return value.toFixed(decimals);
}

export function formatPercent(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatMOIC(value: number): string {
  return `${value.toFixed(2)}x`;
}

export function statusColor(status: string): string {
  const colors: Record<string, string> = {
    active: "bg-emerald-100 text-emerald-800",
    closed: "bg-slate-100 text-slate-800",
    fundraising: "bg-blue-100 text-blue-800",
    exited: "bg-purple-100 text-purple-800",
    written_off: "bg-red-100 text-red-800",
    marked_up: "bg-amber-100 text-amber-800",
    pending: "bg-yellow-100 text-yellow-800",
    completed: "bg-emerald-100 text-emerald-800",
    failed: "bg-red-100 text-red-800",
    draft: "bg-slate-100 text-slate-800",
    approved: "bg-emerald-100 text-emerald-800",
    in_review: "bg-blue-100 text-blue-800",
    parsing: "bg-blue-100 text-blue-800",
    extracting: "bg-indigo-100 text-indigo-800",
    generating: "bg-blue-100 text-blue-800",
  };
  return colors[status] || "bg-slate-100 text-slate-800";
}

export function sectorLabel(sector: string): string {
  return sector.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
