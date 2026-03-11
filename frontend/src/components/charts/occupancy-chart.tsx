"use client";
import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { WardOccupancy } from "@/types";

interface OccupancyChartProps {
  data: WardOccupancy[];
}

export function OccupancyChart({ data }: OccupancyChartProps) {
  if (!data || data.length === 0) {
    return <div className="h-64 flex items-center justify-center text-gray-400">No occupancy data</div>;
  }

  const chartData = data.map(w => ({
    name: w.ward_name,
    occupancy: w.occupancy_rate,
    occupied: w.occupied,
    available: w.available,
  }));

  const getColor = (rate: number) => {
    if (rate >= 90) return "#ef4444";
    if (rate >= 70) return "#f59e0b";
    return "#22c55e";
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} unit="%" />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={75} />
          <Tooltip formatter={(value: number) => `${value}%`} />
          <Bar dataKey="occupancy" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={getColor(entry.occupancy)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
