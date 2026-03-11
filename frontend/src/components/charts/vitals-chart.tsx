"use client";
import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface VitalsChartProps {
  data: Array<{
    time: string;
    temperature?: number;
    bp_systolic?: number;
    bp_diastolic?: number;
    pulse?: number;
    spo2?: number;
    respiratory_rate?: number;
  }>;
}

export function VitalsChart({ data }: VitalsChartProps) {
  if (!data || data.length === 0) {
    return <div className="h-64 flex items-center justify-center text-gray-400">No vitals data available</div>;
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="time" tick={{ fontSize: 10 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="pulse" stroke="#ef4444" name="Pulse" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="bp_systolic" stroke="#3b82f6" name="BP Systolic" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="bp_diastolic" stroke="#93c5fd" name="BP Diastolic" strokeWidth={1.5} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="spo2" stroke="#22c55e" name="SpO2" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="temperature" stroke="#f59e0b" name="Temp" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="respiratory_rate" stroke="#8b5cf6" name="Resp Rate" strokeWidth={1.5} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
