import { Skeleton } from '@radix-ui/themes'
import { type Table as TableType, flexRender } from '@tanstack/react-table'
import { AnimatePresence, motion } from 'framer-motion'
import { useEffect } from 'react'

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '../../ui/table'
import { columns } from '../items-table/columns'
import { WeekFilters } from '../items-table/week-filters'
import { Statuses } from '../statuses'
import { TableSkeleton } from '../table-skeleton'

import { SubTable } from './sub-table'
import { Collapsible, CollapsibleContent } from '@/components/ui/collapsible'
import { useColumnDragDrop } from '@/hooks/use-column-controls'
import type { OrdersData } from '@/store/api/ebms/ebms.types'
import { useAddUsersProfilesMutation } from '@/store/api/profiles/profiles'
import { useAppSelector } from '@/store/hooks/hooks'
import { stopEvent } from '@/utils/stop-events'

interface Props {
    isLoading: boolean
    isFetching?: boolean
    table: TableType<any>
}

export const CollapsibleTable: React.FC<Props> = ({ isLoading, table, isFetching }) => {
    const [addUsersProfiles] = useAddUsersProfilesMutation()

    const { onDragStart, onDrop } = useColumnDragDrop(table, 'orders', addUsersProfiles)

    const colSpan = columns.length + 1

    const scheduled = useAppSelector((state) => state.orders.scheduled)

    useEffect(() => {
        table.setRowSelection({})
    }, [scheduled])

    const MotionTableRow = motion(TableRow, { forwardMotionProps: true })

    return (
        <div className='rounded-md'>
            <WeekFilters />
            <Statuses
                table={table}
                page='orders'
            />

            <Table>
                <TableHeader>
                    {isLoading ? (
                        <TableRow className='p-0'>
                            <TableCell
                                colSpan={colSpan}
                                className='h-[39px] py-1.5 !px-0'>
                                <Skeleton className='opacity-50 w-full h-[39px]' />
                            </TableCell>
                        </TableRow>
                    ) : (
                        table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => (
                                    <TableHead
                                        className='px-0.5 w-2 last:w-auto'
                                        draggable={
                                            !table.getState().columnSizingInfo
                                                .isResizingColumn
                                        }
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
                                ))}
                            </TableRow>
                        ))
                    )}
                </TableHeader>

                <TableBody>
                    <AnimatePresence initial={false}>
                        {isLoading ? (
                            <TableSkeleton cellCount={columns.length} />
                        ) : table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => {
                                const originItems = (row.original as OrdersData)
                                    .origin_items

                                return (
                                    <Collapsible
                                        key={row?.original?.id}
                                        asChild>
                                        <>
                                            <MotionTableRow
                                                initial={false}
                                                animate={{
                                                    opacity: 1,
                                                    x: 0
                                                }}
                                                exit={{
                                                    opacity:
                                                        isFetching || isLoading ? 1 : 0,
                                                    x: isFetching || isLoading ? 0 : -1000
                                                }}
                                                transition={{
                                                    duration:
                                                        isFetching || isLoading ? 0 : 0.3
                                                }}
                                                className='odd:bg-secondary/60'
                                                data-state={
                                                    row.getIsSelected() && 'selected'
                                                }>
                                                {row.getVisibleCells().map((cell) => (
                                                    <TableCell
                                                        className='py-1.5 px-0.5 first:w-10 [&div]:h-[53px]'
                                                        key={cell.id}>
                                                        {flexRender(
                                                            cell.column.columnDef.cell,
                                                            cell.getContext()
                                                        )}
                                                    </TableCell>
                                                ))}
                                            </MotionTableRow>

                                            <CollapsibleContent asChild>
                                                <tr>
                                                    <motion.td
                                                        initial={false}
                                                        animate={{
                                                            opacity: 1,
                                                            x: 0
                                                        }}
                                                        exit={{
                                                            opacity:
                                                                isFetching || isLoading
                                                                    ? 1
                                                                    : 0,
                                                            x:
                                                                isFetching || isLoading
                                                                    ? 0
                                                                    : -1000
                                                        }}
                                                        transition={{
                                                            duration:
                                                                isFetching || isLoading
                                                                    ? 0
                                                                    : 0.3
                                                        }}
                                                        className='max-w-[100vw]'
                                                        colSpan={colSpan}>
                                                        <SubTable data={originItems} />
                                                    </motion.td>
                                                </tr>
                                            </CollapsibleContent>
                                        </>
                                    </Collapsible>
                                )
                            })
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
                    </AnimatePresence>
                </TableBody>
            </Table>
        </div>
    )
}
