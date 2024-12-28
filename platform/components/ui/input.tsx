import * as React from "react"

import { cn } from "@/lib/utils"

export interface InputWrapperProps extends React.ComponentProps<"div"> {
  fullWidth?: boolean;
}

const InputWrapper = React.forwardRef<HTMLDivElement, InputWrapperProps>(
  ({ className, fullWidth = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "w-full max-w-[800px] mx-auto",
          fullWidth && "max-w-full",
          "no-scrollbar overflow-y-hidden",
          className
        )}
        {...props}
      />
    )
  }
)
InputWrapper.displayName = "InputWrapper"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-white px-3 py-2 text-base shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground/50 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input, InputWrapper }
