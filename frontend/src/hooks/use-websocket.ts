import { useEffect } from 'react'

import type { AccessToken } from '@/types/auth'

interface UseWebsocketProps<T> {
    refetch: () => void
    endpoint: 'items' | 'orders'
    setDataToRender: React.Dispatch<React.SetStateAction<T[]>>
}

export const UseWebsocket = <T extends { id: string }>({
    refetch,
    setDataToRender,
    endpoint
}: UseWebsocketProps<T>) => {
    useEffect(() => {
        const token = JSON.parse(
            localStorage.getItem('token') || sessionStorage.getItem('token') || 'null'
        ) as AccessToken

        const websocket = new WebSocket(
            `wss://api.dev-ebms.fun/ws/${endpoint}/`,
            token.access
        )

        websocket.addEventListener('message', (event) => {
            const dataToPatch = JSON.parse(event.data) as T
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
}
