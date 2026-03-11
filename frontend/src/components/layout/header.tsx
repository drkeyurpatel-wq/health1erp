"use client";
import React, { useState, useRef, useEffect } from "react";
import { Bell, Search, Globe, ChevronDown, Menu, X, LogOut, Settings, User, Clock } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";
import Link from "next/link";

const languages = [
  { code: "en", label: "English", flag: "EN" },
  { code: "hi", label: "Hindi", flag: "HI" },
  { code: "ar", label: "Arabic", flag: "AR" },
  { code: "es", label: "Spanish", flag: "ES" },
  { code: "fr", label: "French", flag: "FR" },
  { code: "zh", label: "Chinese", flag: "ZH" },
];

const mockNotifications = [
  { id: "1", title: "Critical: ICU Bed 4", message: "Patient vitals deteriorating - NEWS2 score 8", time: "2 min ago", type: "critical" as const },
  { id: "2", title: "Lab Results Ready", message: "CBC results for patient #P2024001", time: "15 min ago", type: "info" as const },
  { id: "3", title: "Low Stock Alert", message: "Paracetamol IV below reorder level", time: "1 hr ago", type: "warning" as const },
  { id: "4", title: "Discharge Pending", message: "Dr. Shah approved discharge for Bed 12", time: "2 hrs ago", type: "success" as const },
];

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuthStore();
  const [langOpen, setLangOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState("en");
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const langRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (langRef.current && !langRef.current.contains(e.target as Node)) setLangOpen(false);
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) setProfileOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const selectLang = (code: string) => {
    setCurrentLang(code);
    localStorage.setItem("language", code);
    setLangOpen(false);
  };

  const notifTypeStyles = {
    critical: "bg-red-50 border-red-200",
    warning: "bg-amber-50 border-amber-200",
    info: "bg-blue-50 border-blue-200",
    success: "bg-emerald-50 border-emerald-200",
  };

  return (
    <header className="sticky top-0 z-30 glass border-b border-gray-200/50 px-4 lg:px-6 h-16">
      <div className="flex items-center justify-between h-full">
        {/* Mobile menu + Search */}
        <div className="flex items-center gap-3">
          {onMenuClick && (
            <button onClick={onMenuClick} className="lg:hidden p-2 rounded-xl hover:bg-gray-100 transition-colors">
              <Menu className="h-5 w-5 text-gray-600" />
            </button>
          )}
          <div className={`relative transition-all duration-300 ${searchFocused ? "w-96" : "w-72"} max-lg:w-48`}>
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onFocus={() => setSearchFocused(true)}
              onBlur={() => { setSearchFocused(false); setSearchQuery(""); }}
              placeholder="Search patients, UHID, doctors..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200/80 bg-white/60 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400 focus:bg-white transition-all placeholder:text-gray-400"
            />
            {searchQuery && searchFocused && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50">
                <div className="px-4 py-3 text-sm text-gray-500 text-center">
                  <Search className="h-5 w-5 mx-auto mb-2 text-gray-300" />
                  Type to search patients, appointments, or UHIDs
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          {/* Live Clock */}
          <LiveClock />

          {/* Language */}
          <div ref={langRef} className="relative">
            <button
              onClick={() => { setLangOpen(!langOpen); setNotifOpen(false); setProfileOpen(false); }}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl hover:bg-gray-100/80 text-sm text-gray-600 transition-colors"
            >
              <Globe className="h-4 w-4" />
              <span className="max-lg:hidden">{languages.find(l => l.code === currentLang)?.flag}</span>
              <ChevronDown className="h-3 w-3" />
            </button>
            {langOpen && (
              <div className="absolute right-0 top-full mt-2 w-44 bg-white rounded-xl shadow-lg border border-gray-100 py-1.5 z-50 animate-slide-down">
                {languages.map(lang => (
                  <button
                    key={lang.code}
                    onClick={() => selectLang(lang.code)}
                    className={`w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center justify-between ${
                      currentLang === lang.code ? "bg-primary-50 text-primary-700 font-medium" : "hover:bg-gray-50 text-gray-700"
                    }`}
                  >
                    <span>{lang.label}</span>
                    <span className="text-xs text-gray-400">{lang.flag}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Notifications */}
          <div ref={notifRef} className="relative">
            <button
              onClick={() => { setNotifOpen(!notifOpen); setLangOpen(false); setProfileOpen(false); }}
              className="relative p-2.5 rounded-xl hover:bg-gray-100/80 transition-colors"
            >
              <Bell className="h-5 w-5 text-gray-500" />
              <span className="notification-dot" />
            </button>
            {notifOpen && (
              <div className="absolute right-0 top-full mt-2 w-96 bg-white rounded-xl shadow-lg border border-gray-100 z-50 animate-slide-down">
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                  <h3 className="font-semibold text-sm text-gray-900">Notifications</h3>
                  <span className="text-xs text-primary-600 font-medium cursor-pointer hover:underline">Mark all read</span>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {mockNotifications.map(n => (
                    <div key={n.id} className={`px-4 py-3 border-b border-gray-50 hover:bg-gray-50/80 transition-colors cursor-pointer ${notifTypeStyles[n.type]} border-l-4`}>
                      <p className="text-sm font-medium text-gray-900">{n.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                      <p className="text-[11px] text-gray-400 mt-1 flex items-center gap-1"><Clock className="h-3 w-3" />{n.time}</p>
                    </div>
                  ))}
                </div>
                <div className="px-4 py-2.5 border-t border-gray-100 text-center">
                  <Link href="/notifications" className="text-xs text-primary-600 font-medium hover:underline" onClick={() => setNotifOpen(false)}>View all notifications</Link>
                </div>
              </div>
            )}
          </div>

          {/* Profile */}
          <div ref={profileRef} className="relative">
            <button
              onClick={() => { setProfileOpen(!profileOpen); setLangOpen(false); setNotifOpen(false); }}
              className="flex items-center gap-2.5 px-2 py-1.5 rounded-xl hover:bg-gray-100/80 transition-colors"
            >
              <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white text-xs font-semibold shadow-sm">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </div>
              <div className="max-lg:hidden text-left">
                <p className="text-sm font-medium text-gray-700 leading-tight">{user?.first_name}</p>
                <p className="text-[11px] text-gray-400 leading-tight">{user?.role}</p>
              </div>
              <ChevronDown className="h-3 w-3 text-gray-400 max-lg:hidden" />
            </button>
            {profileOpen && (
              <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-1.5 z-50 animate-slide-down">
                <div className="px-4 py-3 border-b border-gray-100">
                  <p className="text-sm font-semibold text-gray-900">{user?.first_name} {user?.last_name}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
                <Link href="/settings" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                  <User className="h-4 w-4 text-gray-400" /><span>My Profile</span>
                </Link>
                <Link href="/settings" onClick={() => setProfileOpen(false)} className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                  <Settings className="h-4 w-4 text-gray-400" /><span>Settings</span>
                </Link>
                <div className="border-t border-gray-100 mt-1 pt-1">
                  <button onClick={logout} className="flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 w-full transition-colors">
                    <LogOut className="h-4 w-4" /><span>Sign out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

function LiveClock() {
  const [time, setTime] = useState("");
  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }));
    tick();
    const id = setInterval(tick, 60000);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="hidden lg:flex items-center gap-1.5 px-3 py-2 text-sm text-gray-500">
      <Clock className="h-3.5 w-3.5" />
      <span className="font-medium tabular-nums">{time}</span>
    </div>
  );
}
