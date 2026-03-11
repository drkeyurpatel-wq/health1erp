"use client";
import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

// Sample data - in production this comes from API
const sampleData = [
  { month: "Jan", revenue: 1250000, collections: 1100000 },
  { month: "Feb", revenue: 1380000, collections: 1200000 },
  { month: "Mar", revenue: 1520000, collections: 1350000 },
  { month: "Apr", revenue: 1410000, collections: 1280000 },
  { month: "May", revenue: 1680000, collections: 1500000 },
  { month: "Jun", revenue: 1590000, collections: 1450000 },
];

export function RevenueChart() {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={sampleData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} tickFormatter={v => `${(v / 100000).toFixed(0)}L`} />
          <Tooltip formatter={(value: number) => `Rs. ${value.toLocaleString("en-IN")}`} />
          <Legend />
          <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" radius={[4, 4, 0, 0]} />
          <Bar dataKey="collections" fill="#22c55e" name="Collections" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
