import type { SortingState } from '@tanstack/react-table'
import { useEffect, useMemo, useState } from 'react'

import { selectOrders, setCurrentQueryParams } from '../store/orders'

import { columns } from './columns'
import { ItemsTable } from './table'
import { useCurrentValue } from '@/hooks/use-current-value'
import { usePagination } from '@/hooks/use-pagination'
import { useWebSocket } from '@/hooks/use-web-socket'
import { useGetItemsQuery } from '@/store/api/ebms/ebms'
import type { EBMSItemsQueryParams } from '@/store/api/ebms/ebms.types'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'

export const ItemsTablePage = () => {
    const { limit, offset, setPagination } = usePagination()
    const [sorting, setSorting] = useState<SortingState>([
        {
            id: 'order',
            desc: true
        }
    ])

    const currentSortingTerm = sorting[0]?.desc ? `-${sorting[0]?.id}` : sorting[0]?.id

    const { category, scheduled, date, searchTerm, isOrderCompleted, overdue } =
        useAppSelector(selectOrders)

    useEffect(() => {
        setPagination({
            pageIndex: 0,
            pageSize: 10
        })
    }, [category])

    const queryParams: Partial<EBMSItemsQueryParams> = {
        offset,
        limit,
        ordering: currentSortingTerm,
        search: searchTerm,
        production_date: scheduled ? date : '',
        // completed: isOrderCompleted,
        is_scheduled: scheduled,
        category: category!
    }

    if (overdue) {
        queryParams.over_due = overdue
    }

    if (isOrderCompleted) {
        queryParams.completed = isOrderCompleted
    }

    const dispatch = useAppDispatch()

    useEffect(() => {
        dispatch(setCurrentQueryParams(queryParams as EBMSItemsQueryParams))
    }, [category, limit, offset, scheduled, date, searchTerm, isOrderCompleted])

    const { currentData, isLoading, isFetching, refetch } = useGetItemsQuery(queryParams)

    const currentCount = useCurrentValue(currentData?.count)

    const pageCount = useMemo(
        () => (currentCount ? Math.ceil(currentCount! / limit) : 0),
        [isLoading, limit, currentCount]
    )

    const { dataToRender } = useWebSocket({
        currentData: currentData!,
        endpoint: 'items',
        refetch
    })

    return (
        <div className='mx-auto'>
            <ItemsTable
                setPagination={setPagination}
                limit={limit}
                offset={offset}
                columns={columns}
                data={dataToRender}
                pageCount={Math.ceil(pageCount)}
                setSorting={setSorting}
                sorting={sorting}
                isLoading={isLoading}
                isFetching={isFetching}
            />
        </div>
    )
}
