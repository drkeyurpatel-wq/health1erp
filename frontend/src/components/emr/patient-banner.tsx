"use client";
import React from "react";
import { Badge } from "@/components/ui/badge";
import {
  Phone, Mail, Droplets, AlertTriangle, ShieldAlert,
  Calendar, Clock, User,
} from "lucide-react";
import type { Patient } from "@/types";

interface PatientBannerProps {
  patient: Patient;
  activeAdmission?: any;
  alertCount?: number;
}

export function PatientBanner({ patient, activeAdmission, alertCount = 0 }: PatientBannerProps) {
  const age = Math.floor(
    (Date.now() - new Date(patient.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)
  );
  const hasAllergies = patient.allergies && patient.allergies.length > 0;

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
      {/* Allergy strip */}
      {hasAllergies && (
        <div className="bg-red-600 px-4 py-1.5 flex items-center gap-2 animate-pulse-ring">
          <ShieldAlert className="h-4 w-4 text-white" />
          <span className="text-white text-xs font-bold tracking-wide uppercase">
            Allergies: {patient.allergies!.join(" | ")}
          </span>
        </div>
      )}

      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left: Patient identity */}
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white text-lg font-bold shadow-lg">
              {patient.first_name[0]}{patient.last_name[0]}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-gray-900">
                  {patient.first_name} {patient.last_name}
                </h1>
                <Badge variant="default"><span className="font-mono text-[11px]">{patient.uhid}</span></Badge>
              </div>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <User className="h-3.5 w-3.5" />
                  {age}y / {patient.gender}
                </span>
                {patient.blood_group && (
                  <span className="flex items-center gap-1">
                    <Droplets className="h-3.5 w-3.5 text-red-400" />
                    {patient.blood_group}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  {new Date(patient.date_of_birth).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
                </span>
                <span className="flex items-center gap-1">
                  <Phone className="h-3.5 w-3.5" />
                  {patient.phone}
                </span>
                {patient.email && (
                  <span className="flex items-center gap-1">
                    <Mail className="h-3.5 w-3.5" />
                    {patient.email}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Right: Status indicators */}
          <div className="flex items-center gap-3">
            {alertCount > 0 && (
              <div className="flex items-center gap-1.5 bg-red-50 text-red-700 px-3 py-2 rounded-xl border border-red-200">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm font-semibold">{alertCount} Alert{alertCount > 1 ? "s" : ""}</span>
              </div>
            )}
            {activeAdmission && (
              <div className="flex items-center gap-1.5 bg-emerald-50 text-emerald-700 px-3 py-2 rounded-xl border border-emerald-200">
                <Clock className="h-4 w-4" />
                <span className="text-sm font-semibold">Admitted</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
