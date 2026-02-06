"use client";

import { cn, statusColor } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export default function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span className={cn("badge", statusColor(status), className)}>
      {status.replace(/_/g, " ")}
    </span>
  );
}
