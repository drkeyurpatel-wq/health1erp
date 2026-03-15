"use client";
import React, { useEffect, useState } from "react";
import {
  Activity, BedDouble, TrendingUp, TrendingDown,
  Users, Clock, AlertTriangle, CheckCircle2,
  BarChart3, ArrowUpRight, ArrowDownRight, Minus,
  Heart, Stethoscope, FileText, DollarSign,
} from "lucide-react";
import api from "@/lib/api";

interface QualitySummary {
  census: {
    current_inpatients: number;
    total_beds: number;
    occupied_beds: number;
    available_beds: number;
    occupancy_percent: number;
    occupancy_status: string;
  };
  thirty_day_metrics: {
    admissions: number;
    discharges: number;
    opd_encounters: number;
    new_patients: number;
    total_revenue: number;
  };
  today: {
    appointments: number;
  };
  quality_indicators: Record<string, string>;
}

interface ReadmissionData {
  total_discharges: number;
  readmissions: number;
  readmission_rate_percent: number;
  benchmark: string;
}

interface LOSData {
  total_admissions: number;
  average_los_days: number;
  median_los_days: number;
  max_los_days: number;
  distribution: Record<string, number>;
  benchmark: string;
}

interface BedOccupancy {
  total_beds: number;
  occupied_beds: number;
  available_beds: number;
  overall_occupancy_percent: number;
  by_ward: Array<{
    ward_name: string;
    total_beds: number;
    occupied: number;
    available: number;
    occupancy_percent: number;
  }>;
  status: string;
}

interface DoctorPerf {
  doctor_name: string;
  total_encounters: number;
  signed_encounters: number;
  documentation_completion_rate: number;
}

export default function QualityDashboard() {
  const [summary, setSummary] = useState<QualitySummary | null>(null);
  const [readmission, setReadmission] = useState<ReadmissionData | null>(null);
  const [los, setLOS] = useState<LOSData | null>(null);
  const [bedOccupancy, setBedOccupancy] = useState<BedOccupancy | null>(null);
  const [doctors, setDoctors] = useState<DoctorPerf[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [sumRes, readmitRes, losRes, bedRes, docRes] = await Promise.allSettled([
          api.get("/quality/summary-dashboard"),
          api.get("/quality/readmission-rates"),
          api.get("/quality/length-of-stay"),
          api.get("/quality/bed-occupancy"),
          api.get("/quality/doctor-performance"),
        ]);
        if (sumRes.status === "fulfilled") setSummary(sumRes.value.data);
        if (readmitRes.status === "fulfilled") setReadmission(readmitRes.value.data);
        if (losRes.status === "fulfilled") setLOS(losRes.value.data);
        if (bedRes.status === "fulfilled") setBedOccupancy(bedRes.value.data);
        if (docRes.status === "fulfilled") setDoctors(docRes.value.data.doctors || []);
      } catch (e) {
        console.error("Quality data load failed:", e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-6 animate-pulse">
        <div className="h-8 w-64 bg-gray-200 rounded" />
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-gray-100 rounded-2xl" />)}
        </div>
        <div className="grid grid-cols-2 gap-4">
          {[1, 2].map(i => <div key={i} className="h-64 bg-gray-100 rounded-2xl" />)}
        </div>
      </div>
    );
  }

  const occupancyColor = (pct: number) =>
    pct > 90 ? "text-red-600" : pct > 75 ? "text-amber-600" : "text-emerald-600";

  const occupancyBg = (pct: number) =>
    pct > 90 ? "bg-red-500" : pct > 75 ? "bg-amber-500" : "bg-emerald-500";

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Activity className="h-6 w-6 text-blue-600" />
            Quality Metrics & Analytics
          </h1>
          <p className="text-sm text-gray-500 mt-1">Hospital performance indicators and clinical quality tracking</p>
        </div>
        <div className="text-xs text-gray-400 bg-gray-50 px-3 py-1.5 rounded-lg">
          Last 30 days
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <KPICard
          title="Bed Occupancy"
          value={`${bedOccupancy?.overall_occupancy_percent ?? summary?.census?.occupancy_percent ?? 0}%`}
          subtitle={`${summary?.census?.occupied_beds ?? 0} / ${summary?.census?.total_beds ?? 0} beds`}
          icon={BedDouble}
          color={occupancyColor(summary?.census?.occupancy_percent ?? 0)}
          bgColor="bg-blue-50"
          trend={summary?.census?.occupancy_percent && summary.census.occupancy_percent > 85 ? "warning" : "good"}
        />
        <KPICard
          title="30-Day Readmission"
          value={`${readmission?.readmission_rate_percent ?? 0}%`}
          subtitle={`${readmission?.readmissions ?? 0} of ${readmission?.total_discharges ?? 0} discharges`}
          icon={TrendingDown}
          color={(readmission?.readmission_rate_percent ?? 0) > 15 ? "text-red-600" : "text-emerald-600"}
          bgColor="bg-emerald-50"
          trend={(readmission?.readmission_rate_percent ?? 0) > 15 ? "bad" : "good"}
        />
        <KPICard
          title="Avg Length of Stay"
          value={`${los?.average_los_days ?? 0} days`}
          subtitle={`Median: ${los?.median_los_days ?? 0} days`}
          icon={Clock}
          color="text-purple-600"
          bgColor="bg-purple-50"
          trend={(los?.average_los_days ?? 0) > 7 ? "warning" : "good"}
        />
        <KPICard
          title="OPD Encounters"
          value={`${summary?.thirty_day_metrics?.opd_encounters ?? 0}`}
          subtitle={`${summary?.thirty_day_metrics?.new_patients ?? 0} new patients`}
          icon={Stethoscope}
          color="text-blue-600"
          bgColor="bg-blue-50"
          trend="neutral"
        />
      </div>

      {/* Second row: Census + Revenue */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <KPICard
          title="Current Inpatients"
          value={`${summary?.census?.current_inpatients ?? 0}`}
          subtitle={`${summary?.census?.available_beds ?? 0} beds available`}
          icon={Users}
          color="text-indigo-600"
          bgColor="bg-indigo-50"
          trend="neutral"
        />
        <KPICard
          title="Admissions (30d)"
          value={`${summary?.thirty_day_metrics?.admissions ?? 0}`}
          subtitle={`${summary?.thirty_day_metrics?.discharges ?? 0} discharges`}
          icon={ArrowUpRight}
          color="text-teal-600"
          bgColor="bg-teal-50"
          trend="neutral"
        />
        <KPICard
          title="Today's Appointments"
          value={`${summary?.today?.appointments ?? 0}`}
          subtitle="Scheduled for today"
          icon={FileText}
          color="text-amber-600"
          bgColor="bg-amber-50"
          trend="neutral"
        />
        <KPICard
          title="Revenue (30d)"
          value={`₹${((summary?.thirty_day_metrics?.total_revenue ?? 0) / 100000).toFixed(1)}L`}
          subtitle="Total billing"
          icon={DollarSign}
          color="text-emerald-600"
          bgColor="bg-emerald-50"
          trend="neutral"
        />
      </div>

      {/* Ward-wise Bed Occupancy */}
      {bedOccupancy && bedOccupancy.by_ward.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <h2 className="text-sm font-bold text-gray-900 flex items-center gap-2 mb-4">
            <BedDouble className="h-4 w-4 text-blue-600" />
            Ward-wise Bed Occupancy
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {bedOccupancy.by_ward.map((ward) => (
              <div key={ward.ward_name} className="border border-gray-100 rounded-xl p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">{ward.ward_name}</span>
                  <span className={`text-sm font-bold ${occupancyColor(ward.occupancy_percent)}`}>
                    {ward.occupancy_percent}%
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${occupancyBg(ward.occupancy_percent)}`}
                    style={{ width: `${Math.min(ward.occupancy_percent, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between mt-1.5 text-[10px] text-gray-400">
                  <span>{ward.occupied}/{ward.total_beds} occupied</span>
                  <span>{ward.available} available</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Length of Stay Distribution + Doctor Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* LOS Distribution */}
        {los && los.distribution && (
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="text-sm font-bold text-gray-900 flex items-center gap-2 mb-4">
              <Clock className="h-4 w-4 text-purple-600" />
              Length of Stay Distribution
            </h2>
            <div className="space-y-3">
              {Object.entries(los.distribution).map(([range, count]) => {
                const maxCount = Math.max(...Object.values(los.distribution), 1);
                const pct = (count / maxCount) * 100;
                return (
                  <div key={range} className="flex items-center gap-3">
                    <span className="text-xs text-gray-500 w-20 text-right">{range.replace(/_/g, " ")}</span>
                    <div className="flex-1 h-6 bg-gray-50 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full flex items-center justify-end px-2 transition-all"
                        style={{ width: `${Math.max(pct, 8)}%` }}
                      >
                        <span className="text-[10px] text-white font-bold">{count}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-3 pt-3 border-t border-gray-100 flex justify-between text-xs text-gray-400">
              <span>Avg: {los.average_los_days} days</span>
              <span>Median: {los.median_los_days} days</span>
              <span>Max: {los.max_los_days} days</span>
            </div>
          </div>
        )}

        {/* Doctor Performance */}
        {doctors.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200 p-5">
            <h2 className="text-sm font-bold text-gray-900 flex items-center gap-2 mb-4">
              <Stethoscope className="h-4 w-4 text-blue-600" />
              Doctor Performance (30 days)
            </h2>
            <div className="space-y-2 max-h-[320px] overflow-y-auto">
              {doctors.slice(0, 10).map((doc) => (
                <div key={doc.doctor_name} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50">
                  <div>
                    <span className="text-sm font-medium text-gray-900">{doc.doctor_name}</span>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-[10px] text-gray-400">{doc.total_encounters} encounters</span>
                      <span className="text-[10px] text-gray-400">{doc.signed_encounters} signed</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          doc.documentation_completion_rate >= 90 ? "bg-emerald-500" :
                          doc.documentation_completion_rate >= 70 ? "bg-amber-500" : "bg-red-500"
                        }`}
                        style={{ width: `${doc.documentation_completion_rate}%` }}
                      />
                    </div>
                    <span className={`text-xs font-bold ${
                      doc.documentation_completion_rate >= 90 ? "text-emerald-600" :
                      doc.documentation_completion_rate >= 70 ? "text-amber-600" : "text-red-600"
                    }`}>
                      {doc.documentation_completion_rate}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Quality Benchmarks */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <h2 className="text-sm font-bold text-gray-900 flex items-center gap-2 mb-4">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          Quality Benchmarks & Targets
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <BenchmarkCard
            label="Bed Occupancy"
            target="80-85%"
            actual={`${summary?.census?.occupancy_percent ?? 0}%`}
            met={(summary?.census?.occupancy_percent ?? 0) >= 75 && (summary?.census?.occupancy_percent ?? 0) <= 90}
          />
          <BenchmarkCard
            label="30-Day Readmission"
            target="<15%"
            actual={`${readmission?.readmission_rate_percent ?? 0}%`}
            met={(readmission?.readmission_rate_percent ?? 0) < 15}
          />
          <BenchmarkCard
            label="Average LOS"
            target="4-5 days"
            actual={`${los?.average_los_days ?? 0} days`}
            met={(los?.average_los_days ?? 0) <= 6}
          />
          <BenchmarkCard
            label="Documentation Rate"
            target="100%"
            actual={doctors.length > 0 ? `${Math.round(doctors.reduce((s, d) => s + d.documentation_completion_rate, 0) / doctors.length)}%` : "N/A"}
            met={doctors.length > 0 && doctors.reduce((s, d) => s + d.documentation_completion_rate, 0) / doctors.length >= 90}
          />
        </div>
      </div>
    </div>
  );
}

function KPICard({
  title, value, subtitle, icon: Icon, color, bgColor, trend,
}: {
  title: string; value: string; subtitle: string;
  icon: any; color: string; bgColor: string;
  trend: "good" | "bad" | "warning" | "neutral";
}) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <div className={`h-10 w-10 rounded-xl ${bgColor} flex items-center justify-center`}>
          <Icon className={`h-5 w-5 ${color}`} />
        </div>
        {trend === "good" && <span className="text-[10px] bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded-full font-medium">On Track</span>}
        {trend === "bad" && <span className="text-[10px] bg-red-50 text-red-600 px-2 py-0.5 rounded-full font-medium">Needs Attention</span>}
        {trend === "warning" && <span className="text-[10px] bg-amber-50 text-amber-600 px-2 py-0.5 rounded-full font-medium">Monitor</span>}
      </div>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>
      <p className="text-[10px] text-gray-300 mt-1">{title}</p>
    </div>
  );
}

function BenchmarkCard({
  label, target, actual, met,
}: {
  label: string; target: string; actual: string; met: boolean;
}) {
  return (
    <div className={`rounded-xl p-3 border ${met ? "border-emerald-200 bg-emerald-50/50" : "border-red-200 bg-red-50/50"}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-gray-700">{label}</span>
        {met ? (
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
        ) : (
          <AlertTriangle className="h-4 w-4 text-red-500" />
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <span className={`text-lg font-bold ${met ? "text-emerald-600" : "text-red-600"}`}>{actual}</span>
        <span className="text-[10px] text-gray-400">target: {target}</span>
      </div>
    </div>
  );
}
