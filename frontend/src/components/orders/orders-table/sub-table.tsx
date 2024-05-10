import {
    flexRender,
    getCoreRowModel,
    getSortedRowModel,
    useReactTable
} from '@tanstack/react-table'

import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '../../ui/table'

import { subColumns } from './sub-columns'
import type { OriginItems } from '@/store/api/ebms/ebms.types'

interface Props {
    data: OriginItems[]
}

export const SubTable: React.FC<Props> = ({ data }) => {
    const subTable = useReactTable({
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        data,
        columns: subColumns,
        paginateExpandedRows: false,
        autoResetPageIndex: false
    })

    const originItemsRows = subTable.getRowModel().rows

    return (
        <Table>
            <TableHeader>
                {subTable.getHeaderGroups().map((headerGroup) => (
                    <TableRow key={headerGroup.id}>
                        {headerGroup.headers.map((header) => (
                            <TableHead
                                key={header.id}
                                className='py-1.5 px-0.5'>
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
                {originItemsRows.map((row) => (
                    <TableRow key={row?.original?.id}>
                        {row.getVisibleCells().map((cell) => (
                            <TableCell
                                className='py-1.5 px-0.5'
                                key={cell.id}>
                                {flexRender(
                                    cell.column.columnDef.cell,
                                    cell.getContext()
                                )}
                            </TableCell>
                        ))}
                    </TableRow>
                ))}
            </TableBody>
        </Table>
    )
}
