import type { Column } from '@tanstack/react-table'
import { ArrowUpDown } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { useAppSelector } from '@/store/hooks/hooks'
import { cn } from '@/utils/cn'

export const createHeader = <T, U>(
    title: string,
    column: Column<T, U>,
    className: string = 'text-center'
) => {
    const groupedView = useAppSelector((store) => store.orders.groupedView)
    const category = !!useAppSelector((store) => store.orders.category)

    return (
        <Button
            disabled={groupedView && category}
            variant='ghost'
            className={cn('w-full', className)}
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
            {title}

            <ArrowUpDown
                className={cn(
                    'ml-2 h-4 w-4 flex-shrink-0',
                    groupedView && category ? 'opacity-0' : ''
                )}
            />
        </Button>
    )
}

type Align = 'text-left' | 'text-center' | 'text-right'

export const alignCell = (value: string | number, align: Align = 'text-center') => (
    <div className={align}>{value}</div>
)
