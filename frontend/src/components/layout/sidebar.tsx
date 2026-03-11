"use client";
import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Users, Calendar, BedDouble, Receipt,
  Package, Pill, FlaskConical, ScanLine, Scissors,
  BarChart3, Settings, LogOut, Heart, ChevronLeft,
  ChevronRight, HelpCircle, UserCog, FileHeart,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";

const navGroups = [
  {
    label: "Overview",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    ],
  },
  {
    label: "Clinical",
    items: [
      { href: "/patients", label: "Patients", icon: Users },
      { href: "/emr", label: "EMR / Charting", icon: FileHeart },
      { href: "/appointments", label: "Appointments", icon: Calendar },
      { href: "/ipd", label: "IPD / Inpatient", icon: BedDouble },
    ],
  },
  {
    label: "Diagnostics",
    items: [
      { href: "/laboratory", label: "Laboratory", icon: FlaskConical },
      { href: "/radiology", label: "Radiology", icon: ScanLine },
      { href: "/pharmacy", label: "Pharmacy", icon: Pill },
      { href: "/ot", label: "Operation Theatre", icon: Scissors },
    ],
  },
  {
    label: "Administration",
    items: [
      { href: "/billing", label: "Billing", icon: Receipt },
      { href: "/inventory", label: "Inventory", icon: Package },
      { href: "/reports", label: "Reports", icon: BarChart3 },
      { href: "/hr", label: "HR & Staff", icon: UserCog },
    ],
  },
];

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

export function Sidebar({ collapsed = false, onToggle, mobileOpen, onMobileClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  const sidebarContent = (
    <aside className={cn(
      "fixed left-0 top-0 z-40 h-screen flex flex-col gradient-sidebar text-white shadow-sidebar transition-all duration-300",
      collapsed ? "w-[72px]" : "w-[280px]",
      mobileOpen !== undefined && !mobileOpen && "max-lg:hidden",
      mobileOpen && "max-lg:fixed max-lg:inset-0 max-lg:w-[280px] max-lg:z-50"
    )}>
      {/* Logo */}
      <div className={cn(
        "flex items-center border-b border-white/10 shrink-0 transition-all duration-300",
        collapsed ? "px-4 py-5 justify-center" : "px-6 py-5 gap-3"
      )}>
        <div className="relative">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-400 to-teal-400 flex items-center justify-center shadow-lg">
            <Heart className="h-5 w-5 text-white" />
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 h-3 w-3 bg-emerald-400 rounded-full border-2 border-sidebar-bg" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <h1 className="text-lg font-bold tracking-tight">Health1ERP</h1>
            <p className="text-[11px] text-sidebar-text leading-tight">Hospital Management</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {navGroups.map(group => (
          <div key={group.label}>
            {!collapsed && (
              <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-sidebar-text/60">
                {group.label}
              </p>
            )}
            <div className="space-y-0.5">
              {group.items.map(({ href, label, icon: Icon }) => {
                const isActive = pathname === href || pathname.startsWith(href + "/");
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={onMobileClose}
                    className={cn(
                      "flex items-center gap-3 rounded-xl text-sm font-medium transition-all duration-200 group relative",
                      collapsed ? "px-3 py-3 justify-center" : "px-3 py-2.5",
                      isActive
                        ? "bg-white/15 text-white shadow-sm"
                        : "text-sidebar-text hover:bg-white/8 hover:text-white"
                    )}
                    title={collapsed ? label : undefined}
                  >
                    {isActive && (
                      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full bg-blue-400" />
                    )}
                    <Icon className={cn("h-[18px] w-[18px] shrink-0", isActive && "text-blue-400")} />
                    {!collapsed && <span>{label}</span>}
                    {collapsed && (
                      <div className="absolute left-full ml-2 px-2.5 py-1.5 rounded-lg bg-gray-900 text-white text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity shadow-lg z-50">
                        {label}
                      </div>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Collapse Toggle */}
      {onToggle && (
        <div className="px-3 py-2 border-t border-white/10">
          <button
            onClick={onToggle}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-sidebar-text hover:bg-white/8 hover:text-white transition-all text-sm"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <><ChevronLeft className="h-4 w-4" /><span>Collapse</span></>}
          </button>
        </div>
      )}

      {/* User */}
      <div className="border-t border-white/10 p-3 shrink-0">
        <div className={cn("flex items-center", collapsed ? "justify-center" : "gap-3")}>
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold text-xs shrink-0 shadow">
            {user?.first_name?.[0]}{user?.last_name?.[0]}
          </div>
          {!collapsed && (
            <>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-[11px] text-sidebar-text truncate">{user?.role}</p>
              </div>
              <button onClick={logout} className="p-2 rounded-lg text-sidebar-text hover:text-red-400 hover:bg-white/8 transition-all" title="Sign out">
                <LogOut className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      </div>
    </aside>
  );

  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={onMobileClose} />
      )}
      {sidebarContent}
    </>
  );
}
