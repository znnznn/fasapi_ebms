import {
    getCoreRowModel,
    getExpandedRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable
} from '@tanstack/react-table'
import { useEffect } from 'react'

import { selectOrders } from '../store/orders'

import { CollapsibleTable } from './collapsible-table'
import { useColumnOrder, useColumnVisibility } from '@/hooks/use-column-controls'
import type { OrdersData } from '@/store/api/ebms/ebms.types'
import { useGetUsersProfilesQuery } from '@/store/api/profiles/profiles'
import { useAppSelector } from '@/store/hooks/hooks'
import type { TableProps } from '@/types/table'

export const OrdersTable = <TData, TValue>({
    columns,
    data,
    pageCount,
    limit,
    offset,
    isFetching,
    isLoading,
    setSorting,
    sorting,
    setPagination
}: TableProps<TData, TValue>) => {
    const { data: usersProfilesData } = useGetUsersProfilesQuery()

    const { columnOrder } = useColumnOrder(usersProfilesData!, 'orders')

    const { columnVisibility } = useColumnVisibility(
        usersProfilesData!,
        'orders',
        columns
    )

    const table = useReactTable({
        getSubRows: (originalRow) => (originalRow as OrdersData)?.origin_items as any,
        getCoreRowModel: getCoreRowModel(),
        onPaginationChange: setPagination,
        getPaginationRowModel: getPaginationRowModel(),
        onSortingChange: setSorting,
        getSortedRowModel: getSortedRowModel(),
        getExpandedRowModel: getExpandedRowModel(),
        data,
        columns,
        manualPagination: true,
        manualSorting: true,
        manualExpanding: true,
        pageCount,
        paginateExpandedRows: false,
        autoResetPageIndex: false,
        state: {
            columnVisibility,
            sorting,
            columnOrder,
            pagination: {
                pageIndex: offset / limit,
                pageSize: limit
            }
        }
    })

    const overdue = useAppSelector(selectOrders).overdue
    const completed = useAppSelector(selectOrders).isOrderCompleted

    useEffect(() => {
        table.setPageIndex(0)
    }, [overdue, completed])

    return (
        <CollapsibleTable
            isLoading={isLoading}
            table={table}
            isFetching={isFetching}
        />
    )
}
