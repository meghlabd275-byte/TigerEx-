import * as React from "react"

const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(({ className, ...props }, ref) => {
    return (
        <select
            className={className}
            ref={ref}
            {...props} />
    )
})
Select.displayName = "Select"

export { Select }