import { createSlice } from '@reduxjs/toolkit'

import { api } from '@/store/api'
import type { LoginResponse } from '@/types/auth'

interface IAuthState extends LoginResponse {
    isAuth: boolean
}

const initialState: IAuthState = {
    user: null,
    access: null,
    refresh: null,
    isAuth: false
}

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logout: () => {
            localStorage.clear()
            sessionStorage.clear()
            return initialState
        },
        tokenUpdated: (state, action) => {
            if (state.user) {
                state.access = action.payload.access
            }
        }
    },
    extraReducers: (build) => {
        build
            .addMatcher(api.endpoints.login.matchFulfilled, (state, action) => {
                const { access, user } = action.payload
                state.access = access
                state.user = user
                state.isAuth = true
            })
            .addMatcher(api.endpoints.getUser.matchFulfilled, (state, action) => {
                state.isAuth = true
                state.user = action.payload
            })
    }
})

export const { logout, tokenUpdated } = authSlice.actions
export const authReducer = authSlice.reducer
export const selectUser = (state: { auth: IAuthState }) => state?.auth?.user
