"use client";
import React, { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/contexts/toast-context";
import api from "@/lib/api";
import { UserPlus, User, Phone, Mail, MapPin, Droplets, AlertCircle, Calendar } from "lucide-react";

interface PatientRegistrationProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function PatientRegistration({ open, onClose, onSuccess }: PatientRegistrationProps) {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [form, setForm] = useState({
    first_name: "", last_name: "", date_of_birth: "", gender: "Male",
    phone: "", email: "", blood_group: "",
    address_line: "", city: "", state: "", pincode: "",
    allergies: "", emergency_contact_name: "", emergency_contact_phone: "",
    preferred_language: "en",
  });

  const validate = () => {
    const e: Record<string, string> = {};
    if (!form.first_name.trim()) e.first_name = "First name is required";
    if (!form.last_name.trim()) e.last_name = "Last name is required";
    if (!form.date_of_birth) e.date_of_birth = "Date of birth is required";
    if (!form.phone.trim()) e.phone = "Phone number is required";
    else if (!/^\+?[\d\s-]{8,15}$/.test(form.phone.trim())) e.phone = "Invalid phone number";
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = "Invalid email";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      await api.post("/patients", {
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        date_of_birth: form.date_of_birth,
        gender: form.gender,
        phone: form.phone.trim(),
        email: form.email.trim() || undefined,
        blood_group: form.blood_group || undefined,
        address: form.address_line ? {
          line: form.address_line, city: form.city, state: form.state, pincode: form.pincode,
        } : undefined,
        allergies: form.allergies ? form.allergies.split(",").map(s => s.trim()).filter(Boolean) : [],
        emergency_contact: form.emergency_contact_name ? {
          name: form.emergency_contact_name, phone: form.emergency_contact_phone,
        } : undefined,
        preferred_language: form.preferred_language,
      });
      toast("success", "Patient Registered", "New patient has been added successfully");
      onClose();
      onSuccess?.();
      setForm({
        first_name: "", last_name: "", date_of_birth: "", gender: "Male",
        phone: "", email: "", blood_group: "",
        address_line: "", city: "", state: "", pincode: "",
        allergies: "", emergency_contact_name: "", emergency_contact_phone: "",
        preferred_language: "en",
      });
    } catch (err: any) {
      toast("error", "Registration Failed", err.response?.data?.detail || "Could not register patient");
    } finally {
      setLoading(false);
    }
  };

  const update = (field: string, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors(prev => { const n = { ...prev }; delete n[field]; return n; });
  };

  return (
    <Modal open={open} onClose={onClose} title="Register New Patient" description="Fill in patient demographics and medical info" size="xl">
      <div className="p-6 space-y-6">
        {/* Personal Info */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2"><User className="h-4 w-4 text-primary-500" />Personal Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">First Name *</label>
              <Input value={form.first_name} onChange={e => update("first_name", e.target.value)} error={errors.first_name} placeholder="John" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Last Name *</label>
              <Input value={form.last_name} onChange={e => update("last_name", e.target.value)} error={errors.last_name} placeholder="Doe" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Date of Birth *</label>
              <Input type="date" value={form.date_of_birth} onChange={e => update("date_of_birth", e.target.value)} error={errors.date_of_birth} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Gender</label>
              <select value={form.gender} onChange={e => update("gender", e.target.value)} className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400">
                <option>Male</option><option>Female</option><option>Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Blood Group</label>
              <select value={form.blood_group} onChange={e => update("blood_group", e.target.value)} className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400">
                <option value="">Select</option>
                {["A+","A-","B+","B-","AB+","AB-","O+","O-"].map(bg => <option key={bg}>{bg}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Preferred Language</label>
              <select value={form.preferred_language} onChange={e => update("preferred_language", e.target.value)} className="flex h-10 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-400">
                <option value="en">English</option><option value="hi">Hindi</option><option value="ar">Arabic</option>
                <option value="es">Spanish</option><option value="fr">French</option><option value="zh">Chinese</option>
              </select>
            </div>
          </div>
        </div>

        {/* Contact Info */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2"><Phone className="h-4 w-4 text-primary-500" />Contact Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Phone *</label>
              <Input value={form.phone} onChange={e => update("phone", e.target.value)} error={errors.phone} placeholder="+91 98765 43210" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Email</label>
              <Input type="email" value={form.email} onChange={e => update("email", e.target.value)} error={errors.email} placeholder="patient@email.com" />
            </div>
          </div>
        </div>

        {/* Address */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2"><MapPin className="h-4 w-4 text-primary-500" />Address</h4>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <Input value={form.address_line} onChange={e => update("address_line", e.target.value)} placeholder="Street address" />
            </div>
            <Input value={form.city} onChange={e => update("city", e.target.value)} placeholder="City" />
            <div className="grid grid-cols-2 gap-2">
              <Input value={form.state} onChange={e => update("state", e.target.value)} placeholder="State" />
              <Input value={form.pincode} onChange={e => update("pincode", e.target.value)} placeholder="PIN" />
            </div>
          </div>
        </div>

        {/* Medical Info */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2"><AlertCircle className="h-4 w-4 text-red-500" />Medical Information</h4>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Allergies (comma-separated)</label>
            <Input value={form.allergies} onChange={e => update("allergies", e.target.value)} placeholder="e.g. Penicillin, Aspirin, Shellfish" />
          </div>
        </div>

        {/* Emergency Contact */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2"><Phone className="h-4 w-4 text-amber-500" />Emergency Contact</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input value={form.emergency_contact_name} onChange={e => update("emergency_contact_name", e.target.value)} placeholder="Contact name" />
            <Input value={form.emergency_contact_phone} onChange={e => update("emergency_contact_phone", e.target.value)} placeholder="Contact phone" />
          </div>
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
        <Button variant="outline" onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} loading={loading} variant="gradient">
          <UserPlus className="h-4 w-4 mr-2" />Register Patient
        </Button>
      </div>
    </Modal>
  );
}
