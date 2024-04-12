import type { SortingState } from '@tanstack/react-table'
import { useEffect, useState } from 'react'

import { selectOrders, setCurrentQueryParams } from '../store/orders'

import { columns } from './columns'
import { ItemsTable } from './table'
import { usePagination } from '@/hooks/use-pagination'
import { api } from '@/store/api'
import { useGetItemsQuery } from '@/store/api/ebms/ebms'
import type { EBMSItemsQueryParams } from '@/store/api/ebms/ebms.types'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'
import { AccessToken } from '@/types/auth'

export const ItemsTablePage = () => {
    const { limit, offset, setPagination } = usePagination()
    const [sorting, setSorting] = useState<SortingState>([
        {
            id: 'order',
            desc: true
        }
    ])

    const currentSortingTerm = sorting[0]?.desc ? `-${sorting[0]?.id}` : sorting[0]?.id

    const {
        category,
        scheduled,
        date,
        dateRange,
        searchTerm,
        isOrderCompleted
        // overdue
    } = useAppSelector(selectOrders)

    useEffect(() => {
        setPagination({
            pageIndex: 0,
            pageSize: 10
        })
    }, [category])

    const [fromDate, toDate] = dateRange
    const dateRangeToQuery = fromDate && toDate ? `${fromDate},${toDate}` : ''

    const queryParams: Partial<EBMSItemsQueryParams> = {
        offset,
        limit,
        ordering: currentSortingTerm,
        search: searchTerm,
        production_date: date,
        // over_due: overdue,
        completed: isOrderCompleted,
        date_range: dateRangeToQuery,
        is_scheduled: scheduled,
        category: category!
    }

    const dispatch = useAppDispatch()

    useEffect(() => {
        dispatch(setCurrentQueryParams(queryParams as EBMSItemsQueryParams))
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

    const { currentData, isLoading, isFetching, refetch } = useGetItemsQuery(queryParams)
    const pageCount = Math.ceil(currentData?.count! / limit)

    const token = JSON.parse(
        localStorage.getItem('token') || sessionStorage.getItem('token') || 'null'
    ) as AccessToken

    const websocket = new WebSocket(
        'ws://ec2-35-183-142-252.ca-central-1.compute.amazonaws.com/ws/items/',
        token.access
    )

    websocket.addEventListener('message', (event) => {
        console.log(event.data)
        refetch()
        api.util.invalidateTags(['EBMSItems'])
    })

    return (
        <div className='mx-auto'>
            <ItemsTable
                setPagination={setPagination}
                limit={limit}
                offset={offset}
                columns={columns}
                data={currentData?.results! || []}
                pageCount={Math.ceil(pageCount)}
                setSorting={setSorting}
                sorting={sorting}
                isLoading={isLoading}
                isFetching={isFetching}
            />
        </div>
    )
}
