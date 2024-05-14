import {
    getCoreRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable
} from '@tanstack/react-table'
import { useEffect } from 'react'

import { BaseTable } from '../base-table'
import { selectOrders, setFlowsData } from '../store/orders'

import { useColumnOrder, useColumnVisibility } from '@/hooks/use-column-controls'
import { useGetFlowsQuery } from '@/store/api/flows/flows'
import { useGetUsersProfilesQuery } from '@/store/api/profiles/profiles'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'
import type { TableProps } from '@/types/table'

export function ItemsTable<TData, TValue>({
    columns,
    data,
    pageCount,
    limit,
    offset,
    isLoading,
    isFetching,
    setSorting,
    sorting,
    setPagination
}: TableProps<TData, TValue>) {
    const { data: usersProfilesData } = useGetUsersProfilesQuery()

    const { columnOrder } = useColumnOrder(usersProfilesData!, 'items')
    const { columnVisibility } = useColumnVisibility(usersProfilesData!, 'items', columns)

    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
        manualPagination: true,
        manualSorting: true,
        onPaginationChange: setPagination,
        getPaginationRowModel: getPaginationRowModel(),
        pageCount,
        onSortingChange: setSorting,
        getSortedRowModel: getSortedRowModel(),
        autoResetPageIndex: false,
        enableHiding: true,
        state: {
            sorting,
            // rowSelection: { TIDBOKSIBT2NF130: true },
            columnVisibility,
            columnOrder,
            pagination: {
                pageIndex: offset / limit,
                pageSize: limit
            }
        }
    })

    const category = useAppSelector(selectOrders).category

    const dispatch = useAppDispatch()

    const { data: flowsData, isFetching: isFlowsFetching } = useGetFlowsQuery({
        category__prod_type: category
    })

    useEffect(() => {
        dispatch(setFlowsData(flowsData?.results!))
    }, [flowsData])

    return (
        <BaseTable
            isFetching={isFetching || isFlowsFetching}
            isLoading={isLoading}
            table={table}
        />
    )
}
