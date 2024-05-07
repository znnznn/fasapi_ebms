import type { SortingState } from '@tanstack/react-table'
import { useEffect, useMemo, useState } from 'react'

import { selectOrders, setCurrentQueryParams } from '../store/orders'

import { columns } from './columns'
import { OrdersTable } from './table'
import { useCurrentValue } from '@/hooks/use-current-value'
import { usePagination } from '@/hooks/use-pagination'
import { useWebSocket } from '@/hooks/use-web-socket'
import { useGetOrdersQuery } from '@/store/api/ebms/ebms'
import type { OrdersQueryParams } from '@/store/api/ebms/ebms.types'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'

export const OrderTablePage = () => {
    const { limit, offset, setPagination } = usePagination()
    const [sorting, setSorting] = useState<SortingState>([
        {
            id: 'invoice',
            desc: true
        }
    ])

    const dispatch = useAppDispatch()

    const currentSortingTerm = sorting[0]?.desc ? `-${sorting[0]?.id}` : sorting[0]?.id

    const { category, scheduled, date, searchTerm, isOrderCompleted, overdue } =
        useAppSelector(selectOrders)

    useEffect(() => {
        setPagination({
            pageIndex: 0,
            pageSize: 10
        })
    }, [category])

    const queryParams: Partial<OrdersQueryParams> = {
        offset,
        limit,
        is_scheduled: scheduled,
        ordering: currentSortingTerm,
        search: searchTerm
    }

    if (isOrderCompleted) {
        queryParams.completed = isOrderCompleted
    }

    if (overdue) {
        queryParams.over_due = overdue
    }

    useEffect(() => {
        dispatch(setCurrentQueryParams(queryParams as OrdersQueryParams))
    }, [category, limit, offset, scheduled, date, searchTerm, isOrderCompleted])

    const { currentData, isLoading, isFetching, refetch } = useGetOrdersQuery(queryParams)

    const { dataToRender } = useWebSocket({
        currentData: currentData!,
        endpoint: 'orders',
        refetch
    })

    const currentCount = useCurrentValue(currentData?.count)

    const pageCount = useMemo(
        () => (currentCount ? Math.ceil(currentCount! / limit) : 0),
        [isLoading, limit, currentCount]
    )

    return (
        <div className='mx-auto'>
            <OrdersTable
                setPagination={setPagination}
                limit={limit}
                offset={offset}
                columns={columns}
                data={dataToRender}
                pageCount={pageCount}
                setSorting={setSorting}
                sorting={sorting}
                isLoading={isLoading}
                isFetching={isFetching}
            />
        </div>
    )
}
