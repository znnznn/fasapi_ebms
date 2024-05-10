import { TableRow } from '@radix-ui/themes'
import React from 'react'

import { Skeleton } from '@/components/ui/skeleton'
import { TableCell } from '@/components/ui/table'

interface Props {
    cellCount: number
}
export const TableSkeleton: React.FC<Props> = ({ cellCount }) => {
    return Array.from({ length: 10 }).map((_, index) => (
        <TableRow
            className='p-0'
            key={index}>
            <TableCell
                colSpan={cellCount}
                className='h-[41px] py-1.5 !px-0'>
                <Skeleton className='w-full h-[41px]' />
            </TableCell>
        </TableRow>
    ))
}
