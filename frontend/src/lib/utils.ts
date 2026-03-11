import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { format, parseISO } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency = "INR"): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency }).format(amount);
}

export function formatDate(dateStr: string): string {
  try { return format(parseISO(dateStr), "dd MMM yyyy"); } catch { return dateStr; }
}

export function formatDateTime(dateStr: string): string {
  try { return format(parseISO(dateStr), "dd MMM yyyy, hh:mm a"); } catch { return dateStr; }
}

export function getRiskColor(score: number): string {
  if (score >= 0.7) return "text-red-600 bg-red-50";
  if (score >= 0.4) return "text-yellow-600 bg-yellow-50";
  return "text-green-600 bg-green-50";
}

export function getRiskLabel(score: number): string {
  if (score >= 0.7) return "High";
  if (score >= 0.4) return "Medium";
  return "Low";
}
