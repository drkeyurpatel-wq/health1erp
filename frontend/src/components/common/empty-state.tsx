"use client";
import React from "react";
import { FileX, Users, Calendar, Receipt, Package, FlaskConical, Pill, BedDouble, Scissors, ScanLine, ClipboardList } from "lucide-react";
import { Button } from "@/components/ui/button";

const icons: Record<string, React.ReactNode> = {
  patients: <Users className="h-16 w-16" />,
  appointments: <Calendar className="h-16 w-16" />,
  billing: <Receipt className="h-16 w-16" />,
  inventory: <Package className="h-16 w-16" />,
  laboratory: <FlaskConical className="h-16 w-16" />,
  pharmacy: <Pill className="h-16 w-16" />,
  ipd: <BedDouble className="h-16 w-16" />,
  ot: <Scissors className="h-16 w-16" />,
  radiology: <ScanLine className="h-16 w-16" />,
  reports: <ClipboardList className="h-16 w-16" />,
  default: <FileX className="h-16 w-16" />,
};

interface EmptyStateProps {
  icon?: string;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ icon = "default", title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="text-gray-300">{icons[icon] || icons.default}</div>
      <h3 className="text-lg font-semibold text-gray-600 mb-1">{title}</h3>
      {description && <p className="text-sm text-gray-400 max-w-sm mb-4">{description}</p>}
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm">{actionLabel}</Button>
      )}
    </div>
  );
}
