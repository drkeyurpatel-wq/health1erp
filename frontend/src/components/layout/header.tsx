"use client";
import React, { useState } from "react";
import { Bell, Search, Globe, ChevronDown } from "lucide-react";
import { useAuthStore } from "@/store/auth-store";

const languages = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ar", label: "Arabic" },
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "zh", label: "Chinese" },
];

export function Header() {
  const { user } = useAuthStore();
  const [langOpen, setLangOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState("en");

  const selectLang = (code: string) => {
    setCurrentLang(code);
    localStorage.setItem("language", code);
    setLangOpen(false);
  };

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-gray-200 px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search patients, UHID, appointments..."
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div className="flex items-center gap-4">
          {/* Language Selector */}
          <div className="relative">
            <button
              onClick={() => setLangOpen(!langOpen)}
              className="flex items-center gap-1 px-3 py-2 rounded-lg hover:bg-gray-50 text-sm text-gray-600"
            >
              <Globe className="h-4 w-4" />
              {languages.find(l => l.code === currentLang)?.label}
              <ChevronDown className="h-3 w-3" />
            </button>
            {langOpen && (
              <div className="absolute right-0 top-full mt-1 w-40 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                {languages.map(lang => (
                  <button
                    key={lang.code}
                    onClick={() => selectLang(lang.code)}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50"
                  >
                    {lang.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-gray-50">
            <Bell className="h-5 w-5 text-gray-500" />
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
          </button>

          {/* User */}
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white text-xs font-semibold">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
