"use client";
import React, { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Search, FileHeart, User, Clock, ArrowRight,
  Stethoscope, Brain, ShieldCheck,
} from "lucide-react";
import api from "@/lib/api";
import type { Patient } from "@/types";

export default function EMRLandingPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Patient[]>([]);
  const [searching, setSearching] = useState(false);
  const [recentPatients, setRecentPatients] = useState<string[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      return JSON.parse(localStorage.getItem("emr_recent") || "[]");
    } catch { return []; }
  });

  const searchPatients = useCallback(async (q: string) => {
    setQuery(q);
    if (q.length < 2) { setResults([]); return; }
    setSearching(true);
    try {
      const { data } = await api.get(`/patients?q=${encodeURIComponent(q)}&page_size=8`);
      setResults(Array.isArray(data) ? data : data.items || []);
    } catch {
      setResults([]);
    } finally {
      setSearching(false);
    }
  }, []);

  const openPatient = (patientId: string) => {
    // Save to recent
    const recent = [patientId, ...recentPatients.filter(id => id !== patientId)].slice(0, 5);
    localStorage.setItem("emr_recent", JSON.stringify(recent));
    router.push(`/emr/${patientId}`);
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 pt-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 text-white mb-4 shadow-lg">
            <FileHeart className="h-8 w-8" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Electronic Medical Record</h1>
          <p className="text-gray-500 mt-2 max-w-lg mx-auto">
            CDSS-enabled clinical documentation with SOAP templates, AI-powered diagnostics, drug interaction checking, and predictive analytics.
          </p>
        </div>

        {/* Feature badges */}
        <div className="flex justify-center gap-3 mb-8 flex-wrap">
          <Badge variant="default" className="px-3 py-1.5 text-xs gap-1.5">
            <Stethoscope className="h-3.5 w-3.5" />SOAP Templates
          </Badge>
          <Badge variant="purple" className="px-3 py-1.5 text-xs gap-1.5">
            <Brain className="h-3.5 w-3.5" />CDSS + AI Diagnostics
          </Badge>
          <Badge variant="warning" className="px-3 py-1.5 text-xs gap-1.5">
            <ShieldCheck className="h-3.5 w-3.5" />Drug Interaction Check
          </Badge>
          <Badge variant="success" className="px-3 py-1.5 text-xs gap-1.5">
            <Clock className="h-3.5 w-3.5" />NEWS2 Auto-Scoring
          </Badge>
        </div>

        {/* Search */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => searchPatients(e.target.value)}
                placeholder="Search by patient name, UHID, or phone number..."
                className="w-full pl-12 pr-4 py-4 text-lg border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-4 focus:ring-primary-500/20 focus:border-primary-400 transition-all"
                autoFocus
              />
              {searching && (
                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                  <div className="animate-spin h-5 w-5 border-2 border-primary-600 border-t-transparent rounded-full" />
                </div>
              )}
            </div>

            {/* Results */}
            {results.length > 0 && (
              <div className="mt-4 space-y-2">
                {results.map(patient => {
                  const age = Math.floor(
                    (Date.now() - new Date(patient.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)
                  );
                  return (
                    <button
                      key={patient.id}
                      onClick={() => openPatient(patient.id)}
                      className="w-full flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-primary-300 hover:bg-primary-50/50 transition-all group"
                    >
                      <div className="flex items-center gap-4">
                        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white font-bold shadow">
                          {patient.first_name[0]}{patient.last_name[0]}
                        </div>
                        <div className="text-left">
                          <p className="font-semibold text-gray-900">
                            {patient.first_name} {patient.last_name}
                          </p>
                          <div className="flex items-center gap-3 text-sm text-gray-500 mt-0.5">
                            <span className="font-mono text-xs bg-gray-100 px-2 py-0.5 rounded">{patient.uhid}</span>
                            <span>{age}y / {patient.gender}</span>
                            <span>{patient.phone}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {patient.allergies && patient.allergies.length > 0 && (
                          <Badge variant="danger" className="text-[10px]">Allergies</Badge>
                        )}
                        <ArrowRight className="h-5 w-5 text-gray-300 group-hover:text-primary-500 transition-colors" />
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {query.length >= 2 && results.length === 0 && !searching && (
              <p className="text-center text-gray-400 mt-6 py-4">No patients found for &ldquo;{query}&rdquo;</p>
            )}
          </CardContent>
        </Card>

        {/* Quick access info */}
        {query.length < 2 && (
          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-5 text-center">
                <div className="h-10 w-10 rounded-xl bg-blue-100 flex items-center justify-center mx-auto mb-3">
                  <FileHeart className="h-5 w-5 text-blue-600" />
                </div>
                <h3 className="font-semibold text-sm text-gray-900">7 Specialty Templates</h3>
                <p className="text-xs text-gray-500 mt-1">General, Cardiology, Respiratory, Diabetes, Orthopedic, Pediatrics, Emergency</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-5 text-center">
                <div className="h-10 w-10 rounded-xl bg-purple-100 flex items-center justify-center mx-auto mb-3">
                  <Brain className="h-5 w-5 text-purple-600" />
                </div>
                <h3 className="font-semibold text-sm text-gray-900">AI-Powered CDSS</h3>
                <p className="text-xs text-gray-500 mt-1">Differential diagnosis, NEWS2, drug interactions, 50+ interaction pairs, LOS prediction</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-5 text-center">
                <div className="h-10 w-10 rounded-xl bg-emerald-100 flex items-center justify-center mx-auto mb-3">
                  <Stethoscope className="h-5 w-5 text-emerald-600" />
                </div>
                <h3 className="font-semibold text-sm text-gray-900">55+ ICD-10 Codes</h3>
                <p className="text-xs text-gray-500 mt-1">Integrated ICD-10 search, auto-save drafts, order entry for meds, labs, and radiology</p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}
