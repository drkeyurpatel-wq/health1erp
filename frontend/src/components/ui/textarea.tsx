import * as React from "react";
import { cn } from "@/lib/utils";

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(({ className, error, ...props }, ref) => (
  <div>
    <textarea
      className={cn(
        "flex min-h-[80px] w-full rounded-xl border bg-white px-3 py-2.5 text-sm transition-all duration-200",
        "placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-0",
        "disabled:cursor-not-allowed disabled:opacity-50",
        error ? "border-red-300 focus:ring-red-500/30" : "border-gray-200 focus:ring-primary-500/30 focus:border-primary-400",
        className
      )}
      ref={ref}
      {...props}
    />
    {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
  </div>
));
Textarea.displayName = "Textarea";

export { Textarea };
