import {
    flexRender,
    getCoreRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable
} from '@tanstack/react-table'

import { selectOrders } from '../orders/store/orders'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '../ui/table'

import { Controls } from './controls'
import { TableSkeleton } from './table-skeleton'
import type { UsersData } from '@/store/api/users/users.types'
import { useAppSelector } from '@/store/hooks/hooks'
import type { BaseTableProps } from '@/types/table'

export function UsersTable<TValue>({
    columns,
    data,
    isLoading
}: BaseTableProps<UsersData, TValue>) {
    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        enableHiding: true
    })

    const searchTerm = useAppSelector(selectOrders).searchTerm.toLowerCase()

    const filteredData = table
        .getRowModel()
        .rows.filter(
            ({ original: { email, first_name, last_name } }) =>
                email.toLowerCase().includes(searchTerm) ||
                first_name.toLowerCase().includes(searchTerm) ||
                last_name.toLowerCase().includes(searchTerm)
        )

    return (
        <>
            <Controls table={table} />

            <Table className='mt-2'>
                <TableHeader>
                    {table.getHeaderGroups().map((headerGroup) => (
                        <TableRow key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                                <TableHead key={header.id}>
                                    {header.isPlaceholder
                                        ? null
                                        : flexRender(
                                              header.column.columnDef.header,
                                              header.getContext()
                                          )}
                                </TableHead>
                            ))}
                        </TableRow>
                    ))}
                </TableHeader>

                <TableBody>
                    {isLoading ? (
                        <TableSkeleton />
                    ) : filteredData.length ? (
                        filteredData.map((row) => (
                            <TableRow
                                key={row.id}
                                className='odd:bg-secondary/60'
                                data-state={row.getIsSelected() && 'selected'}>
                                {row.getVisibleCells().map((cell) => (
                                    <TableCell
                                        className='py-1.5 h-[53px] '
                                        key={cell.id}>
                                        {flexRender(
                                            cell.column.columnDef.cell,
                                            cell.getContext()
                                        )}
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))
                    ) : (
                        <TableRow>
                            <TableCell
                                colSpan={columns.length}
                                className='h-24 text-center'>
                                No results.
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </>
    )
}
