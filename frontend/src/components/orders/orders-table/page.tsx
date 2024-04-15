import type { SortingState } from '@tanstack/react-table'
import { useEffect, useState } from 'react'

import { selectOrders, setCurrentQueryParams } from '../store/orders'

import { columns } from './columns'
import { OrdersTable } from './table'
import { usePagination } from '@/hooks/use-pagination'
import { api } from '@/store/api'
import { useGetOrdersQuery } from '@/store/api/ebms/ebms'
import type { OrdersQueryParams } from '@/store/api/ebms/ebms.types'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'
import { AccessToken } from '@/types/auth'

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

    const {
        category,
        scheduled,
        date,
        dateRange,
        searchTerm,
        isOrderCompleted,
        overdue
    } = useAppSelector(selectOrders)

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
        completed: isOrderCompleted,
        ordering: currentSortingTerm,
        over_due: overdue,
        search: searchTerm
    }

    useEffect(() => {
        dispatch(setCurrentQueryParams(queryParams as OrdersQueryParams))
    }, [
        category,
        limit,
        offset,
        scheduled,
        date,
        dateRange,
        searchTerm,
        isOrderCompleted
    ])

    const { currentData, isLoading, isFetching, refetch } = useGetOrdersQuery(queryParams)

    const token = JSON.parse(
        localStorage.getItem('token') || sessionStorage.getItem('token') || 'null'
    ) as AccessToken

    const websocket = new WebSocket('wss://dev-ebms.fun/ws/items/', token.access)

    websocket.addEventListener('message', (event) => {
        console.log(event.data)
        refetch()
        api.util.invalidateTags(['Orders'])
    })

    const pageCount = Math.ceil(currentData?.count! / limit)

    return (
        <div className='mx-auto'>
            <OrdersTable
                setPagination={setPagination}
                limit={limit}
                offset={offset}
                columns={columns}
                data={currentData?.results! || []}
                pageCount={pageCount}
                setSorting={setSorting}
                sorting={sorting}
                isLoading={isLoading}
                isFetching={isFetching}
            />
        </div>
    )
}
