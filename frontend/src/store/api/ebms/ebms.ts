import { api } from '..'

import type {
    AllCategoriesData,
    CalendarQueryParams,
    CalendarResponse,
    CategoriesQueryParams,
    CategoriesResponse,
    EBMSItemsQueryParams,
    EBMSItemsResponse,
    OrderItemsQueryParams,
    OrderQueryParams,
    OrdersData,
    OrdersItemsResponse,
    OrdersQueryParams,
    OrdersResponse
} from './ebms.types'
import { getQueryParamString } from '@/utils/get-query-param-string'

export const embs = api.injectEndpoints({
    endpoints: (build) => ({
        getCalendar: build.query<CalendarResponse, CalendarQueryParams>({
            query: ({ year, month }) => `ebms/calendar/${year}/${month}`,
            providesTags: ['Calendar']
        }),
        getCategories: build.query<CategoriesResponse, Partial<CategoriesQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `ebms/categories?${queryString}`
            },
            providesTags: ['Categories']
        }),
        getAllCategories: build.query<AllCategoriesData[], void>({
            query: () => 'ebms/categories/all'
        }),
        getOrders: build.query<OrdersResponse, Partial<OrdersQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `ebms/orders?${queryString}`
            },
            providesTags: ['Orders']
        }),
        getOrder: build.query<OrdersData, Partial<OrderQueryParams>>({
            query: ({ autoid }) => `ebms/orders/${autoid}`
        }),
        getItems: build.query<EBMSItemsResponse, Partial<EBMSItemsQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)

                return `ebms/items?${queryString}`
            },
            providesTags: ['EBMSItems']
        }),
        getOrdersItems: build.query<OrdersItemsResponse, Partial<OrderItemsQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `ebms/orders-items?${queryString}`
            }
        })
    })
})

export const {
    useGetCalendarQuery,
    useGetOrderQuery,
    useLazyGetOrderQuery,
    useGetCategoriesQuery,
    useGetAllCategoriesQuery,
    useGetOrdersQuery,
    useGetItemsQuery,
    useGetOrdersItemsQuery
} = embs
