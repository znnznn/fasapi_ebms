import { api } from '..'

import type {
    CapacitiesAddData,
    CapacitiesData,
    CapacitiesPatchData,
    CapacitiesResponse
} from './capacities.types'
import type { BaseQueryParams } from '@/types/api'
import { getQueryParamString } from '@/utils/get-query-param-string'

export const capacities = api.injectEndpoints({
    endpoints: (build) => ({
        getCapacities: build.query<CapacitiesResponse, BaseQueryParams>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `capacities/?${queryString}`
            },
            providesTags: ['Capacities']
        }),
        getCapacity: build.query<CapacitiesData, number>({
            query: (id) => `capacities/${id}`,
            providesTags: ['Capacities']
        }),
        addCapacity: build.mutation<void, CapacitiesAddData>({
            query: (data) => ({
                url: `capacities/`,
                method: 'POST',
                body: data
            }),
            invalidatesTags: ['Capacities', 'Flows', 'Categories', 'Calendar']
        }),
        patchCapacity: build.mutation<void, CapacitiesPatchData>({
            query: ({ data, id }) => ({
                url: `capacities/${id}/`,
                method: 'PATCH',
                body: data
            }),
            invalidatesTags: ['Capacities', 'Flows', 'Categories', 'Calendar']
        }),
        removeCapacity: build.mutation<void, number>({
            query: (id) => ({
                url: `capacities/${id}/`,
                method: 'DELETE'
            }),
            invalidatesTags: ['Capacities', 'Flows', 'Categories']
        })
    })
})

export const {
    useGetCapacitiesQuery,
    useGetCapacityQuery,
    useAddCapacityMutation,
    usePatchCapacityMutation,
    useRemoveCapacityMutation
} = capacities
