import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary-50 text-primary-700 border border-primary-200",
        success: "bg-emerald-50 text-emerald-700 border border-emerald-200",
        warning: "bg-amber-50 text-amber-700 border border-amber-200",
        danger: "bg-red-50 text-red-700 border border-red-200",
        secondary: "bg-gray-100 text-gray-700 border border-gray-200",
        outline: "border border-gray-300 text-gray-600 bg-white",
        info: "bg-blue-50 text-blue-700 border border-blue-200",
        purple: "bg-purple-50 text-purple-700 border border-purple-200",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

function Badge({ className, variant, dot, children, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props}>
      {dot && <span className={cn("h-1.5 w-1.5 rounded-full mr-1.5", {
        "bg-primary-500": variant === "default" || !variant,
        "bg-emerald-500": variant === "success",
        "bg-amber-500": variant === "warning",
        "bg-red-500": variant === "danger",
        "bg-gray-500": variant === "secondary",
        "bg-blue-500": variant === "info",
        "bg-purple-500": variant === "purple",
      })} />}
      {children}
    </div>
  );
}

export { Badge, badgeVariants };
