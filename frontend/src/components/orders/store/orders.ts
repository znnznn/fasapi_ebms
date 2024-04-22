import { type PayloadAction, createSlice } from '@reduxjs/toolkit'

import type {
    Capacity,
    EBMSItemsQueryParams,
    OrdersQueryParams
} from '@/store/api/ebms/ebms.types'
import type { FlowsData } from '@/store/api/flows/flows.types'

type QueryKeyParams = Partial<OrdersQueryParams | EBMSItemsQueryParams> | {}

interface State {
    isOrderCompleted: boolean
    category: string | undefined
    scheduled: boolean
    overdue: boolean
    date: string
    searchTerm: string
    currentQueryParams: QueryKeyParams
    currentCapacity: Capacity
    flowsData: FlowsData[]
}

const initialState: State = {
    isOrderCompleted: false,
    category: '',
    overdue: false,
    scheduled: false,
    date: '',
    searchTerm: '',
    flowsData: [],
    currentQueryParams: {},
    currentCapacity: {
        capacity: null,
        total_capacity: null
    }
}

export const ordersSlice = createSlice({
    name: 'orders',
    initialState,
    reducers: {
        setOrderCompleted(state, action: PayloadAction<boolean>) {
            state.isOrderCompleted = action.payload
        },
        setCategory(state, action: PayloadAction<string | undefined>) {
            if (action.payload === 'All') {
                state.category = undefined
            } else {
                state.category = action.payload
            }
        },
        setFlowsData(state, action: PayloadAction<FlowsData[]>) {
            state.flowsData = action.payload
        },
        setSearch(state, action: PayloadAction<string>) {
            state.searchTerm = action.payload
        },
        setScheduled(state, action: PayloadAction<boolean>) {
            state.scheduled = action.payload
        },
        setDate(state, action: PayloadAction<string>) {
            state.date = action.payload
        },

        setOverDue(state, action: PayloadAction<boolean>) {
            state.overdue = action.payload
        },
        setCurrentQueryParams(
            state,
            action: PayloadAction<EBMSItemsQueryParams | OrdersQueryParams>
        ) {
            state.currentQueryParams = action.payload
        },
        setCurrentCapacity(state, action: PayloadAction<Capacity>) {
            state.currentCapacity = action.payload
        },
        resetAllOrders() {
            return initialState
        }
    }
})

export const {
    setCurrentQueryParams,
    setOverDue,
    setOrderCompleted,
    setCategory,
    resetAllOrders,
    setScheduled,
    setDate,
    setSearch,
    setFlowsData,
    setCurrentCapacity
} = ordersSlice.actions

export const selectOrders = (state: { orders: State }) => state.orders
export const selectCategory = (state: { orders: State }) => state.orders.category
