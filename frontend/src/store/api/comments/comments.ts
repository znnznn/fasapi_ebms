import { api } from '..'

import { embs } from '../ebms/ebms'
import type {
    EBMSItemsQueryParams,
    Item,
    ItemComment,
    OrdersQueryParams
} from '../ebms/ebms.types'
import type { UsersData } from '../users/users.types'

import type {
    CommentsAddData,
    CommentsData,
    CommentsPatchData,
    CommentsResponse
} from './comments.types'
import { type RootState, store } from '@/store/index'
import type { BaseQueryParams } from '@/types/api'
import { getQueryParamString } from '@/utils/get-query-param-string'

export const comments = api.injectEndpoints({
    endpoints: (build) => ({
        getComments: build.query<CommentsResponse, Partial<BaseQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `comments/?${queryString}`
            },
            providesTags: ['Comments']
        }),
        getComment: build.query<CommentsData, number>({
            query: (id) => `comments/${id}`,
            providesTags: ['Comments']
        }),
        addOrderComment: build.mutation<void, CommentsAddData>({
            query: (data) => ({
                url: `comments/`,
                method: 'POST',
                body: data
            }),
            async onQueryStarted({ ...data }, { dispatch, queryFulfilled, getState }) {
                const { role, category, ...userDataToPatch } = (getState() as RootState)
                    ?.auth?.user as UsersData
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
                                (item) => item.id === data.item
                            )

                            const dataToPatch: ItemComment = {
                                item: data.item,
                                text: data.text,
                                user: userDataToPatch,
                                id: Math.floor(Math.random() * 1000),
                                created_at: new Date().toISOString()
                            }

                            if (item?.item) {
                                item?.item?.comments.push(dataToPatch)
                            } else {
                                const itemToPatch: Item = {
                                    id: Math.floor(Math.random() * 1000),
                                    origin_item: Math.floor(
                                        Math.random() * 1000
                                    ).toString(),
                                    flow: {
                                        id: '' as any,
                                        name: '',
                                        stages: []
                                    },
                                    time: '',
                                    comments: [dataToPatch],
                                    order: Math.floor(Math.random() * 1000),
                                    priority: 0,
                                    packages: 0,
                                    location: 0,
                                    production_date: '',
                                    stage: null
                                }

                                Object.assign(item!, {
                                    item: itemToPatch
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

            invalidatesTags: ['Comments', 'Orders', 'Items']
        }),
        addItemComment: build.mutation<void, CommentsAddData>({
            query: (data) => ({
                url: `comments/`,
                method: 'POST',
                body: data
            }),
            async onQueryStarted({ ...data }, { dispatch, queryFulfilled, getState }) {
                const { role, category, ...userDataToPatch } = (getState() as RootState)
                    ?.auth?.user as UsersData
                const queryKeyParams = store.getState().orders.currentQueryParams

                const dataToPatch: ItemComment = {
                    item: data.item,
                    text: data.text,
                    user: userDataToPatch,
                    id: Math.floor(Math.random() * 1000),
                    created_at: new Date().toISOString()
                }

                const patchResult = dispatch(
                    embs.util.updateQueryData(
                        'getItems',
                        queryKeyParams as EBMSItemsQueryParams,
                        (draft) => {
                            const item = draft.results.find(
                                (item) => item.id === data.item
                            )

                            if (item?.item) {
                                item?.item?.comments.push(dataToPatch)
                            } else {
                                const itemToPatch: Item = {
                                    id: Math.floor(Math.random() * 1000),
                                    origin_item: Math.floor(
                                        Math.random() * 1000
                                    ).toString(),
                                    flow: {
                                        id: '' as any,
                                        name: '',
                                        stages: []
                                    },
                                    time: '',
                                    comments: [dataToPatch],
                                    order: Math.floor(Math.random() * 1000),
                                    priority: 0,
                                    packages: 0,
                                    location: 0,
                                    production_date: '',
                                    stage: null
                                }

                                Object.assign(item!, {
                                    item: itemToPatch
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
            invalidatesTags: ['Comments', 'Orders', 'Items']
        }),
        patchComment: build.mutation<void, CommentsPatchData>({
            query: ({ data, id }) => ({
                url: `comments/${id}/`,
                method: 'PATCH',
                body: data
            }),
            invalidatesTags: ['Comments']
        }),
        removeComment: build.mutation<void, number>({
            query: (id) => ({
                url: `comments/${id}/`,
                method: 'DELETE'
            }),
            invalidatesTags: ['Comments']
        })
    })
})

export const {
    useGetCommentsQuery,
    useGetCommentQuery,
    useAddOrderCommentMutation,
    useAddItemCommentMutation,
    usePatchCommentMutation,
    useRemoveCommentMutation
} = comments
