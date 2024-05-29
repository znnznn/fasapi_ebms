import { type Table as TableType, flexRender } from '@tanstack/react-table'
// import { AnimatePresence, motion } from 'framer-motion'
import { Fragment, useEffect } from 'react'

import { Badge } from '../ui/badge'
import { Checkbox } from '../ui/checkbox'
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
import { selectCategory } from './store/orders'
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

    const onCheckedChange = (value: boolean, group: any[]) => {
        const currentGroup = groupByOrder.filter((gr) => gr[0] === group[0])
        const currentGroupIds = currentGroup[0][1].map((obj) => obj.id)

        const obj = currentGroupIds
            .map((obj) => ({ [obj]: true }))
            .reduce((acc, val) => ({ ...acc, ...val }), {})

        if (value) {
            table.setRowSelection((prev) => ({
                ...prev,
                ...obj
            }))
        } else {
            table.setRowSelection((prev) => {
                const newSelection = { ...prev }
                currentGroupIds.forEach((id) => {
                    if (newSelection[id]) {
                        delete newSelection[id]
                    }
                })
                return newSelection
            })
        }
    }

    const category = useAppSelector(selectCategory)
    const scheduled = useAppSelector((state) => state.orders.scheduled)
    useEffect(() => {
        table.setRowSelection({})
    }, [category, scheduled])

    // const MotionTableRow = motion(TableRow, { forwardMotionProps: true })

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
                                className='h-[41px] py-1.5 !px-0'>
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
                                            className='w-2 !px-0.5 last:w-auto'
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
                    {/* <AnimatePresence initial={false}> */}
                    {isLoading ? (
                        <TableSkeleton cellCount={columns.length} />
                    ) : table.getRowModel().rows?.length ? (
                        groupedView ? (
                            groupByOrder.map((group) =>
                                group[1].map((row, index) => {
                                    const isIndeterminate = group[1].some((row) =>
                                        row.getIsSelected()
                                    )
                                        ? group[1].every((row) => row.getIsSelected())
                                            ? true
                                            : 'indeterminate'
                                        : false

                                    return (
                                        <Fragment key={row.original?.id}>
                                            {index === 0 && (
                                                <TableRow
                                                    // initial={false}
                                                    // animate={{
                                                    //     opacity: 1,
                                                    //     x: 0
                                                    // }}
                                                    // exit={{
                                                    //     opacity:
                                                    //         isFetching || isLoading
                                                    //             ? 1
                                                    //             : 0,
                                                    //     x:
                                                    //         isFetching || isLoading
                                                    //             ? 0
                                                    //             : -1000
                                                    // }}
                                                    // transition={{
                                                    //     duration:
                                                    //         isFetching || isLoading
                                                    //             ? 0
                                                    //             : 0.3
                                                    // }}
                                                    className=' !p-0'>
                                                    <TableCell
                                                        className='!p-0'
                                                        colSpan={colSpan}>
                                                        <Badge
                                                            variant='secondary'
                                                            className='py-2 w-full !m-0 !rounded-none'>
                                                            <Checkbox
                                                                className='mr-4'
                                                                checked={isIndeterminate}
                                                                value={row.id}
                                                                onCheckedChange={(
                                                                    value
                                                                ) => {
                                                                    onCheckedChange(
                                                                        !!value,
                                                                        group
                                                                    )
                                                                }}
                                                                aria-label='Select row'
                                                            />
                                                            <div className='pl-4'>
                                                                {group[0]} |{' '}
                                                                {
                                                                    group[1][0].original
                                                                        ?.customer
                                                                }
                                                            </div>
                                                        </Badge>
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                            <TableRow
                                                // initial={false}
                                                // animate={{
                                                //     opacity: 1,
                                                //     x: 0
                                                // }}
                                                // exit={{
                                                //     opacity:
                                                //         isFetching || isLoading
                                                //             ? 1
                                                //             : 0,
                                                //     x:
                                                //         isFetching || isLoading
                                                //             ? 0
                                                //             : -1000
                                                // }}
                                                // transition={{
                                                //     duration:
                                                //         isFetching || isLoading
                                                //             ? 0
                                                //             : 0.3
                                                // }}
                                                className='odd:bg-secondary/60'
                                                data-state={
                                                    row.getIsSelected() && 'selected'
                                                }>
                                                {row.getVisibleCells().map((cell) => (
                                                    <TableCell
                                                        className='py-1.5 h-[53px] !px-0.5'
                                                        key={cell.id}>
                                                        {flexRender(
                                                            cell.column.columnDef.cell,
                                                            cell.getContext()
                                                        )}
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                        </Fragment>
                                    )
                                })
                            )
                        ) : (
                            table.getRowModel().rows.map((row) => {
                                return (
                                    <TableRow
                                        // initial={false}
                                        // animate={{
                                        //     opacity: 1,
                                        //     x: 0
                                        // }}
                                        // exit={{
                                        //     opacity: isFetching || isLoading ? 1 : 0,
                                        //     x: isFetching || isLoading ? 0 : -1000
                                        // }}
                                        // transition={{
                                        //     duration: isFetching || isLoading ? 0 : 0.3
                                        // }}
                                        key={row.original?.id}
                                        className='odd:bg-secondary/60'
                                        data-state={row.getIsSelected() && 'selected'}>
                                        {row.getVisibleCells().map((cell) => (
                                            <TableCell
                                                className='py-1.5 h-[53px] !px-0.5'
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
                    {/* </AnimatePresence> */}
                </TableBody>
            </Table>
        </div>
    )
}
