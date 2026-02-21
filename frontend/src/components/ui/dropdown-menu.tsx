import * as React from "react"
import { cn } from "../../lib/utils"

const DropdownMenu = ({ children }: { children: React.ReactNode }) => {
    const [open, setOpen] = React.useState(false)

    const handleToggle = () => {
        setOpen(!open)
    }

    const handleClose = () => {
        setOpen(false)
    }

    React.useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const dropdown = event.target as Node
            if (dropdown && !document.querySelector('[role="dropdown-menu"]')?.contains(dropdown)) {
                setOpen(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    return (
        <div className="relative inline-block">
            {React.Children.map(children, child => {
                if (React.isValidElement(child)) {
                    if (child.type === DropdownMenuTrigger) {
                        return React.cloneElement(child, {
                            onClick: handleToggle
                        })
                    } else if (child.type === DropdownMenuContent) {
                        return open ? React.cloneElement(child, {
                            onMouseLeave: handleClose
                        }) : null
                    }
                }
                return child
            })}
        </div>
    )
}

const DropdownMenuTrigger = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement> & { asChild?: boolean }
>(({ className, children, asChild, ...props }, ref) => {
    return (
        <div ref={ref} className={cn("cursor-pointer", className)} {...props}>
            {children}
        </div>
    )
})
DropdownMenuTrigger.displayName = "DropdownMenuTrigger"

const DropdownMenuContent = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement> & { align?: 'start' | 'center' | 'end' }
>(({ className, align = 'center', children, ...props }, ref) => {
    const alignClass = align === 'end' ? 'right-0' : align === 'start' ? 'left-0' : 'left-1/2 -translate-x-1/2'
    
    return (
        <div
            ref={ref}
            className={cn(
                "absolute z-50 mt-2 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
                alignClass,
                className
            )}
            {...props}
        >
            {children}
        </div>
    )
})
DropdownMenuContent.displayName = "DropdownMenuContent"

const DropdownMenuItem = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => {
    return (
        <div
            ref={ref}
            className={cn(
                "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
                className
            )}
            {...props}
        >
            {children}
        </div>
    )
})
DropdownMenuItem.displayName = "DropdownMenuItem"

export { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem }