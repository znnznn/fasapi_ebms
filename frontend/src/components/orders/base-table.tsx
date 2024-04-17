import { type Table as TableType, flexRender } from '@tanstack/react-table'
import { Fragment } from 'react'

import { Badge } from '../ui/badge'
import { Skeleton } from '../ui/skeleton'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '../ui/table'

import { Filters } from './filters'
import { columns } from './items-table/columns'
import { WeekFilters } from './items-table/week-filters'
import { Statuses } from './statuses'
import { TableSkeleton } from './table-skeleton'
import { groupBy } from './utils/group-by'
import { useColumnDragDrop } from '@/hooks/use-column-controls'
import { useAddUsersProfilesMutation } from '@/store/api/profiles/profiles'
import { stopEvent } from '@/utils/stop-events'

interface Props {
    isLoading: boolean
    isFetching?: boolean
    table: TableType<any>
}

export const BaseTable: React.FC<Props> = ({ isLoading, table, isFetching }) => {
    const [addUsersProfiles] = useAddUsersProfilesMutation()

    const { onDragStart, onDrop } = useColumnDragDrop(table, 'items', addUsersProfiles)

    const colSpan = columns.length + 1

    const groupByOrder = groupBy(table.getRowModel().rows, 'original')

    return (
        <div className='rounded-md'>
            <div className='flex items-center justify-between gap-4 mb-3'>
                <Filters />
                <WeekFilters />
            </div>
            <Statuses table={table} page='items' />

            <Table>
                <TableHeader>
                    {isLoading ? (
                        <TableRow className='p-0'>
                            <TableCell colSpan={colSpan} className='h-[41px] py-1.5'>
                                <Skeleton className='w-full h-[41px]' />
                            </TableCell>
                        </TableRow>
                    ) : (
                        table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header, i) => {
                                    return i === 0 ? (
                                        <TableHead className='w-10' key={header.id}>
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                      header.column.columnDef.header,
                                                      header.getContext()
                                                  )}
                                        </TableHead>
                                    ) : (
                                        <TableHead
                                            draggable={
                                                !table.getState().columnSizingInfo
                                                    .isResizingColumn &&
                                                header.id !== 'flow' &&
                                                header.id !== 'status' &&
                                                header.id !== 'production_date'
                                            }
                                            className='w-2 last:w-auto'
                                            data-column-index={header.index}
                                            onDragStart={onDragStart}
                                            onDragOver={stopEvent}
                                            onDrop={onDrop}
                                            colSpan={header.colSpan}
                                            key={header.id}>
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                      header.column.columnDef.header,
                                                      header.getContext()
                                                  )}
                                        </TableHead>
                                    )
                                })}
                            </TableRow>
                        ))
                    )}
                </TableHeader>

                <TableBody>
                    {isLoading ? (
                        <TableSkeleton cellCount={columns.length} />
                    ) : table.getRowModel().rows?.length ? (
                        // table.getRowModel().rows.map((row) => {
                        //     return (
                        //         <TableRow
                        //             key={row.id}
                        //             className='odd:bg-secondary/60'
                        //             data-state={row.getIsSelected() && 'selected'}>
                        //             {row.getVisibleCells().map((cell) => (
                        //                 <TableCell
                        //                     className='py-1.5 h-[53px]'
                        //                     key={cell.id}>
                        //                     {flexRender(
                        //                         cell.column.columnDef.cell,
                        //                         cell.getContext()
                        //                     )}
                        //                 </TableCell>
                        //             ))}
                        //         </TableRow>
                        //     )
                        // })
                        groupByOrder.map((group) =>
                            group[1].map((row, index) => (
                                <Fragment key={row.id}>
                                    {index === 0 && (
                                        <TableRow className='pointer-events-none !p-0'>
                                            <TableCell
                                                className='!py-0 pl-8'
                                                colSpan={colSpan}>
                                                <Badge
                                                    variant='secondary'
                                                    className='py-2 ml-4 w-full !rounded-none'>
                                                    {group[0]}
                                                </Badge>
                                            </TableCell>
                                        </TableRow>
                                    )}
                                    <TableRow
                                        key={row.id}
                                        className='odd:bg-secondary/60'
                                        data-state={row.getIsSelected() && 'selected'}>
                                        {row.getVisibleCells().map((cell) => (
                                            <TableCell
                                                className='py-1.5 h-[53px]'
                                                key={cell.id}>
                                                {flexRender(
                                                    cell.column.columnDef.cell,
                                                    cell.getContext()
                                                )}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                </Fragment>
                            ))
                        )
                    ) : isFetching ? (
                        <TableSkeleton cellCount={columns.length} />
                    ) : (
                        <TableRow>
                            <TableCell colSpan={colSpan} className='h-24 text-center'>
                                No results.
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </div>
    )
}
