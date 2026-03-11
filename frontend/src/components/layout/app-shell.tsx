"use client";
import React from "react";
import { Sidebar } from "./sidebar";
import { Header } from "./header";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="ml-[260px]">
        <Header />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
