import { api } from '..'

import type {
    StagesAddData,
    StagesData,
    StagesPatchData,
    StagesQueryParams,
    StagesResponse
} from './stages.types'
import type { BaseQueryParams } from '@/types/api'
import { getQueryParamString } from '@/utils/get-query-param-string'

export const stage = api.injectEndpoints({
    endpoints: (build) => ({
        getStages: build.query<StagesResponse, Partial<StagesQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `stages/?${queryString}`
            },
            providesTags: ['Stage']
        }),
        getAllStages: build.query<StagesData[], Partial<BaseQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `stages/all/?${queryString}`
            },
            providesTags: ['Stage']
        }),
        getStage: build.query<StagesData, number>({
            query: (id) => `stages/${id}/`,
            providesTags: ['Stage']
        }),
        addStage: build.mutation<void, StagesAddData>({
            query: (data) => ({
                url: `stages/`,
                method: 'POST',
                body: data
            }),
            invalidatesTags: ['Stage']
        }),
        patchStage: build.mutation<void, StagesPatchData>({
            query: ({ data, id }) => ({
                url: `stages/${id}/`,
                method: 'PATCH',
                body: data
            }),
            invalidatesTags: ['Stage']
        }),
        removeStage: build.mutation<void, number>({
            query: (id) => ({
                url: `stages/${id}/`,
                method: 'DELETE'
            }),
            invalidatesTags: ['Stage']
        })
    })
})

export const {
    useGetStagesQuery,
    useGetStageQuery,
    useGetAllStagesQuery,
    useAddStageMutation,
    usePatchStageMutation,
    useRemoveStageMutation
} = stage
