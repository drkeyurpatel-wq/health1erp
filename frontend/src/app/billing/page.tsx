"use client";
import React, { useEffect, useState, useCallback, useMemo } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Modal } from "@/components/ui/modal";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  Receipt,
  IndianRupee,
  TrendingUp,
  TrendingDown,
  Clock,
  Plus,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  Trash2,
  Eye,
  CreditCard,
  Search,
  CalendarDays,
  X,
} from "lucide-react";
import { EmptyState } from "@/components/common/empty-state";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

// ── Types ──────────────────────────────────────────────────────────────

interface BillLineItem {
  description: string;
  category: string;
  quantity: number;
  unit_price: number;
}

interface Bill {
  id: string;
  bill_number: string;
  bill_date: string;
  patient_id: string;
  patient_name?: string;
  total_amount: number;
  paid_amount: number;
  balance: number;
  status: string;
  items?: BillLineItem[];
  tax_amount?: number;
  discount_amount?: number;
  subtotal?: number;
  payment_mode?: string;
  notes?: string;
}

// ── Constants ──────────────────────────────────────────────────────────

const SERVICE_TYPES = [
  "Consultation",
  "Room Charges",
  "Lab Test",
  "Medicine",
  "Procedure",
  "Surgery",
  "Nursing",
  "Other",
] as const;

const PAYMENT_MODES = ["Cash", "Card", "UPI", "Insurance", "Bank Transfer"] as const;

const STATUS_TABS = ["All", "Paid", "Pending", "Overdue", "Draft"] as const;

const STATUS_VARIANT: Record<string, "success" | "warning" | "default" | "danger" | "secondary"> = {
  Paid: "success",
  Pending: "warning",
  PartialPaid: "default",
  Overdue: "danger",
  Draft: "secondary",
  Cancelled: "danger",
};

const TAX_RATE = 0.18;

// ── Helper: today as YYYY-MM-DD ────────────────────────────────────────

function todayISO() {
  const d = new Date();
  return d.toISOString().slice(0, 10);
}

// ── Main Page ──────────────────────────────────────────────────────────

export default function BillingPage() {
  const { toast } = useToast();

  // Data
  const [bills, setBills] = useState<Bill[]>([]);
  const [revenue, setRevenue] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [activeTab, setActiveTab] = useState("All");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  // Modals
  const [showCreate, setShowCreate] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [showView, setShowView] = useState(false);
  const [selectedBill, setSelectedBill] = useState<Bill | null>(null);

  // ── Load Data ──────────────────────────────────────────────────────

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.all([
      api
        .get("/billing")
        .then((r) => setBills(Array.isArray(r.data) ? r.data : r.data?.items || []))
        .catch(() => {}),
      api
        .get("/billing/revenue-report")
        .then((r) => setRevenue(r.data))
        .catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // ── Filtered Bills ─────────────────────────────────────────────────

  const filteredBills = useMemo(() => {
    let result = bills;
    if (activeTab !== "All") {
      result = result.filter((b) => b.status === activeTab);
    }
    if (dateFrom) {
      result = result.filter((b) => b.bill_date >= dateFrom);
    }
    if (dateTo) {
      result = result.filter((b) => b.bill_date <= dateTo);
    }
    return result;
  }, [bills, activeTab, dateFrom, dateTo]);

  // ── Revenue Cards ──────────────────────────────────────────────────

  const revenueCards = [
    {
      title: "Total Revenue",
      value: formatCurrency(revenue?.total_revenue || 0),
      icon: IndianRupee,
      color: "from-emerald-500 to-emerald-600",
      change: revenue?.revenue_change_pct ?? 18,
    },
    {
      title: "Collected",
      value: formatCurrency(revenue?.total_collected || 0),
      icon: TrendingUp,
      color: "from-blue-500 to-blue-600",
      change: revenue?.collected_change_pct ?? 12,
    },
    {
      title: "Outstanding",
      value: formatCurrency(revenue?.total_outstanding || 0),
      icon: Clock,
      color: "from-amber-500 to-amber-600",
      change: revenue?.outstanding_change_pct ?? -5,
    },
  ];

  // ── Render ─────────────────────────────────────────────────────────

  return (
    <AppShell>
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Billing</h1>
          <p className="page-subtitle">Revenue tracking and invoice management</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="gradient" onClick={() => setShowCreate(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Generate Bill
          </Button>
        </div>
      </div>

      {/* Revenue Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 animate-stagger">
        {revenueCards.map((card) => {
          const isPositive = card.change >= 0;
          return (
            <div key={card.title} className="stat-card">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-500 font-medium">{card.title}</p>
                  <p className="text-2xl font-bold mt-2 counter-value">{card.value}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {isPositive ? (
                      <ArrowUpRight className="h-3.5 w-3.5 text-emerald-500" />
                    ) : (
                      <ArrowDownRight className="h-3.5 w-3.5 text-red-500" />
                    )}
                    <span
                      className={`text-xs font-medium ${
                        isPositive ? "text-emerald-600" : "text-red-600"
                      }`}
                    >
                      {isPositive ? "+" : ""}
                      {card.change}%
                    </span>
                    <span className="text-xs text-gray-400 ml-1">vs last month</span>
                  </div>
                </div>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${card.color} shadow-sm`}>
                  <card.icon className="h-5 w-5 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Bills Table with Tabs & Filters */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>Bills</CardTitle>
            <Badge variant="secondary">{filteredBills.length} bills</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {/* Tabs & Date Range */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between mb-4">
              <TabsList>
                {STATUS_TABS.map((tab) => (
                  <TabsTrigger key={tab} value={tab}>
                    {tab}
                  </TabsTrigger>
                ))}
              </TabsList>

              <div className="flex items-center gap-2">
                <CalendarDays className="h-4 w-4 text-gray-400" />
                <Input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="w-40"
                  placeholder="From"
                />
                <span className="text-gray-400 text-sm">to</span>
                <Input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="w-40"
                  placeholder="To"
                />
                {(dateFrom || dateTo) && (
                  <button
                    onClick={() => {
                      setDateFrom("");
                      setDateTo("");
                    }}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>

            {/* We use a single TabsContent for "All" and render filtered data */}
            {STATUS_TABS.map((tab) => (
              <TabsContent key={tab} value={tab}>
                <BillsTable
                  bills={filteredBills}
                  loading={loading}
                  onCreateBill={() => setShowCreate(true)}
                  onViewBill={(bill) => {
                    setSelectedBill(bill);
                    setShowView(true);
                  }}
                  onRecordPayment={(bill) => {
                    setSelectedBill(bill);
                    setShowPayment(true);
                  }}
                />
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Generate Bill Modal */}
      <GenerateBillModal
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onSuccess={loadData}
      />

      {/* Record Payment Modal */}
      {selectedBill && (
        <RecordPaymentModal
          open={showPayment}
          bill={selectedBill}
          onClose={() => {
            setShowPayment(false);
            setSelectedBill(null);
          }}
          onSuccess={loadData}
        />
      )}

      {/* View Bill Modal */}
      {selectedBill && (
        <ViewBillModal
          open={showView}
          bill={selectedBill}
          onClose={() => {
            setShowView(false);
            setSelectedBill(null);
          }}
        />
      )}
    </AppShell>
  );
}

// ── Bills Table ────────────────────────────────────────────────────────

function BillsTable({
  bills,
  loading,
  onCreateBill,
  onViewBill,
  onRecordPayment,
}: {
  bills: Bill[];
  loading: boolean;
  onCreateBill: () => void;
  onViewBill: (b: Bill) => void;
  onRecordPayment: (b: Bill) => void;
}) {
  if (loading) {
    return (
      <div className="space-y-3 animate-pulse">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-gray-100 rounded" />
        ))}
      </div>
    );
  }

  if (bills.length === 0) {
    return (
      <EmptyState
        icon="billing"
        title="No bills found"
        description="No bills match the current filters"
        actionLabel="Generate Bill"
        onAction={onCreateBill}
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="data-table">
        <thead>
          <tr>
            <th>Bill #</th>
            <th>Patient</th>
            <th>Date</th>
            <th>Total</th>
            <th>Paid</th>
            <th>Balance</th>
            <th>Status</th>
            <th className="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {bills.map((b) => (
            <tr key={b.id}>
              <td>
                <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded-lg">
                  {b.bill_number}
                </span>
              </td>
              <td className="text-gray-700 font-medium">
                {b.patient_name || (
                  <span className="font-mono text-xs text-gray-400">{b.patient_id}</span>
                )}
              </td>
              <td className="text-gray-500">{formatDate(b.bill_date)}</td>
              <td className="font-semibold">{formatCurrency(b.total_amount)}</td>
              <td className="text-emerald-600 font-medium">{formatCurrency(b.paid_amount)}</td>
              <td className={b.balance > 0 ? "text-red-600 font-medium" : "text-gray-400"}>
                {formatCurrency(b.balance)}
              </td>
              <td>
                <Badge variant={STATUS_VARIANT[b.status] || "secondary"} dot>
                  {b.status}
                </Badge>
              </td>
              <td>
                <div className="flex items-center justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onViewBill(b)}
                    title="View bill details"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  {b.balance > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onRecordPayment(b)}
                      title="Record payment"
                    >
                      <CreditCard className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Generate Bill Modal ────────────────────────────────────────────────

function GenerateBillModal({
  open,
  onClose,
  onSuccess,
}: {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  // Form state
  const [patientSearch, setPatientSearch] = useState("");
  const [patientId, setPatientId] = useState("");
  const [patientResults, setPatientResults] = useState<any[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [billDate, setBillDate] = useState(todayISO());
  const [paymentMode, setPaymentMode] = useState<string>("Cash");
  const [discount, setDiscount] = useState(0);
  const [notes, setNotes] = useState("");
  const [items, setItems] = useState<BillLineItem[]>([
    { description: "", category: "Consultation", quantity: 1, unit_price: 0 },
  ]);

  // Patient search
  const searchPatients = useCallback(async (query: string) => {
    if (query.length < 2) {
      setPatientResults([]);
      setShowResults(false);
      return;
    }
    try {
      const res = await api.get("/patients", { params: { search: query, limit: 5 } });
      const data = Array.isArray(res.data) ? res.data : res.data?.items || [];
      setPatientResults(data);
      setShowResults(true);
    } catch {
      setPatientResults([]);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => searchPatients(patientSearch), 300);
    return () => clearTimeout(timer);
  }, [patientSearch, searchPatients]);

  // Line item helpers
  const addItem = () =>
    setItems((prev) => [
      ...prev,
      { description: "", category: "Consultation", quantity: 1, unit_price: 0 },
    ]);

  const removeItem = (idx: number) => setItems((prev) => prev.filter((_, i) => i !== idx));

  const updateItem = (idx: number, field: keyof BillLineItem, value: any) => {
    setItems((prev) => prev.map((item, i) => (i === idx ? { ...item, [field]: value } : item)));
  };

  // Calculations
  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  const taxAmount = Math.round(subtotal * TAX_RATE * 100) / 100;
  const grandTotal = Math.max(subtotal + taxAmount - discount, 0);

  // Reset on close
  const handleClose = () => {
    setPatientSearch("");
    setPatientId("");
    setBillDate(todayISO());
    setPaymentMode("Cash");
    setDiscount(0);
    setNotes("");
    setItems([{ description: "", category: "Consultation", quantity: 1, unit_price: 0 }]);
    setPatientResults([]);
    setShowResults(false);
    onClose();
  };

  const handleSubmit = async () => {
    if (!patientId.trim()) {
      toast("error", "Error", "Please search and select a patient");
      return;
    }
    if (items.some((i) => !i.description || i.unit_price <= 0)) {
      toast("error", "Error", "Please fill all item details with valid prices");
      return;
    }
    setLoading(true);
    try {
      await api.post("/billing", {
        patient_id: patientId.trim(),
        bill_date: billDate,
        items: items.map((i) => ({
          description: i.description,
          category: i.category,
          quantity: i.quantity,
          unit_price: i.unit_price,
          total_price: i.quantity * i.unit_price,
        })),
        subtotal,
        tax_amount: taxAmount,
        discount_amount: discount,
        total_amount: grandTotal,
        payment_mode: paymentMode,
        notes: notes.trim() || undefined,
      });
      toast("success", "Bill Created", `Bill generated for ${formatCurrency(grandTotal)}`);
      handleClose();
      onSuccess();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not create bill");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Generate Bill"
      description="Create a new bill with itemized charges"
      size="xl"
    >
      <div className="p-6 space-y-5">
        {/* Patient Search & Date */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="relative">
            <label className="block text-sm font-medium text-gray-600 mb-1">Patient *</label>
            <Input
              value={patientSearch}
              onChange={(e) => {
                setPatientSearch(e.target.value);
                setPatientId("");
              }}
              placeholder="Search by name, phone, or ID..."
              icon={<Search className="h-4 w-4" />}
            />
            {showResults && patientResults.length > 0 && (
              <div className="absolute z-50 top-full mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto">
                {patientResults.map((p: any) => (
                  <button
                    key={p.id}
                    className="w-full text-left px-4 py-2.5 hover:bg-gray-50 transition-colors text-sm border-b border-gray-50 last:border-0"
                    onClick={() => {
                      setPatientSearch(
                        p.full_name || `${p.first_name || ""} ${p.last_name || ""}`.trim()
                      );
                      setPatientId(p.id);
                      setShowResults(false);
                    }}
                  >
                    <span className="font-medium text-gray-900">
                      {p.full_name || `${p.first_name || ""} ${p.last_name || ""}`.trim()}
                    </span>
                    {p.phone && (
                      <span className="text-gray-400 ml-2 text-xs">{p.phone}</span>
                    )}
                  </button>
                ))}
              </div>
            )}
            {patientId && (
              <p className="text-xs text-emerald-600 mt-1">Patient selected</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Bill Date</label>
            <Input type="date" value={billDate} onChange={(e) => setBillDate(e.target.value)} />
          </div>
        </div>

        {/* Line Items */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-700">Bill Items</h4>
            <Button size="sm" variant="outline" onClick={addItem}>
              <Plus className="h-3 w-3 mr-1" />
              Add Item
            </Button>
          </div>
          <div className="space-y-3">
            <div className="grid grid-cols-12 gap-2 text-xs font-semibold text-gray-500 uppercase tracking-wider px-1">
              <div className="col-span-3">Service Type</div>
              <div className="col-span-3">Description</div>
              <div className="col-span-1">Qty</div>
              <div className="col-span-2">Unit Price</div>
              <div className="col-span-2 text-right">Total</div>
              <div className="col-span-1"></div>
            </div>
            {items.map((item, idx) => (
              <div key={idx} className="grid grid-cols-12 gap-2 items-center">
                <div className="col-span-3">
                  <select
                    value={item.category}
                    onChange={(e) => updateItem(idx, "category", e.target.value)}
                    className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30"
                  >
                    {SERVICE_TYPES.map((c) => (
                      <option key={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div className="col-span-3">
                  <Input
                    value={item.description}
                    onChange={(e) => updateItem(idx, "description", e.target.value)}
                    placeholder="Description"
                  />
                </div>
                <div className="col-span-1">
                  <Input
                    type="number"
                    min={1}
                    value={item.quantity}
                    onChange={(e) => updateItem(idx, "quantity", parseInt(e.target.value) || 1)}
                  />
                </div>
                <div className="col-span-2">
                  <Input
                    type="number"
                    min={0}
                    value={item.unit_price}
                    onChange={(e) => updateItem(idx, "unit_price", parseFloat(e.target.value) || 0)}
                  />
                </div>
                <div className="col-span-2 text-sm font-medium text-gray-700 text-right">
                  {formatCurrency(item.quantity * item.unit_price)}
                </div>
                <div className="col-span-1 text-center">
                  {items.length > 1 && (
                    <button
                      onClick={() => removeItem(idx)}
                      className="p-1.5 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Summary */}
        <div className="bg-gray-50 rounded-xl p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Subtotal</span>
            <span className="font-medium">{formatCurrency(subtotal)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Tax (18% GST)</span>
            <span className="font-medium">{formatCurrency(taxAmount)}</span>
          </div>
          <div className="flex justify-between text-sm items-center">
            <span className="text-gray-500">Discount</span>
            <Input
              type="number"
              min={0}
              value={discount}
              onChange={(e) => setDiscount(parseFloat(e.target.value) || 0)}
              className="w-32 text-right"
            />
          </div>
          <div className="flex justify-between text-base font-bold border-t border-gray-200 pt-2">
            <span>Grand Total</span>
            <span className="text-primary-700">{formatCurrency(grandTotal)}</span>
          </div>
        </div>

        {/* Payment Mode & Notes */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Payment Mode</label>
            <select
              value={paymentMode}
              onChange={(e) => setPaymentMode(e.target.value)}
              className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30"
            >
              {PAYMENT_MODES.map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Notes</label>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Optional notes..."
              rows={2}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
        <Button variant="outline" onClick={handleClose}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} loading={loading} variant="gradient">
          <Receipt className="h-4 w-4 mr-2" />
          Generate Bill
        </Button>
      </div>
    </Modal>
  );
}

// ── Record Payment Modal ───────────────────────────────────────────────

function RecordPaymentModal({
  open,
  bill,
  onClose,
  onSuccess,
}: {
  open: boolean;
  bill: Bill;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [amount, setAmount] = useState(bill.balance);
  const [paymentMethod, setPaymentMethod] = useState("Cash");
  const [transactionId, setTransactionId] = useState("");

  useEffect(() => {
    setAmount(bill.balance);
    setPaymentMethod("Cash");
    setTransactionId("");
  }, [bill]);

  const handleSubmit = async () => {
    if (amount <= 0) {
      toast("error", "Error", "Amount must be greater than zero");
      return;
    }
    if (amount > bill.balance) {
      toast("error", "Error", "Amount cannot exceed outstanding balance");
      return;
    }
    setLoading(true);
    try {
      await api.post(`/billing/${bill.id}/payment`, {
        amount,
        payment_method: paymentMethod,
        transaction_id: transactionId.trim() || undefined,
      });
      toast("success", "Payment Recorded", `${formatCurrency(amount)} recorded for ${bill.bill_number}`);
      onClose();
      onSuccess();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not record payment");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Record Payment" description={`Payment for bill ${bill.bill_number}`} size="md">
      <div className="p-6 space-y-5">
        {/* Bill Summary */}
        <div className="bg-gray-50 rounded-xl p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Bill Number</span>
            <span className="font-mono text-sm font-medium">{bill.bill_number}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Patient</span>
            <span className="font-medium">{bill.patient_name || bill.patient_id}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Total Amount</span>
            <span className="font-medium">{formatCurrency(bill.total_amount)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Already Paid</span>
            <span className="font-medium text-emerald-600">{formatCurrency(bill.paid_amount)}</span>
          </div>
          <div className="flex justify-between text-sm font-bold border-t border-gray-200 pt-2">
            <span>Outstanding Balance</span>
            <span className="text-red-600">{formatCurrency(bill.balance)}</span>
          </div>
        </div>

        {/* Payment Form */}
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Amount *</label>
          <Input
            type="number"
            min={0}
            max={bill.balance}
            step={0.01}
            value={amount}
            onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Payment Method</label>
          <select
            value={paymentMethod}
            onChange={(e) => setPaymentMethod(e.target.value)}
            className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30"
          >
            {PAYMENT_MODES.map((m) => (
              <option key={m}>{m}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Transaction ID</label>
          <Input
            value={transactionId}
            onChange={(e) => setTransactionId(e.target.value)}
            placeholder="Optional reference number"
          />
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} loading={loading} variant="gradient">
          <CreditCard className="h-4 w-4 mr-2" />
          Record Payment
        </Button>
      </div>
    </Modal>
  );
}

// ── View Bill Modal ────────────────────────────────────────────────────

function ViewBillModal({
  open,
  bill,
  onClose,
}: {
  open: boolean;
  bill: Bill;
  onClose: () => void;
}) {
  const [fullBill, setFullBill] = useState<Bill | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && bill.id) {
      setLoading(true);
      api
        .get(`/billing/${bill.id}`)
        .then((r) => setFullBill(r.data))
        .catch(() => setFullBill(bill))
        .finally(() => setLoading(false));
    }
  }, [open, bill]);

  const data = fullBill || bill;
  const lineItems: BillLineItem[] = data.items || [];

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Bill ${data.bill_number}`}
      description={`Issued on ${formatDate(data.bill_date)}`}
      size="lg"
    >
      <div className="p-6 space-y-5">
        {loading ? (
          <div className="space-y-3 animate-pulse">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-8 bg-gray-100 rounded" />
            ))}
          </div>
        ) : (
          <>
            {/* Bill Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider">Patient</p>
                <p className="text-sm font-medium text-gray-900 mt-0.5">
                  {data.patient_name || data.patient_id}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider">Status</p>
                <div className="mt-0.5">
                  <Badge variant={STATUS_VARIANT[data.status] || "secondary"} dot>
                    {data.status}
                  </Badge>
                </div>
              </div>
              {data.payment_mode && (
                <div>
                  <p className="text-xs text-gray-400 uppercase tracking-wider">Payment Mode</p>
                  <p className="text-sm font-medium text-gray-900 mt-0.5">{data.payment_mode}</p>
                </div>
              )}
            </div>

            {/* Line Items Table */}
            {lineItems.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Line Items</h4>
                <div className="border border-gray-100 rounded-xl overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">
                          Description
                        </th>
                        <th className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">
                          Category
                        </th>
                        <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">
                          Qty
                        </th>
                        <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">
                          Unit Price
                        </th>
                        <th className="text-right px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase">
                          Total
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {lineItems.map((item, idx) => (
                        <tr key={idx} className="border-t border-gray-50">
                          <td className="px-4 py-2.5 text-gray-900">{item.description}</td>
                          <td className="px-4 py-2.5 text-gray-500">{item.category}</td>
                          <td className="px-4 py-2.5 text-right text-gray-700">{item.quantity}</td>
                          <td className="px-4 py-2.5 text-right text-gray-700">
                            {formatCurrency(item.unit_price)}
                          </td>
                          <td className="px-4 py-2.5 text-right font-medium text-gray-900">
                            {formatCurrency(item.quantity * item.unit_price)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Totals */}
            <div className="bg-gray-50 rounded-xl p-4 space-y-2">
              {data.subtotal != null && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Subtotal</span>
                  <span className="font-medium">{formatCurrency(data.subtotal)}</span>
                </div>
              )}
              {data.tax_amount != null && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Tax (GST)</span>
                  <span className="font-medium">{formatCurrency(data.tax_amount)}</span>
                </div>
              )}
              {data.discount_amount != null && data.discount_amount > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Discount</span>
                  <span className="font-medium text-red-600">
                    -{formatCurrency(data.discount_amount)}
                  </span>
                </div>
              )}
              <div className="flex justify-between text-sm font-bold border-t border-gray-200 pt-2">
                <span>Total Amount</span>
                <span>{formatCurrency(data.total_amount)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Paid</span>
                <span className="font-medium text-emerald-600">
                  {formatCurrency(data.paid_amount)}
                </span>
              </div>
              {data.balance > 0 && (
                <div className="flex justify-between text-sm font-semibold">
                  <span className="text-gray-500">Balance Due</span>
                  <span className="text-red-600">{formatCurrency(data.balance)}</span>
                </div>
              )}
            </div>

            {/* Notes */}
            {data.notes && (
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Notes</p>
                <p className="text-sm text-gray-600 bg-gray-50 rounded-xl p-3">{data.notes}</p>
              </div>
            )}
          </>
        )}
      </div>

      <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
        <Button variant="outline" onClick={onClose}>
          Close
        </Button>
      </div>
    </Modal>
  );
}
