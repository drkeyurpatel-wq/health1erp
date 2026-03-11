"use client";
import React, { useEffect, useCallback } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "full";
  className?: string;
}

const sizeClasses = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
  full: "max-w-6xl",
};

export function Modal({ open, onClose, title, description, children, size = "md", className }: ModalProps) {
  const handleEsc = useCallback((e: KeyboardEvent) => {
    if (e.key === "Escape") onClose();
  }, [onClose]);

  useEffect(() => {
    if (open) {
      document.addEventListener("keydown", handleEsc);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEsc);
      document.body.style.overflow = "";
    };
  }, [open, handleEsc]);

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="flex items-center justify-center min-h-screen p-4">
        <div
          className={cn(
            "modal-content bg-white rounded-2xl shadow-modal w-full",
            sizeClasses[size],
            "max-h-[90vh] flex flex-col",
            className
          )}
          onClick={e => e.stopPropagation()}
        >
          {title && (
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
                {description && <p className="text-sm text-gray-500 mt-0.5">{description}</p>}
              </div>
              <button onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600">
                <X className="h-5 w-5" />
              </button>
            </div>
          )}
          <div className="flex-1 overflow-y-auto">{children}</div>
        </div>
      </div>
    </div>
  );
}
