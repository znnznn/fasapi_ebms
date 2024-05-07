import { useEffect, useState } from 'react'

import type {
    EBMSItemsData,
    EBMSItemsResponse,
    OrdersData,
    OrdersResponse
} from '@/store/api/ebms/ebms.types'
import type { AccessToken } from '@/types/auth'

interface OrdersWebSocket {
    endpoint: 'orders'
    currentData: OrdersResponse
    refetch: () => void
}

interface ItemsWebSocket {
    endpoint: 'items'
    currentData: EBMSItemsResponse
    refetch: () => void
}

type UseWebsocketProps = OrdersWebSocket | ItemsWebSocket

export const useWebSocket = <T extends UseWebsocketProps>({
    currentData,
    refetch,
    endpoint
}: T) => {
    const [dataToRender, setDataToRender] = useState<(OrdersData | EBMSItemsData)[]>(
        currentData?.results || []
    )

    useEffect(() => {
        setDataToRender(currentData?.results || [])
    }, [currentData])

    const token = JSON.parse(
        localStorage.getItem('token') || sessionStorage.getItem('token') || ''
    ) as AccessToken

    useEffect(() => {
        const websocket = new WebSocket(
            `wss://api.dev-ebms.fun/ws/${endpoint}/`,
            token.access
        )

        websocket.addEventListener('message', (event) => {
            const dataToPatch = JSON.parse(event.data) as OrdersData | EBMSItemsData

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
            // websocket.removeEventListener('message', () => {})
        }
    }, [])

    return {
        dataToRender
    } as T extends { endpoint: 'orders' }
        ? { dataToRender: OrdersResponse['results'] }
        : { dataToRender: EBMSItemsResponse['results'] }
}
