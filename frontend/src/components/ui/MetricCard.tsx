"use client";

import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  change?: number;
  icon?: LucideIcon;
  className?: string;
}

export default function MetricCard({ title, value, subtitle, change, icon: Icon, className }: MetricCardProps) {
  return (
    <div className={cn("metric-card", className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{value}</p>
          {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
        </div>
        {Icon && (
          <div className="rounded-lg bg-brand-50 p-2.5">
            <Icon className="h-5 w-5 text-brand-600" />
          </div>
        )}
      </div>
      {change !== undefined && (
        <div className="mt-3 flex items-center gap-1">
          <span
            className={cn(
              "text-sm font-medium",
              change >= 0 ? "text-emerald-600" : "text-red-600"
            )}
          >
            {change >= 0 ? "+" : ""}
            {(change * 100).toFixed(1)}%
          </span>
          <span className="text-sm text-slate-400">vs prior period</span>
        </div>
      )}
    </div>
  );
}
