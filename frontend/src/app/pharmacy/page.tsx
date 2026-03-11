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
  Pill,
  CheckCircle,
  Clock,
  AlertTriangle,
  Package,
  Plus,
  Trash2,
  Eye,
  Search,
} from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

interface MedicineRow {
  medicine_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  route: string;
  quantity: string;
  instructions: string;
}

const emptyMedicineRow = (): MedicineRow => ({
  medicine_name: "",
  dosage: "",
  frequency: "Once Daily",
  duration: "",
  route: "Oral",
  quantity: "",
  instructions: "",
});

const FREQUENCIES = [
  "Once Daily",
  "Twice Daily",
  "Thrice Daily",
  "As Needed",
  "Every 6 Hours",
  "Every 8 Hours",
];

const ROUTES = ["Oral", "IV", "IM", "Topical", "Inhalation"];

export default function PharmacyPage() {
  const [prescriptions, setPrescriptions] = useState<any[]>([]);
  const [dispensedList, setDispensedList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [dispensedLoading, setDispensedLoading] = useState(true);
  const [dispensing, setDispensing] = useState<string | null>(null);
  const [lowStockCount, setLowStockCount] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [newPatientId, setNewPatientId] = useState("");
  const [medicineRows, setMedicineRows] = useState<MedicineRow[]>([emptyMedicineRow()]);

  // Drug interactions state
  const [drugSearchInput, setDrugSearchInput] = useState("");
  const [drugInteractionResult, setDrugInteractionResult] = useState<any>(null);
  const [drugInteractionLoading, setDrugInteractionLoading] = useState(false);

  const { toast } = useToast();

  const loadPending = useCallback(() => {
    setLoading(true);
    api
      .get("/pharmacy/prescriptions/pending")
      .then((r) => setPrescriptions(Array.isArray(r.data) ? r.data : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const loadDispensed = useCallback(() => {
    setDispensedLoading(true);
    api
      .get("/pharmacy/prescriptions/dispensed")
      .then((r) => setDispensedList(Array.isArray(r.data) ? r.data : []))
      .catch(() => setDispensedList([]))
      .finally(() => setDispensedLoading(false));
  }, []);

  const loadStats = useCallback(() => {
    api
      .get("/pharmacy/inventory/stats")
      .then((r) => {
        if (r.data) {
          setLowStockCount(r.data.low_stock_count ?? 0);
          setTotalItems(r.data.total_items ?? 0);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    loadPending();
    loadDispensed();
    loadStats();
  }, [loadPending, loadDispensed, loadStats]);

  const dispense = async (id: string) => {
    setDispensing(id);
    try {
      await api.post("/pharmacy/dispense", { prescription_id: id });
      setPrescriptions((prev) => prev.filter((p) => p.id !== id));
      toast("success", "Dispensed", "Prescription has been dispensed successfully");
      loadDispensed();
    } catch (err: any) {
      toast("error", "Dispense Failed", err.response?.data?.detail || "Error dispensing");
    } finally {
      setDispensing(null);
    }
  };

  const addMedicineRow = () => {
    setMedicineRows((prev) => [...prev, emptyMedicineRow()]);
  };

  const removeMedicineRow = (index: number) => {
    setMedicineRows((prev) => prev.filter((_, i) => i !== index));
  };

  const updateMedicineRow = (index: number, field: keyof MedicineRow, value: string) => {
    setMedicineRows((prev) =>
      prev.map((row, i) => (i === index ? { ...row, [field]: value } : row))
    );
  };

  const handleCreatePrescription = async () => {
    if (!newPatientId.trim()) {
      toast("error", "Error", "Patient ID is required");
      return;
    }
    if (medicineRows.length === 0 || !medicineRows[0].medicine_name.trim()) {
      toast("error", "Error", "At least one medicine is required");
      return;
    }
    setCreateLoading(true);
    try {
      await api.post("/pharmacy/prescriptions", {
        patient_id: newPatientId,
        medicines: medicineRows.map((row) => ({
          medicine_name: row.medicine_name,
          dosage: row.dosage,
          frequency: row.frequency,
          duration: row.duration,
          route: row.route,
          quantity: row.quantity ? parseInt(row.quantity) : undefined,
          instructions: row.instructions || undefined,
        })),
      });
      toast("success", "Prescription Created", "New prescription has been created");
      setShowCreateModal(false);
      setNewPatientId("");
      setMedicineRows([emptyMedicineRow()]);
      loadPending();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not create prescription");
    } finally {
      setCreateLoading(false);
    }
  };

  const handleDrugInteractionSearch = async () => {
    const drugs = drugSearchInput
      .split(",")
      .map((d) => d.trim())
      .filter(Boolean);
    if (drugs.length < 2) {
      toast("error", "Error", "Enter at least 2 drug names separated by commas");
      return;
    }
    setDrugInteractionLoading(true);
    setDrugInteractionResult(null);
    try {
      const { data } = await api.get("/pharmacy/drug-interactions", {
        params: { drugs: drugs.join(",") },
      });
      setDrugInteractionResult(data);
    } catch (err: any) {
      toast(
        "error",
        "Error",
        err.response?.data?.detail || "Could not check drug interactions"
      );
    } finally {
      setDrugInteractionLoading(false);
    }
  };

  const dispensedToday = dispensedList.filter((d) => {
    try {
      const date = new Date(d.dispensed_date || d.updated_at);
      const today = new Date();
      return date.toDateString() === today.toDateString();
    } catch {
      return false;
    }
  }).length;

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Pharmacy</h1>
          <p className="page-subtitle">Prescription dispensing and drug management</p>
        </div>
        <Button variant="gradient" onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Prescription
        </Button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8 animate-stagger">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600">
              <Clock className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Pending Prescriptions</p>
              <p className="text-2xl font-bold counter-value">{prescriptions.length}</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600">
              <CheckCircle className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Dispensed Today</p>
              <p className="text-2xl font-bold counter-value">{dispensedToday}</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-red-500 to-red-600">
              <AlertTriangle className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Low Stock Medicines</p>
              <p className="text-2xl font-bold counter-value">{lowStockCount}</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600">
              <Package className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Items</p>
              <p className="text-2xl font-bold counter-value">{totalItems}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="pending">
        <TabsList>
          <TabsTrigger value="pending">
            Pending Prescriptions ({prescriptions.length})
          </TabsTrigger>
          <TabsTrigger value="dispensed">Dispensed ({dispensedList.length})</TabsTrigger>
          <TabsTrigger value="interactions">Drug Interactions</TabsTrigger>
        </TabsList>

        {/* Pending Prescriptions Tab */}
        <TabsContent value="pending">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Pill className="h-4 w-4 text-primary-500" />
                  Pending Prescriptions
                </CardTitle>
                <Badge variant="warning" dot>
                  {prescriptions.length} pending
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3 animate-pulse">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-100 rounded-xl" />
                  ))}
                </div>
              ) : prescriptions.length === 0 ? (
                <EmptyState
                  icon="pharmacy"
                  title="All caught up!"
                  description="No pending prescriptions to dispense"
                />
              ) : (
                <div className="space-y-3">
                  {prescriptions.map((p: any) => (
                    <div
                      key={p.id}
                      className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:border-primary-200 hover:bg-primary-50/30 transition-all"
                    >
                      <div className="flex items-center gap-4">
                        <div className="p-2.5 rounded-xl bg-amber-50 border border-amber-100">
                          <Pill className="h-5 w-5 text-amber-600" />
                        </div>
                        <div>
                          <p className="font-medium text-sm">
                            {p.patient_name || `Patient`}{" "}
                            <span className="text-gray-400 font-mono text-xs">
                              ({p.id?.slice(0, 8)})
                            </span>
                          </p>
                          <div className="flex items-center gap-3 mt-0.5">
                            <p className="text-xs text-gray-500">
                              {formatDateTime(p.prescription_date || p.created_at)}
                            </p>
                            {p.items && (
                              <span className="text-xs text-gray-400">
                                {Array.isArray(p.items) ? p.items.length : p.items} item(s)
                              </span>
                            )}
                          </div>
                        </div>
                        {p.priority && p.priority !== "Normal" && (
                          <Badge
                            variant={p.priority === "Urgent" || p.priority === "STAT" ? "danger" : "warning"}
                            dot
                          >
                            {p.priority}
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="ghost">
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                        <Button
                          size="sm"
                          variant="gradient"
                          loading={dispensing === p.id}
                          onClick={() => dispense(p.id)}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Dispense
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Dispensed Tab */}
        <TabsContent value="dispensed">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-emerald-500" />
                Recently Dispensed
              </CardTitle>
            </CardHeader>
            <CardContent>
              {dispensedLoading ? (
                <div className="space-y-3 animate-pulse">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-12 bg-gray-100 rounded" />
                  ))}
                </div>
              ) : dispensedList.length === 0 ? (
                <EmptyState
                  icon="pharmacy"
                  title="No dispensed prescriptions"
                  description="Dispensed prescriptions will appear here"
                />
              ) : (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Prescription ID</th>
                      <th>Patient</th>
                      <th>Dispensed Date</th>
                      <th>Items</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dispensedList.map((d: any) => (
                      <tr key={d.id}>
                        <td>
                          <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">
                            {d.id?.slice(0, 12)}
                          </span>
                        </td>
                        <td className="text-gray-700">
                          {d.patient_name || `Patient (${d.patient_id?.slice(0, 8) || "N/A"})`}
                        </td>
                        <td className="text-gray-500">
                          {formatDateTime(d.dispensed_date || d.updated_at || d.created_at)}
                        </td>
                        <td>
                          <Badge variant="secondary">
                            {Array.isArray(d.items) ? d.items.length : d.item_count || "-"} item(s)
                          </Badge>
                        </td>
                        <td>
                          <Badge variant="success" dot>
                            Dispensed
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Drug Interactions Tab */}
        <TabsContent value="interactions">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-500" />
                Drug Interaction Checker
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="max-w-xl space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">
                    Enter drug names (comma-separated, at least 2)
                  </label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="e.g. Aspirin, Warfarin"
                      value={drugSearchInput}
                      onChange={(e) => setDrugSearchInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleDrugInteractionSearch();
                      }}
                    />
                    <Button
                      variant="gradient"
                      onClick={handleDrugInteractionSearch}
                      loading={drugInteractionLoading}
                    >
                      <Search className="h-4 w-4 mr-1" />
                      Check
                    </Button>
                  </div>
                </div>
                {drugInteractionResult && (
                  <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
                    <p className="text-sm font-semibold text-blue-800 mb-2">
                      Interaction Results
                    </p>
                    {Array.isArray(drugInteractionResult.interactions) &&
                    drugInteractionResult.interactions.length > 0 ? (
                      <ul className="space-y-2">
                        {drugInteractionResult.interactions.map((item: any, idx: number) => (
                          <li
                            key={idx}
                            className="text-sm text-blue-700 bg-white rounded-lg p-3 border border-blue-100"
                          >
                            <span className="font-medium">{item.drug_pair || item.drugs}</span>
                            {item.severity && (
                              <Badge
                                variant={
                                  item.severity === "High"
                                    ? "danger"
                                    : item.severity === "Moderate"
                                    ? "warning"
                                    : "secondary"
                                }
                                className="ml-2"
                                dot
                              >
                                {item.severity}
                              </Badge>
                            )}
                            <p className="mt-1 text-gray-600">
                              {item.description || item.detail || "Interaction found"}
                            </p>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-blue-700">
                        {drugInteractionResult.message ||
                          "No interactions found between the specified drugs."}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Prescription Modal */}
      <Modal
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create Prescription"
        description="Add a new prescription for a patient"
        size="xl"
      >
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">
              Patient ID *
            </label>
            <Input
              placeholder="Enter Patient UUID"
              value={newPatientId}
              onChange={(e) => setNewPatientId(e.target.value)}
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-600">Medicines *</label>
              <Button size="sm" variant="outline" onClick={addMedicineRow}>
                <Plus className="h-3.5 w-3.5 mr-1" />
                Add Medicine
              </Button>
            </div>
            <div className="space-y-3">
              {medicineRows.map((row, index) => (
                <div
                  key={index}
                  className="p-4 rounded-xl border border-gray-200 bg-gray-50/50 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-gray-500">
                      Medicine #{index + 1}
                    </span>
                    {medicineRows.length > 1 && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeMedicineRow(index)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Medicine Name *</label>
                      <Input
                        placeholder="e.g. Paracetamol"
                        value={row.medicine_name}
                        onChange={(e) =>
                          updateMedicineRow(index, "medicine_name", e.target.value)
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Dosage</label>
                      <Input
                        placeholder="e.g. 500mg"
                        value={row.dosage}
                        onChange={(e) => updateMedicineRow(index, "dosage", e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Frequency</label>
                      <select
                        className="flex h-10 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                        value={row.frequency}
                        onChange={(e) =>
                          updateMedicineRow(index, "frequency", e.target.value)
                        }
                      >
                        {FREQUENCIES.map((f) => (
                          <option key={f} value={f}>
                            {f}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Duration</label>
                      <Input
                        placeholder="e.g. 7 days"
                        value={row.duration}
                        onChange={(e) => updateMedicineRow(index, "duration", e.target.value)}
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Route</label>
                      <select
                        className="flex h-10 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                        value={row.route}
                        onChange={(e) => updateMedicineRow(index, "route", e.target.value)}
                      >
                        {ROUTES.map((r) => (
                          <option key={r} value={r}>
                            {r}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Quantity</label>
                      <Input
                        type="number"
                        placeholder="e.g. 10"
                        value={row.quantity}
                        onChange={(e) => updateMedicineRow(index, "quantity", e.target.value)}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Instructions</label>
                    <Input
                      placeholder="e.g. Take after meals"
                      value={row.instructions}
                      onChange={(e) =>
                        updateMedicineRow(index, "instructions", e.target.value)
                      }
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => setShowCreateModal(false)}>
            Cancel
          </Button>
          <Button variant="gradient" onClick={handleCreatePrescription} loading={createLoading}>
            <Pill className="h-4 w-4 mr-2" />
            Create Prescription
          </Button>
        </div>
      </Modal>
    </AppShell>
  );
}
