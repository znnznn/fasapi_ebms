import { TableRow } from '@radix-ui/themes'

import { Skeleton } from '@/components/ui/skeleton'
import { TableCell } from '@/components/ui/table'

export const TableSkeleton = () => {
    return Array.from({ length: 10 }).map((_, index) => (
        <TableRow key={index}>
            {Array.from({ length: 5 }).map((_, index) => (
                <TableCell key={index}>
                    <Skeleton className='w-full h-8' />
                </TableCell>
            ))}
        </TableRow>
    ))
}
