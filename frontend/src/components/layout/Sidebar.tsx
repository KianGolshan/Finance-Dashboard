"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FileText,
  Scan,
  Activity,
  Calculator,
  ClipboardList,
  TrendingUp,
} from "lucide-react";

const navigation = [
  { name: "Portfolio", href: "/portfolio", icon: LayoutDashboard },
  { name: "Companies", href: "/portfolio/companies", icon: TrendingUp },
  { name: "Documents", href: "/documents", icon: FileText },
  { name: "Extraction", href: "/documents/extraction", icon: Scan },
  { name: "Monitoring", href: "/monitoring", icon: Activity },
  { name: "Valuation", href: "/valuation", icon: Calculator },
  { name: "Reports", href: "/reports", icon: ClipboardList },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white">
      <div className="flex h-16 items-center gap-3 border-b border-slate-200 px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
          <TrendingUp className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-900">Meridian</h1>
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
            Private Markets
          </p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/portfolio" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-brand-50 text-brand-700"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <item.icon
                className={cn(
                  "h-5 w-5 shrink-0",
                  isActive ? "text-brand-600" : "text-slate-400"
                )}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-slate-200 p-4">
        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-medium text-slate-500">Platform</p>
          <p className="text-xs text-slate-400">v0.1.0 — Prototype</p>
        </div>
      </div>
    </aside>
  );
}
