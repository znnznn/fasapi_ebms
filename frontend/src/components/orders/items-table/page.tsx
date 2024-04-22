import type { SortingState } from '@tanstack/react-table'
import { useEffect, useState } from 'react'

import { selectOrders, setCurrentQueryParams } from '../store/orders'

import { columns } from './columns'
import { ItemsTable } from './table'
import { usePagination } from '@/hooks/use-pagination'
import { useGetItemsQuery } from '@/store/api/ebms/ebms'
import type { EBMSItemsData, EBMSItemsQueryParams } from '@/store/api/ebms/ebms.types'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'
import type { AccessToken } from '@/types/auth'

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
        production_date: date,
        completed: isOrderCompleted,
        is_scheduled: scheduled,
        category: category!
    }

    if (overdue) {
        queryParams.over_due = overdue
    }

    const dispatch = useAppDispatch()

    useEffect(() => {
        dispatch(setCurrentQueryParams(queryParams as EBMSItemsQueryParams))
    }, [category, limit, offset, scheduled, date, searchTerm, isOrderCompleted])

    const { currentData, isLoading, isFetching, refetch } = useGetItemsQuery(queryParams)
    const pageCount = Math.ceil(currentData?.count! / limit)

    const [dataToRender, setDataToRender] = useState(currentData?.results || [])

    useEffect(() => {
        setDataToRender(currentData?.results || [])
    }, [currentData])

    const token = JSON.parse(
        localStorage.getItem('token') || sessionStorage.getItem('token') || 'null'
    ) as AccessToken

    useEffect(() => {
        const websocket = new WebSocket('wss://api.dev-ebms.fun/ws/items/', token.access)

        websocket.addEventListener('message', (event) => {
            const dataToPatch = JSON.parse(event.data) as EBMSItemsData
            refetch()

            setDataToRender((prevData) => {
                const newData = prevData.map((item) => {
                    if (item.id === dataToPatch.id) {
                        return dataToPatch
                    } else {
                        return item
                    }
                })

                return newData
            })
        })

        return () => {
            websocket.close()
        }
    }, [])

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
