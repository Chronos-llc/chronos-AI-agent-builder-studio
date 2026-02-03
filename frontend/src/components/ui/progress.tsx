import * as React from "react"
import { cn } from "../../lib/utils"

const Progress = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement> & { 
        value?: number; 
        indicatorClassName?: string 
    }
>(({ className, value = 0, indicatorClassName, ...props }, ref) => {
    // Constrain value between 0 and 100
    const constrainedValue = Math.max(0, Math.min(100, value));
    
    return (
        <div
            ref={ref}
            className={cn(
                "relative h-4 w-full overflow-hidden rounded-full bg-secondary",
                className
            )}
            {...props}
        >
            <div
                className={cn(
                    "h-full bg-primary transition-all",
                    indicatorClassName
                )}
                style={{ width: `${constrainedValue}%` }}
            />
        </div>
    )
})
Progress.displayName = "Progress"

export { Progress }
