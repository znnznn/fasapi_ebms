import { api } from '..'

import { embs } from '../ebms/ebms'
import type {
    EBMSItemsQueryParams,
    Item,
    OrderItemsQueryParams,
    OrdersQueryParams
} from '../ebms/ebms.types'

import type {
    Flow,
    ItemsAddData,
    ItemsData,
    ItemsPatchData,
    ItemsResponse
} from './items.types'
import { store } from '@/store'
import type { BaseQueryParams } from '@/types/api'
import { getQueryParamString } from '@/utils/get-query-param-string'

export const items = api.injectEndpoints({
    endpoints: (build) => ({
        getItems: build.query<ItemsResponse, Partial<BaseQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `items/?${queryString}`
            },

            providesTags: ['Items']
        }),
        getItem: build.query<ItemsData, number>({
            query: (id) => `items/${id}`,
            providesTags: ['Items']
        }),
        addOrderItem: build.mutation<void, Partial<ItemsAddData>>({
            query: (data) => ({
                url: `items/`,
                method: 'POST',
                body: data
            }),
            async onQueryStarted(data, { dispatch, queryFulfilled }) {
                const queryKeyParams = store.getState().orders.currentQueryParams

                const patchResult = dispatch(
                    embs.util.updateQueryData(
                        'getOrders',
                        queryKeyParams as OrderItemsQueryParams,
                        (draft) => {
                            const itemToAdd: Item = {
                                id: Math.random() * 1000,
                                order: Math.random() * 1000,
                                origin_item: (Math.random() * 1000).toString(),
                                flow: {
                                    id: data.flow!,
                                    name: data?.flowName!,
                                    stages: []
                                },
                                production_date: '',
                                priority: 0,
                                time: '',
                                packages: 0,
                                location: 0,
                                comments: [],
                                stage: {
                                    id: Math.random() * 1000,
                                    name: '',
                                    position: 1,
                                    item_ids: [],
                                    flow: 1,
                                    color: ''
                                }
                            }

                            const order = draft.results.find(
                                (order) => order.id === data.order
                            )

                            const originItem = order?.origin_items.find(
                                (item) => item.id === data.origin_item
                            )

                            if (originItem) {
                                Object.assign(originItem, {
                                    item: itemToAdd
                                })
                            }
                        }
                    )
                )

                try {
                    await queryFulfilled
                } catch {
                    patchResult.undo()
                }
            },
            invalidatesTags: ['Items', 'Orders', 'EBMSItems']
        }),
        addItem: build.mutation<ItemsData, Partial<ItemsAddData>>({
            query: (data) => ({
                url: `items/`,
                method: 'POST',
                body: data
            }),
            async onQueryStarted(data, { dispatch, queryFulfilled }) {
                const queryKeyParams = store.getState().orders.currentQueryParams

                const patchResult = dispatch(
                    embs.util.updateQueryData(
                        'getItems',
                        queryKeyParams as OrderItemsQueryParams,
                        (draft) => {
                            const itemToAdd: Item = {
                                id: Math.random() * 1000,
                                order: Math.random() * 1000,
                                origin_item: (Math.random() * 1000).toString(),
                                flow: {
                                    id: data?.flow!,
                                    name: data?.flowName!,
                                    stages: []
                                },
                                time: data.time!,
                                production_date: data?.production_date!,
                                priority: data?.priority!,
                                packages: data?.packages!,
                                location: data?.location!,
                                comments: [],
                                stage: null
                            }

                            const item = draft.results.find(
                                (item) => item.id === data.origin_item
                            )

                            if (item?.id) {
                                Object.assign(item, {
                                    item: itemToAdd
                                })
                            }
                        }
                    )
                )

                try {
                    await queryFulfilled
                } catch {
                    patchResult.undo()
                }
            },
            invalidatesTags: ['Items', 'Orders', 'EBMSItems']
        }),
        patchOrderItem: build.mutation<void, ItemsPatchData>({
            query: ({ data, id }) => ({
                url: `items/${id}/`,
                method: 'PATCH',
                body: data
            }),
            async onQueryStarted(
                { data: { ...data }, stageColor, stageName, id },
                { dispatch, queryFulfilled }
            ) {
                const queryKeyParams = store.getState().orders.currentQueryParams

                const patchResult = dispatch(
                    embs.util.updateQueryData(
                        'getOrders',
                        queryKeyParams as OrdersQueryParams,
                        (draft) => {
                            const order = draft.results.find(
                                (order) => order.id === data.order
                            )

                            const item = order?.origin_items.find(
                                (item) => item.item.id === id
                            )

                            const flowToPatch: Flow = {
                                id: data.flow!,
                                name: data.flowName!,
                                stages: []
                            }

                            if (stageName && stageColor) {
                                Object.assign(data, {
                                    stage: {
                                        id: data.stage!,
                                        name: stageName!,
                                        color: stageColor!
                                    }
                                })
                            }

                            if (data.flowName && item?.item) {
                                Object.assign(item?.item, {
                                    ...data,
                                    flow: flowToPatch,
                                    stage: null
                                })
                            }
                            // else if (item?.item) {
                            //     Object.assign(item?.item, {
                            //         ...data,
                            //         stage: null
                            //     })
                            // }
                        }
                    )
                )

                try {
                    await queryFulfilled
                } catch {
                    patchResult.undo()
                }
            },
            invalidatesTags: ['Items', 'Orders', 'EBMSItems', 'Categories', 'Capacities']
        }),
        patchItem: build.mutation<ItemsData, ItemsPatchData>({
            query: ({ data, id }) => ({
                url: `items/${id}/`,
                method: 'PATCH',
                body: data
            }),
            async onQueryStarted(
                { data, stageColor, stageName, id },
                { dispatch, queryFulfilled }
            ) {
                const queryKeyParams = store.getState().orders.currentQueryParams

                const patchResult = dispatch(
                    embs.util.updateQueryData(
                        'getItems',
                        queryKeyParams as EBMSItemsQueryParams,
                        (draft) => {
                            const item = draft.results.find(
                                (item) => item.item?.id === id
                            )

                            const flowToPatch: Flow = {
                                id: data.flow!,
                                name: data.flowName!,
                                stages: []
                            }

                            const dataToPatch = {
                                ...data
                            }

                            if (stageName && stageColor) {
                                Object.assign(dataToPatch, {
                                    stage: {
                                        id: data.stage!,
                                        name: stageName!,
                                        color: stageColor!
                                    }
                                })
                            }

                            if (data?.flowName && item?.item) {
                                Object.assign(item?.item, {
                                    ...data,
                                    flow: flowToPatch,
                                    stage: null
                                })
                            }
                            // else if (item?.item) {
                            //     Object.assign(item?.item, {
                            //         ...dataToPatch
                            //     })
                            // }
                        }
                    )
                )

                try {
                    await queryFulfilled
                } catch {
                    patchResult.undo()
                }
            },
            invalidatesTags: ['Items', 'Orders', 'EBMSItems', 'Categories', 'Capacities']
        }),
        removeItem: build.mutation<void, number>({
            query: (id) => ({
                url: `items/${id}/`,
                method: 'DELETE'
            }),
            invalidatesTags: ['Items']
        }),
        resetItemStages: build.mutation<void, number>({
            query: (id) => ({
                url: `items/${id}/rest-stages/`,
                method: 'DELETE'
            }),
            // async onQueryStarted(id, { dispatch, queryFulfilled }) {
            //     const queryKeyParams = store.getState().orders.currentQueryParams

            //     const patchResult = dispatch(
            //         embs.util.updateQueryData(
            //             'getItems',
            //             queryKeyParams as EBMSItemsQueryParams,
            //             (draft) => {
            //                 const item = draft.results.find(
            //                     (item) => item.item?.id === id
            //                 )

            //                 if (item?.item) {
            //                     Object.assign(item?.item, {
            //                         stage: {}
            //                     })
            //                 }
            //             }
            //         )
            //     )

            //     try {
            //         await queryFulfilled
            //     } catch {
            //         patchResult.undo()
            //     }
            // },
            invalidatesTags: ['Items', 'EBMSItems', 'Orders']
        })
    })
})

export const {
    useGetItemsQuery,
    useGetItemQuery,
    useAddItemMutation,
    usePatchOrderItemMutation,
    useAddOrderItemMutation,
    usePatchItemMutation,
    useResetItemStagesMutation,
    useRemoveItemMutation
} = items
