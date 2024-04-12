import type { UsersData } from '@/store/api/users/users.types'

export interface LoginData {
    email: string
    password: string
}

export interface LoginResponse {
    refresh: string | null
    access: string | null
    user: UsersData | null
}

export interface RefreshResponse {
    data: AccessToken
}

export interface AccessToken {
    access: string
}

export interface RefreshToken {
    refresh: string
}
