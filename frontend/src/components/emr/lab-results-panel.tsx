"use client";
import React, { useEffect, useState, useCallback } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  FlaskConical, AlertTriangle, CheckCircle, Clock,
  ChevronDown, ChevronUp, RefreshCw, Brain, ExternalLink,
} from "lucide-react";
import api from "@/lib/api";

interface LabResultData {
  result_id: string;
  test_name: string;
  test_code: string | null;
  category: string | null;
  result_value: string | null;
  result_text: string | null;
  unit: string | null;
  normal_range: Record<string, any> | null;
  is_abnormal: boolean;
  verified_at: string | null;
  ai_interpretation: string | null;
}

interface LabOrderData {
  order_id: string;
  order_date: string | null;
  priority: string;
  status: string;
  results: LabResultData[];
}

interface LabResultsPanelProps {
  patientId: string;
  onResultCount?: (count: number, abnormalCount: number) => void;
}

export function LabResultsPanel({ patientId, onResultCount }: LabResultsPanelProps) {
  const [orders, setOrders] = useState<LabOrderData[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedOrders, setExpandedOrders] = useState<Set<string>>(new Set());
  const [hasAbnormal, setHasAbnormal] = useState(false);

  const loadResults = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/laboratory/patient/${patientId}/results?include_pending=true`);
      setOrders(data.orders || []);
      setHasAbnormal(data.has_abnormal || false);

      const totalResults = (data.orders || []).reduce(
        (sum: number, o: LabOrderData) => sum + o.results.length, 0
      );
      const abnormalResults = (data.orders || []).reduce(
        (sum: number, o: LabOrderData) => sum + o.results.filter((r: LabResultData) => r.is_abnormal).length, 0
      );
      onResultCount?.(totalResults, abnormalResults);

      // Auto-expand first order if any
      if (data.orders?.length > 0) {
        setExpandedOrders(new Set([data.orders[0].order_id]));
      }
    } catch {
      // silently fail — non-critical
    } finally {
      setLoading(false);
    }
  }, [patientId, onResultCount]);

  useEffect(() => { loadResults(); }, [loadResults]);

  const toggleOrder = (orderId: string) => {
    setExpandedOrders(prev => {
      const next = new Set(prev);
      if (next.has(orderId)) next.delete(orderId);
      else next.add(orderId);
      return next;
    });
  };

  const formatNormalRange = (range: Record<string, any> | null): string => {
    if (!range) return "-";
    if (range.min !== undefined && range.max !== undefined) return `${range.min} - ${range.max}`;
    if (range.text) return range.text;
    return JSON.stringify(range);
  };

  if (loading) {
    return (
      <div className="space-y-2 animate-pulse">
        {[1, 2, 3].map(i => <div key={i} className="h-10 bg-gray-100 rounded-lg" />)}
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="text-center py-6">
        <FlaskConical className="h-8 w-8 text-gray-300 mx-auto mb-2" />
        <p className="text-sm text-gray-500">No lab results available</p>
        <p className="text-xs text-gray-400 mt-1">Results will appear here once completed</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Summary bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant={hasAbnormal ? "danger" : "success"} dot>
            {orders.length} order{orders.length !== 1 ? "s" : ""}
          </Badge>
          {hasAbnormal && (
            <Badge variant="danger">
              <AlertTriangle className="h-3 w-3 mr-1" />Abnormal results
            </Badge>
          )}
        </div>
        <Button size="sm" variant="ghost" onClick={loadResults} className="h-7">
          <RefreshCw className="h-3 w-3 mr-1" />Refresh
        </Button>
      </div>

      {/* Order list */}
      {orders.map(order => (
        <div key={order.order_id} className="border border-gray-200 rounded-xl overflow-hidden">
          {/* Order header */}
          <button
            onClick={() => toggleOrder(order.order_id)}
            className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center gap-2">
              <FlaskConical className="h-4 w-4 text-blue-500" />
              <span className="text-sm font-medium">
                {order.order_date
                  ? new Date(order.order_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })
                  : "Unknown date"}
              </span>
              <Badge variant={order.status === "Completed" ? "success" : "warning"} className="text-[10px]">
                {order.status}
              </Badge>
              {order.priority !== "Routine" && (
                <Badge variant="danger" className="text-[10px]">{order.priority}</Badge>
              )}
              <span className="text-xs text-gray-500">{order.results.length} test{order.results.length !== 1 ? "s" : ""}</span>
            </div>
            {expandedOrders.has(order.order_id) ? (
              <ChevronUp className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronDown className="h-4 w-4 text-gray-400" />
            )}
          </button>

          {/* Results table */}
          {expandedOrders.has(order.order_id) && (
            <div className="p-3">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs text-gray-500 uppercase border-b border-gray-100">
                    <th className="text-left py-2 font-medium">Test</th>
                    <th className="text-left py-2 font-medium">Result</th>
                    <th className="text-left py-2 font-medium">Unit</th>
                    <th className="text-left py-2 font-medium">Normal Range</th>
                    <th className="text-center py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {order.results.map(result => (
                    <tr
                      key={result.result_id}
                      className={`border-b border-gray-50 ${result.is_abnormal ? "bg-red-50/50" : ""}`}
                    >
                      <td className="py-2">
                        <div className="font-medium text-gray-900">{result.test_name}</div>
                        {result.test_code && (
                          <span className="text-[10px] text-gray-400">{result.test_code}</span>
                        )}
                      </td>
                      <td className={`py-2 font-mono ${result.is_abnormal ? "text-red-700 font-bold" : "text-gray-700"}`}>
                        {result.result_value || result.result_text || "-"}
                      </td>
                      <td className="py-2 text-gray-500">{result.unit || "-"}</td>
                      <td className="py-2 text-gray-500 text-xs">{formatNormalRange(result.normal_range)}</td>
                      <td className="py-2 text-center">
                        {result.is_abnormal ? (
                          <Badge variant="danger" className="text-[10px]">
                            <AlertTriangle className="h-2.5 w-2.5 mr-0.5" />Abnormal
                          </Badge>
                        ) : result.result_value ? (
                          <Badge variant="success" className="text-[10px]">
                            <CheckCircle className="h-2.5 w-2.5 mr-0.5" />Normal
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="text-[10px]">
                            <Clock className="h-2.5 w-2.5 mr-0.5" />Pending
                          </Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* AI interpretation if available */}
              {order.results.some(r => r.ai_interpretation) && (
                <div className="mt-3 bg-blue-50 rounded-lg p-3 border border-blue-100">
                  <div className="flex items-center gap-1 mb-1">
                    <Brain className="h-3.5 w-3.5 text-blue-600" />
                    <span className="text-xs font-semibold text-blue-800">AI Interpretation</span>
                  </div>
                  {order.results.filter(r => r.ai_interpretation).map(r => (
                    <p key={r.result_id} className="text-xs text-blue-700 whitespace-pre-wrap">
                      {r.ai_interpretation}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
