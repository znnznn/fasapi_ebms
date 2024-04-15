import { api } from '..'

import type { CompanyProfileData, UsersProfileData } from './profiles.types'

export const users = api.injectEndpoints({
    endpoints: (build) => ({
        getCompanyProfiles: build.query<CompanyProfileData, void>({
            query: () => 'profiles/company/',
            providesTags: ['CompanyProfile']
        }),
        addCompanyProfiles: build.mutation<any, CompanyProfileData>({
            query: (data) => ({
                url: 'profiles/company/',
                method: 'POST',
                body: data
            }),
            invalidatesTags: ['CompanyProfile']
        }),
        getUsersProfiles: build.query<UsersProfileData[], void>({
            query: () => 'profiles/users/',

            providesTags: ['UsersProfile']
        }),
        addUsersProfiles: build.mutation<void, UsersProfileData>({
            query: (data) => ({
                url: 'profiles/users/',
                method: 'POST',
                body: data
            }),
            async onQueryStarted({ ...data }, { dispatch, queryFulfilled }) {
                const patchResult = dispatch(
                    users.util.updateQueryData('getUsersProfiles', undefined, (draft) => {
                        const currentPage = draft?.find(
                            (item) => item?.page === data?.page
                        )

                        if (currentPage) {
                            currentPage.show_columns = data.show_columns
                        } else {
                            draft?.push(data)
                        }
                    })
                )

                try {
                    await queryFulfilled
                } catch {
                    patchResult.undo()
                }
            },
            invalidatesTags: ['UsersProfile']
        }),
        removeUserProfiles: build.mutation<void, void>({
            query: () => ({
                url: 'profiles/users/',
                method: 'DELETE'
            }),
            invalidatesTags: ['UsersProfile']
        })
    })
})

export const {
    useGetCompanyProfilesQuery,
    useGetUsersProfilesQuery,
    useAddCompanyProfilesMutation,
    useAddUsersProfilesMutation,
    useRemoveUserProfilesMutation
} = users
