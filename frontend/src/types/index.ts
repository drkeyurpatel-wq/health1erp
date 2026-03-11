export enum UserRole {
  SuperAdmin = "SuperAdmin", Admin = "Admin", Doctor = "Doctor",
  Nurse = "Nurse", Pharmacist = "Pharmacist", LabTech = "LabTech",
  Receptionist = "Receptionist", Accountant = "Accountant",
}

export enum AdmissionStatus {
  Admitted = "Admitted", Discharged = "Discharged", Transferred = "Transferred",
  LAMA = "LAMA", Expired = "Expired",
}

export enum BedStatus {
  Available = "Available", Occupied = "Occupied",
  Maintenance = "Maintenance", Reserved = "Reserved",
}

export interface User {
  id: string; email: string; phone?: string;
  first_name: string; last_name: string;
  role: UserRole; department_id?: string;
  profile_image?: string; is_active: boolean;
}

export interface Patient {
  id: string; uhid: string; mr_number?: string;
  first_name: string; last_name: string;
  date_of_birth: string; gender: string; blood_group?: string;
  phone: string; email?: string;
  address?: Record<string, any>; allergies?: string[];
  preferred_language: string; photo_url?: string;
  created_at: string;
}

export interface Appointment {
  id: string; patient_id: string; doctor_id: string;
  appointment_date: string; start_time: string; end_time?: string;
  status: string; appointment_type: string;
  chief_complaint?: string; notes?: string;
  token_number?: number; is_teleconsultation: boolean;
}

export interface Admission {
  id: string; patient_id: string; admitting_doctor_id: string;
  department_id?: string; bed_id?: string;
  admission_date: string; discharge_date?: string;
  admission_type: string; status: AdmissionStatus;
  diagnosis_at_admission?: string[]; icd_codes?: string[];
  treatment_plan?: Record<string, any>;
  ai_risk_score?: number; ai_recommendations?: string[];
  estimated_los?: number; actual_los?: number;
  discharge_summary?: string;
}

export interface Bed {
  id: string; ward_id: string; bed_number: string;
  bed_type: string; status: BedStatus; floor: number; wing?: string;
}

export interface Ward {
  id: string; name: string; ward_type: string;
  total_beds: number; floor: number;
}

export interface Bill {
  id: string; patient_id: string; bill_number: string;
  bill_date: string; status: string;
  total_amount: number; paid_amount: number; balance: number;
}

export interface InventoryItem {
  id: string; name: string; generic_name?: string;
  category: string; current_stock: number;
  reorder_level: number; selling_price: number;
}

export interface WardOccupancy {
  ward_id: string; ward_name: string;
  total_beds: number; occupied: number;
  available: number; occupancy_rate: number;
}

export interface IPDDashboard {
  total_admitted: number; discharges_today: number;
  admissions_today: number; critical_count: number;
  occupancy_rate: number; icu_occupancy_rate: number;
  average_los: number; ward_stats: WardOccupancy[];
}

export interface AIInsights {
  admission_id: string; risk_score: number; risk_level: string;
  predicted_los?: number; recommendations: string[];
  alerts: { type: string; message: string }[];
}

export interface PaginatedResponse<T> {
  items: T[]; total: number; page: number;
  page_size: number; total_pages: number;
}
