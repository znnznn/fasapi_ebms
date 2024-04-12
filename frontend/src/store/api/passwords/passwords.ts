import { api } from '..'

import type {
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    PasswordResetResponse
} from './passwords.types'

export const users = api.injectEndpoints({
    endpoints: (build) => ({
        passwordReset: build.mutation<PasswordResetResponse, PasswordReset>({
            query: (data) => ({
                url: `users/password-reset/`,
                method: 'POST',
                body: data
            })
        }),
        passwordResetConfirm: build.mutation<void, PasswordResetConfirm>({
            query: (data) => ({
                url: `users/password-reset-confirm/${data.uidb64}/${data.token}/`,
                method: 'POST',
                body: data
            })
        }),
        changePassword: build.mutation<void, PasswordChange>({
            query: ({ data, id }) => ({
                url: `users/${id}/password-change/`,
                method: 'POST',
                body: data
            })
        })
    })
})

export const {
    usePasswordResetConfirmMutation,
    usePasswordResetMutation,
    useChangePasswordMutation
} = users
