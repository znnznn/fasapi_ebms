import * as ProgressPrimitive from '@radix-ui/react-progress'
import * as React from 'react'

import { cn } from '@/utils/cn'

type ExtendedProgressProps = React.ComponentProps<typeof ProgressPrimitive.Root> & {
    indicatorClassName?: string
}

const Progress = React.forwardRef<
    React.ElementRef<typeof ProgressPrimitive.Root>,
    ExtendedProgressProps
>(({ className, indicatorClassName, value, ...props }, ref) => (
    <ProgressPrimitive.Root
        ref={ref}
        className={cn(
            'relative h-4 w-full overflow-hidden rounded-full bg-secondary',
            className
        )}
        {...props}>
        <ProgressPrimitive.Indicator
            className={cn('h-full bg-foreground/10', indicatorClassName)}
            style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
        />
    </ProgressPrimitive.Root>
))
Progress.displayName = ProgressPrimitive.Root.displayName

export { Progress }
