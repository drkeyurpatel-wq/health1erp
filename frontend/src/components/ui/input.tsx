import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  icon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, type, error, icon, ...props }, ref) => (
  <div className="relative">
    {icon && <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{icon}</div>}
    <input
      type={type}
      className={cn(
        "flex h-10 w-full rounded-xl border bg-white px-3 py-2 text-sm transition-all duration-200",
        "placeholder:text-gray-400",
        "focus:outline-none focus:ring-2 focus:ring-offset-0",
        "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50",
        error
          ? "border-red-300 focus:ring-red-500/30 focus:border-red-400"
          : "border-gray-200 focus:ring-primary-500/30 focus:border-primary-400",
        icon && "pl-10",
        className
      )}
      ref={ref}
      {...props}
    />
    {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
  </div>
));
Input.displayName = "Input";

export { Input };
