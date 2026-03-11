"use client";
import React, { useEffect, useState, useCallback } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Modal } from "@/components/ui/modal";
import {
  FlaskConical,
  Brain,
  Search,
  Plus,
  CheckCircle,
  Clock,
  Activity,
  Beaker,
  Eye,
  Play,
  ClipboardList,
} from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

const COMMON_TESTS = [
  { id: "cbc", name: "CBC (Complete Blood Count)" },
  { id: "blood_sugar", name: "Blood Sugar" },
  { id: "lft", name: "LFT (Liver Function Test)" },
  { id: "kft", name: "KFT (Kidney Function Test)" },
  { id: "thyroid", name: "Thyroid Profile" },
  { id: "lipid", name: "Lipid Profile" },
  { id: "urine", name: "Urine Analysis" },
  { id: "ecg", name: "ECG" },
  { id: "hba1c", name: "HbA1c" },
];

interface ResultEntry {
  test_name: string;
  normal_range: string;
  value: string;
  abnormal: boolean;
}

export default function LaboratoryPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [tab, setTab] = useState("all");
  const [search, setSearch] = useState("");
  const [interpretingId, setInterpretingId] = useState<string | null>(null);
  const [interpretation, setInterpretation] = useState<Record<string, string>>({});
  const [showNewOrder, setShowNewOrder] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newOrder, setNewOrder] = useState({
    patient_id: "",
    priority: "Routine",
    notes: "",
  });
  const [selectedTests, setSelectedTests] = useState<string[]>([]);
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null);

  // Enter Results modal state
  const [showResultsModal, setShowResultsModal] = useState(false);
  const [resultsOrder, setResultsOrder] = useState<any>(null);
  const [resultEntries, setResultEntries] = useState<ResultEntry[]>([]);
  const [submittingResults, setSubmittingResults] = useState(false);

  // View Results modal state
  const [showViewResults, setShowViewResults] = useState(false);
  const [viewResultsData, setViewResultsData] = useState<any>(null);

  const { toast } = useToast();

  const loadOrders = useCallback(() => {
    setLoading(true);
    api
      .get("/laboratory/orders")
      .then((r) => setOrders(Array.isArray(r.data) ? r.data : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  const filtered = orders
    .filter((o) => {
      if (tab === "pending")
        return ["Ordered", "SampleCollected", "InProgress"].includes(o.status);
      if (tab === "completed") return o.status === "Completed";
      return true;
    })
    .filter(
      (o) =>
        !search ||
        o.id?.toLowerCase().includes(search.toLowerCase()) ||
        o.patient_name?.toLowerCase().includes(search.toLowerCase())
    );

  const statusColor: Record<string, "warning" | "default" | "success" | "danger" | "secondary"> =
    {
      Ordered: "warning",
      SampleCollected: "default",
      InProgress: "info" as any,
      Completed: "success",
      Cancelled: "danger",
    };

  const pendingCount = orders.filter((o) =>
    ["Ordered", "SampleCollected", "InProgress"].includes(o.status)
  ).length;
  const inProgressCount = orders.filter((o) => o.status === "InProgress").length;
  const completedTodayCount = orders.filter((o) => {
    if (o.status !== "Completed") return false;
    try {
      const date = new Date(o.completed_date || o.updated_at);
      const today = new Date();
      return date.toDateString() === today.toDateString();
    } catch {
      return false;
    }
  }).length;

  const handleInterpret = async (orderId: string) => {
    setInterpretingId(orderId);
    try {
      const { data } = await api.get(`/laboratory/results/${orderId}/ai-interpretation`);
      setInterpretation((prev) => ({
        ...prev,
        [orderId]:
          data.interpretation || data.ai_interpretation || "No interpretation available.",
      }));
      toast("success", "AI Analysis Complete", "Lab results have been interpreted");
    } catch {
      // Fallback to POST endpoint
      try {
        const { data } = await api.post(`/laboratory/orders/${orderId}/interpret`);
        setInterpretation((prev) => ({
          ...prev,
          [orderId]:
            data.interpretation || data.ai_interpretation || "No interpretation available.",
        }));
        toast("success", "AI Analysis Complete", "Lab results have been interpreted");
      } catch {
        setInterpretation((prev) => ({
          ...prev,
          [orderId]: "AI interpretation unavailable. Check AI service configuration.",
        }));
        toast("warning", "AI Unavailable", "Interpretation service is not configured");
      }
    } finally {
      setInterpretingId(null);
    }
  };

  const toggleTest = (testId: string) => {
    setSelectedTests((prev) =>
      prev.includes(testId) ? prev.filter((t) => t !== testId) : [...prev, testId]
    );
  };

  const handleCreateOrder = async () => {
    if (!newOrder.patient_id.trim()) {
      toast("error", "Error", "Patient ID is required");
      return;
    }
    if (selectedTests.length === 0) {
      toast("error", "Error", "Select at least one test");
      return;
    }
    try {
      await api.post("/laboratory/orders", {
        patient_id: newOrder.patient_id,
        test_ids: selectedTests,
        priority: newOrder.priority,
        notes: newOrder.notes || undefined,
      });
      toast("success", "Order Created", "Lab order has been placed");
      setShowNewOrder(false);
      setNewOrder({ patient_id: "", priority: "Routine", notes: "" });
      setSelectedTests([]);
      loadOrders();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not create order");
    }
  };

  const handleStatusUpdate = async (orderId: string, action: string) => {
    setUpdatingStatus(orderId);
    try {
      await api.post(`/laboratory/orders/${orderId}/status`, { action });
      toast("success", "Status Updated", `Order status updated successfully`);
      loadOrders();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not update status");
    } finally {
      setUpdatingStatus(null);
    }
  };

  const openEnterResults = (order: any) => {
    setResultsOrder(order);
    const tests = Array.isArray(order.tests)
      ? order.tests
      : order.test_ids
      ? Array.isArray(order.test_ids)
        ? order.test_ids
        : [order.test_ids]
      : [];
    setResultEntries(
      tests.map((t: any) => ({
        test_name: typeof t === "string" ? (COMMON_TESTS.find((ct) => ct.id === t)?.name || t) : t.name || t.test_name || "",
        normal_range: typeof t === "object" ? t.normal_range || "" : "",
        value: "",
        abnormal: false,
      }))
    );
    setShowResultsModal(true);
  };

  const updateResultEntry = (index: number, field: keyof ResultEntry, value: any) => {
    setResultEntries((prev) =>
      prev.map((entry, i) => (i === index ? { ...entry, [field]: value } : entry))
    );
  };

  const handleSubmitResults = async () => {
    if (!resultsOrder) return;
    setSubmittingResults(true);
    try {
      await api.post("/laboratory/results", {
        order_id: resultsOrder.id,
        results: resultEntries.map((entry) => ({
          test_name: entry.test_name,
          value: entry.value,
          normal_range: entry.normal_range,
          abnormal: entry.abnormal,
        })),
      });
      toast("success", "Results Saved", "Lab results have been recorded");
      setShowResultsModal(false);
      setResultsOrder(null);
      setResultEntries([]);
      loadOrders();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not save results");
    } finally {
      setSubmittingResults(false);
    }
  };

  const handleViewResults = async (order: any) => {
    setViewResultsData(order);
    setShowViewResults(true);
  };

  const renderActionButtons = (order: any) => {
    const isUpdating = updatingStatus === order.id;
    switch (order.status) {
      case "Ordered":
        return (
          <Button
            size="sm"
            variant="outline"
            loading={isUpdating}
            onClick={() => handleStatusUpdate(order.id, "collect_sample")}
          >
            <Beaker className="h-3.5 w-3.5 mr-1" />
            Collect Sample
          </Button>
        );
      case "SampleCollected":
        return (
          <Button
            size="sm"
            variant="outline"
            loading={isUpdating}
            onClick={() => handleStatusUpdate(order.id, "start_processing")}
          >
            <Play className="h-3.5 w-3.5 mr-1" />
            Start Processing
          </Button>
        );
      case "InProgress":
        return (
          <Button
            size="sm"
            variant="default"
            onClick={() => openEnterResults(order)}
          >
            <ClipboardList className="h-3.5 w-3.5 mr-1" />
            Enter Results
          </Button>
        );
      case "Completed":
        return (
          <div className="flex items-center gap-2">
            <Button size="sm" variant="ghost" onClick={() => handleViewResults(order)}>
              <Eye className="h-3.5 w-3.5 mr-1" />
              View Results
            </Button>
            <Button
              size="sm"
              variant="ghost"
              loading={interpretingId === order.id}
              onClick={() => handleInterpret(order.id)}
            >
              <Brain className="h-3.5 w-3.5 mr-1" />
              AI Interpret
            </Button>
          </div>
        );
      default:
        return null;
    }
  };

  const renderOrdersTable = () => {
    if (loading) {
      return (
        <div className="space-y-3 animate-pulse">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-100 rounded" />
          ))}
        </div>
      );
    }
    if (filtered.length === 0) {
      return (
        <EmptyState
          icon="laboratory"
          title="No orders found"
          description={
            search ? "Try a different search" : "Create a lab order to get started"
          }
        />
      );
    }
    return (
      <table className="data-table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Patient</th>
            <th>Date</th>
            <th>Tests</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map((o: any) => (
            <React.Fragment key={o.id}>
              <tr>
                <td>
                  <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">
                    {o.id?.slice(0, 12)}
                  </span>
                </td>
                <td className="text-gray-700">
                  {o.patient_name ||
                    `Patient (${o.patient_id?.slice(0, 8) || "N/A"})`}
                </td>
                <td className="text-gray-500">{formatDateTime(o.order_date || o.created_at)}</td>
                <td>
                  <div className="flex flex-wrap gap-1">
                    {(Array.isArray(o.tests)
                      ? o.tests.map((t: any) =>
                          typeof t === "string"
                            ? COMMON_TESTS.find((ct) => ct.id === t)?.name || t
                            : t.name || t.test_name || ""
                        )
                      : Array.isArray(o.test_ids)
                      ? o.test_ids.map(
                          (id: string) =>
                            COMMON_TESTS.find((ct) => ct.id === id)?.name || id
                        )
                      : []
                    )
                      .slice(0, 3)
                      .map((name: string, idx: number) => (
                        <Badge key={idx} variant="secondary">
                          {name}
                        </Badge>
                      ))}
                    {((Array.isArray(o.tests) ? o.tests : o.test_ids) || []).length > 3 && (
                      <Badge variant="secondary">
                        +{((Array.isArray(o.tests) ? o.tests : o.test_ids) || []).length - 3} more
                      </Badge>
                    )}
                  </div>
                </td>
                <td>
                  <Badge
                    variant={
                      o.priority === "STAT"
                        ? "danger"
                        : o.priority === "Urgent"
                        ? "warning"
                        : "secondary"
                    }
                    dot
                  >
                    {o.priority}
                  </Badge>
                </td>
                <td>
                  <Badge variant={statusColor[o.status] || "secondary"} dot>
                    {o.status}
                  </Badge>
                </td>
                <td>{renderActionButtons(o)}</td>
              </tr>
              {interpretation[o.id] && (
                <tr>
                  <td colSpan={7} className="!py-0">
                    <div className="bg-blue-50 rounded-xl p-4 my-2 border border-blue-100">
                      <div className="flex items-start gap-2">
                        <Brain className="h-4 w-4 text-blue-600 mt-0.5 shrink-0" />
                        <div>
                          <p className="text-xs font-semibold text-blue-800 mb-1">
                            AI Interpretation
                          </p>
                          <p className="text-xs text-blue-700 whitespace-pre-wrap">
                            {interpretation[o.id]}
                          </p>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Laboratory</h1>
          <p className="page-subtitle">Lab orders, results, and AI interpretation</p>
        </div>
        <Button variant="gradient" onClick={() => setShowNewOrder(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Lab Order
        </Button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8 animate-stagger">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600">
              <FlaskConical className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Orders</p>
              <p className="text-2xl font-bold counter-value">{orders.length}</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600">
              <Clock className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Pending</p>
              <p className="text-2xl font-bold counter-value">{pendingCount}</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">In Progress</p>
              <p className="text-2xl font-bold counter-value">{inProgressCount}</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600">
              <CheckCircle className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Completed Today</p>
              <p className="text-2xl font-bold counter-value">{completedTodayCount}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search orders..."
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="all" onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="all">All ({orders.length})</TabsTrigger>
          <TabsTrigger value="pending">Pending ({pendingCount})</TabsTrigger>
          <TabsTrigger value="completed">
            Completed (
            {orders.filter((o) => o.status === "Completed").length})
          </TabsTrigger>
        </TabsList>

        {["all", "pending", "completed"].map((tabVal) => (
          <TabsContent key={tabVal} value={tabVal}>
            <Card>
              <CardContent className="pt-6">{renderOrdersTable()}</CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* New Order Modal */}
      <Modal
        open={showNewOrder}
        onClose={() => setShowNewOrder(false)}
        title="New Lab Order"
        description="Order laboratory tests for a patient"
        size="lg"
      >
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Patient ID *
              </label>
              <Input
                placeholder="Patient UUID"
                value={newOrder.patient_id}
                onChange={(e) => setNewOrder((p) => ({ ...p, patient_id: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Priority</label>
              <select
                className="flex h-10 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                value={newOrder.priority}
                onChange={(e) => setNewOrder((p) => ({ ...p, priority: e.target.value }))}
              >
                <option>Routine</option>
                <option>Urgent</option>
                <option>STAT</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">
              Select Tests *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {COMMON_TESTS.map((test) => (
                <label
                  key={test.id}
                  className={`flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all ${
                    selectedTests.includes(test.id)
                      ? "border-primary-300 bg-primary-50 text-primary-700"
                      : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedTests.includes(test.id)}
                    onChange={() => toggleTest(test.id)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm">{test.name}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">
              Clinical Notes
            </label>
            <textarea
              className="flex min-h-[80px] w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 resize-none"
              placeholder="Enter clinical notes or special instructions..."
              value={newOrder.notes}
              onChange={(e) => setNewOrder((p) => ({ ...p, notes: e.target.value }))}
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => setShowNewOrder(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateOrder} variant="gradient">
            <FlaskConical className="h-4 w-4 mr-2" />
            Create Order
          </Button>
        </div>
      </Modal>

      {/* Enter Results Modal */}
      <Modal
        open={showResultsModal}
        onClose={() => setShowResultsModal(false)}
        title="Enter Lab Results"
        description={`Order: ${resultsOrder?.id?.slice(0, 12) || ""}`}
        size="lg"
      >
        <div className="p-6 space-y-4">
          {resultEntries.length === 0 ? (
            <p className="text-sm text-gray-500">
              No tests found for this order. Results may need to be entered manually.
            </p>
          ) : (
            <div className="space-y-3">
              {resultEntries.map((entry, index) => (
                <div
                  key={index}
                  className="p-4 rounded-xl border border-gray-200 bg-gray-50/50 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      {entry.test_name}
                    </span>
                    {entry.normal_range && (
                      <span className="text-xs text-gray-500">
                        Normal: {entry.normal_range}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <label className="block text-xs text-gray-500 mb-1">Result Value</label>
                      <Input
                        placeholder="Enter result value"
                        value={entry.value}
                        onChange={(e) => updateResultEntry(index, "value", e.target.value)}
                      />
                    </div>
                    <div className="flex items-center gap-2 pt-5">
                      <input
                        type="checkbox"
                        id={`abnormal-${index}`}
                        checked={entry.abnormal}
                        onChange={(e) =>
                          updateResultEntry(index, "abnormal", e.target.checked)
                        }
                        className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                      />
                      <label
                        htmlFor={`abnormal-${index}`}
                        className="text-sm text-gray-600"
                      >
                        Abnormal
                      </label>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => setShowResultsModal(false)}>
            Cancel
          </Button>
          <Button
            variant="gradient"
            onClick={handleSubmitResults}
            loading={submittingResults}
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Save Results
          </Button>
        </div>
      </Modal>

      {/* View Results Modal */}
      <Modal
        open={showViewResults}
        onClose={() => setShowViewResults(false)}
        title="Lab Results"
        description={`Order: ${viewResultsData?.id?.slice(0, 12) || ""}`}
        size="lg"
      >
        <div className="p-6">
          {viewResultsData?.results && Array.isArray(viewResultsData.results) ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Test</th>
                  <th>Result</th>
                  <th>Normal Range</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {viewResultsData.results.map((r: any, idx: number) => (
                  <tr key={idx}>
                    <td className="font-medium">{r.test_name || r.name}</td>
                    <td>{r.value || r.result || "-"}</td>
                    <td className="text-gray-500">{r.normal_range || "-"}</td>
                    <td>
                      {r.abnormal ? (
                        <Badge variant="danger" dot>
                          Abnormal
                        </Badge>
                      ) : (
                        <Badge variant="success" dot>
                          Normal
                        </Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-gray-500">
              No results available for this order yet.
            </p>
          )}
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => setShowViewResults(false)}>
            Close
          </Button>
          {viewResultsData && (
            <Button
              variant="gradient"
              loading={interpretingId === viewResultsData.id}
              onClick={() => {
                handleInterpret(viewResultsData.id);
                setShowViewResults(false);
              }}
            >
              <Brain className="h-4 w-4 mr-2" />
              AI Interpret
            </Button>
          )}
        </div>
      </Modal>
    </AppShell>
  );
}
