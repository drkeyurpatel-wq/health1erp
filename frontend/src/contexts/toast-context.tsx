"use client";
import React, { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle, AlertTriangle, XCircle, Info, X } from "lucide-react";

type ToastType = "success" | "error" | "warning" | "info";
interface Toast { id: string; type: ToastType; title: string; message?: string; }
interface ToastContextType { toast: (type: ToastType, title: string, message?: string) => void; }

const ToastContext = createContext<ToastContextType>({ toast: () => {} });
export const useToast = () => useContext(ToastContext);

const icons: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle className="h-5 w-5 text-emerald-500" />,
  error: <XCircle className="h-5 w-5 text-red-500" />,
  warning: <AlertTriangle className="h-5 w-5 text-amber-500" />,
  info: <Info className="h-5 w-5 text-blue-500" />,
};

const borderColors: Record<ToastType, string> = {
  success: "border-emerald-200 bg-emerald-50",
  error: "border-red-200 bg-red-50",
  warning: "border-amber-200 bg-amber-50",
  info: "border-blue-200 bg-blue-50",
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((type: ToastType, title: string, message?: string) => {
    const id = Math.random().toString(36).slice(2);
    setToasts(prev => [...prev, { id, type, title, message }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${borderColors[t.type]}`}>
            <div className="flex items-start gap-3">
              <div className="shrink-0 mt-0.5">{icons[t.type]}</div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900">{t.title}</p>
                {t.message && <p className="text-xs text-gray-600 mt-0.5">{t.message}</p>}
              </div>
              <button onClick={() => removeToast(t.id)} className="shrink-0 text-gray-400 hover:text-gray-600">
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
