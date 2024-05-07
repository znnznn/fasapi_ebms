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

import { columns } from './items-table/columns'
import { Statuses } from './statuses'
import { TableSkeleton } from './table-skeleton'
import { groupBy } from './utils/group-by'
import { useColumnDragDrop } from '@/hooks/use-column-controls'
import { useAddUsersProfilesMutation } from '@/store/api/profiles/profiles'
import { useAppSelector } from '@/store/hooks/hooks'
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

    const groupByOrder = groupBy(table?.getRowModel()?.rows, 'original')

    const groupedView = useAppSelector((state) => state.orders.groupedView)

    return (
        <div className='rounded-md'>
            <Statuses
                table={table}
                page='items'
            />

            <Table>
                <TableHeader>
                    {isLoading ? (
                        <TableRow className='p-0'>
                            <TableCell
                                colSpan={colSpan}
                                className='h-[41px] py-1.5'>
                                <Skeleton className='w-full h-[41px]' />
                            </TableCell>
                        </TableRow>
                    ) : (
                        table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
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
                        groupedView ? (
                            groupByOrder.map((group) =>
                                group[1].map((row, index) => (
                                    <Fragment key={row.original?.id}>
                                        {index === 0 && (
                                            <TableRow className='pointer-events-none !p-0'>
                                                <TableCell
                                                    className='!py-0 pl-8'
                                                    colSpan={colSpan}>
                                                    <Badge
                                                        variant='secondary'
                                                        className='py-2 ml-4 w-full !rounded-none'>
                                                        {group[0]} |{' '}
                                                        {group[1][0].original?.customer}
                                                    </Badge>
                                                </TableCell>
                                            </TableRow>
                                        )}
                                        <TableRow
                                            key={row.original?.id}
                                            className='odd:bg-secondary/60'
                                            data-state={
                                                row.getIsSelected() && 'selected'
                                            }>
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
                        ) : (
                            table.getRowModel().rows.map((row) => {
                                return (
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
                                )
                            })
                        )
                    ) : isFetching ? (
                        <TableSkeleton cellCount={columns.length} />
                    ) : (
                        <TableRow>
                            <TableCell
                                colSpan={colSpan}
                                className='h-24 text-left pl-4'>
                                No results
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </div>
    )
}
