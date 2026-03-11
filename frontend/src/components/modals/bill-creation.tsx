"use client";
import React, { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { Receipt, Plus, Trash2 } from "lucide-react";

interface BillCreationProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface BillItem {
  description: string;
  category: string;
  quantity: number;
  unit_price: number;
}

export function BillCreation({ open, onClose, onSuccess }: BillCreationProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [patientId, setPatientId] = useState("");
  const [admissionId, setAdmissionId] = useState("");
  const [discount, setDiscount] = useState(0);
  const [items, setItems] = useState<BillItem[]>([
    { description: "", category: "Consultation", quantity: 1, unit_price: 0 },
  ]);

  const addItem = () => setItems(prev => [...prev, { description: "", category: "Consultation", quantity: 1, unit_price: 0 }]);
  const removeItem = (idx: number) => setItems(prev => prev.filter((_, i) => i !== idx));
  const updateItem = (idx: number, field: keyof BillItem, value: any) => {
    setItems(prev => prev.map((item, i) => i === idx ? { ...item, [field]: value } : item));
  };

  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  const total = subtotal - discount;

  const handleSubmit = async () => {
    if (!patientId.trim()) { toast("error", "Error", "Patient ID is required"); return; }
    if (items.some(i => !i.description || i.unit_price <= 0)) { toast("error", "Error", "Fill all item details"); return; }
    setLoading(true);
    try {
      await api.post("/billing", {
        patient_id: patientId.trim(),
        admission_id: admissionId.trim() || undefined,
        items: items.map(i => ({
          description: i.description, category: i.category,
          quantity: i.quantity, unit_price: i.unit_price,
          total_price: i.quantity * i.unit_price,
        })),
        discount_amount: discount,
        total_amount: total,
      });
      toast("success", "Bill Created", `Bill generated for Rs. ${total.toLocaleString("en-IN")}`);
      onClose();
      onSuccess?.();
    } catch (err: any) {
      toast("error", "Failed", err.response?.data?.detail || "Could not create bill");
    } finally {
      setLoading(false);
    }
  };

  const categories = ["Consultation", "Procedure", "Lab", "Radiology", "Medicine", "Room", "OT", "Nursing", "Other"];

  return (
    <Modal open={open} onClose={onClose} title="Generate Bill" description="Create a new bill with itemized charges" size="xl">
      <div className="p-6 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Patient ID *</label>
            <Input value={patientId} onChange={e => setPatientId(e.target.value)} placeholder="Patient UUID" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Admission ID (optional)</label>
            <Input value={admissionId} onChange={e => setAdmissionId(e.target.value)} placeholder="If IPD bill" />
          </div>
        </div>

        {/* Line Items */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-gray-700">Bill Items</h4>
            <Button size="sm" variant="outline" onClick={addItem}><Plus className="h-3 w-3 mr-1" />Add Item</Button>
          </div>
          <div className="space-y-3">
            <div className="grid grid-cols-12 gap-2 text-xs font-semibold text-gray-500 uppercase tracking-wider px-1">
              <div className="col-span-4">Description</div>
              <div className="col-span-2">Category</div>
              <div className="col-span-2">Qty</div>
              <div className="col-span-2">Price</div>
              <div className="col-span-1">Total</div>
              <div className="col-span-1"></div>
            </div>
            {items.map((item, idx) => (
              <div key={idx} className="grid grid-cols-12 gap-2 items-center">
                <div className="col-span-4">
                  <Input value={item.description} onChange={e => updateItem(idx, "description", e.target.value)} placeholder="Description" />
                </div>
                <div className="col-span-2">
                  <select value={item.category} onChange={e => updateItem(idx, "category", e.target.value)} className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30">
                    {categories.map(c => <option key={c}>{c}</option>)}
                  </select>
                </div>
                <div className="col-span-2">
                  <Input type="number" min={1} value={item.quantity} onChange={e => updateItem(idx, "quantity", parseInt(e.target.value) || 1)} />
                </div>
                <div className="col-span-2">
                  <Input type="number" min={0} value={item.unit_price} onChange={e => updateItem(idx, "unit_price", parseFloat(e.target.value) || 0)} />
                </div>
                <div className="col-span-1 text-sm font-medium text-gray-700 text-right">
                  {(item.quantity * item.unit_price).toLocaleString("en-IN")}
                </div>
                <div className="col-span-1 text-center">
                  {items.length > 1 && (
                    <button onClick={() => removeItem(idx)} className="p-1.5 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 transition-colors">
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
          <div className="flex justify-between text-sm"><span className="text-gray-500">Subtotal</span><span className="font-medium">Rs. {subtotal.toLocaleString("en-IN")}</span></div>
          <div className="flex justify-between text-sm items-center">
            <span className="text-gray-500">Discount</span>
            <Input type="number" min={0} value={discount} onChange={e => setDiscount(parseFloat(e.target.value) || 0)} className="w-32 text-right" />
          </div>
          <div className="flex justify-between text-base font-bold border-t border-gray-200 pt-2">
            <span>Total</span><span className="text-primary-700">Rs. {total.toLocaleString("en-IN")}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
        <Button variant="outline" onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} loading={loading} variant="gradient">
          <Receipt className="h-4 w-4 mr-2" />Generate Bill
        </Button>
      </div>
    </Modal>
  );
}
