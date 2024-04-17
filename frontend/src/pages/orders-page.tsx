import { useEffect } from 'react'

import { Header } from '@/components/orders/header'
import { ItemsTablePage } from '@/components/orders/items-table/page'
import { OrderTablePage } from '@/components/orders/orders-table/page'
import { resetAllOrders, selectCategory } from '@/components/orders/store/orders'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'

const OrdersPage = () => {
    const category = useAppSelector(selectCategory)

    const dispatch = useAppDispatch()

    useEffect(() => {
        return () => {
            dispatch(resetAllOrders())
        }
    }, [])

    return (
        <div>
            <Header />
            {category ? <ItemsTablePage /> : <OrderTablePage />}
        </div>
    )
}

export default OrdersPage
