import * as React from "react"

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'destructive' | 'warning'
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
    ({ className, variant = 'default', ...props }, ref) => {
        const variantStyles = {
            default: 'bg-background text-foreground border-border',
            destructive: 'border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive',
            warning: 'border-yellow-500/50 text-yellow-900 dark:text-yellow-200 [&>svg]:text-yellow-600'
        }

        return (
            <div
                ref={ref}
                role="alert"
                className={`relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground ${variantStyles[variant]} ${className || ''}`}
                {...props}
            />
        )
    }
)
Alert.displayName = "Alert"

const AlertDescription = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={`text-sm [&_p]:leading-relaxed ${className || ''}`}
        {...props}
    />
))
AlertDescription.displayName = "AlertDescription"

export { Alert, AlertDescription }
