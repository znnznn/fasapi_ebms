import { api } from '..'

import type {
    UserAllQueryParams,
    UsersAddData,
    UsersData,
    UsersPatchData,
    UsersResponse
} from './users.types'
import type { BaseQueryParams } from '@/types/api'
import { getQueryParamString } from '@/utils/get-query-param-string'

export const users = api.injectEndpoints({
    endpoints: (build) => ({
        getUsers: build.query<UsersResponse, Partial<BaseQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `users/?${queryString}`
            },
            providesTags: ['Users']
        }),
        getAllUsers: build.query<UsersData[], Partial<UserAllQueryParams>>({
            query: (params) => {
                const queryString = getQueryParamString(params)
                return `users/all/?${queryString}`
            },
            providesTags: ['Users']
        }),
        getUser: build.query<UsersData, number>({
            query: (id) => `users/${id}/`,
            providesTags: ['Users']
        }),
        addUser: build.mutation<void, UsersAddData>({
            query: (data) => ({
                url: `users/`,
                method: 'POST',
                body: data
            }),
            invalidatesTags: ['Users']
        }),
        patchUser: build.mutation<void, UsersPatchData>({
            query: ({ data, id }) => ({
                url: `users/${id}/`,
                method: 'PATCH',
                body: data
            }),
            invalidatesTags: ['Users']
        }),
        removeUser: build.mutation<void, number>({
            query: (id) => ({
                url: `users/${id}/`,
                method: 'DELETE'
            }),
            invalidatesTags: ['Users']
        })
    })
})

export const {
    useGetUsersQuery,
    useGetAllUsersQuery,
    useGetUserQuery,
    useAddUserMutation,
    usePatchUserMutation,
    useRemoveUserMutation
} = users
