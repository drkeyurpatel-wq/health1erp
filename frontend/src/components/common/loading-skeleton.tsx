"use client";
import React from "react";

export function PageSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="flex items-center justify-between">
        <div>
          <div className="h-7 w-48 bg-gray-200 rounded-lg" />
          <div className="h-4 w-64 bg-gray-100 rounded mt-2" />
        </div>
        <div className="h-10 w-36 bg-gray-200 rounded-lg" />
      </div>
      <div className="grid grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100">
            <div className="h-4 w-24 bg-gray-100 rounded mb-3" />
            <div className="h-8 w-16 bg-gray-200 rounded" />
          </div>
        ))}
      </div>
      <div className="bg-white rounded-2xl border border-gray-100 p-6">
        <div className="h-5 w-32 bg-gray-200 rounded mb-4" />
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex items-center gap-4 py-3 border-b border-gray-50">
            <div className="h-4 w-20 bg-gray-100 rounded" />
            <div className="h-4 w-32 bg-gray-100 rounded" />
            <div className="h-4 w-24 bg-gray-100 rounded" />
            <div className="h-4 w-16 bg-gray-100 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function CardSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-pulse">
      {[...Array(count)].map((_, i) => (
        <div key={i} className="bg-white rounded-2xl p-6 border border-gray-100">
          <div className="h-4 w-24 bg-gray-100 rounded mb-3" />
          <div className="h-8 w-20 bg-gray-200 rounded mb-2" />
          <div className="h-3 w-32 bg-gray-50 rounded" />
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="animate-pulse">
      <div className="flex gap-4 py-3 border-b border-gray-100">
        {[...Array(cols)].map((_, i) => <div key={i} className="h-4 w-20 bg-gray-200 rounded" />)}
      </div>
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="flex gap-4 py-3.5 border-b border-gray-50">
          {[...Array(cols)].map((_, j) => <div key={j} className="h-4 w-20 bg-gray-100 rounded" />)}
        </div>
      ))}
    </div>
  );
}
