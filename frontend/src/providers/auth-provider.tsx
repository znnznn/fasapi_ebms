import { type PropsWithChildren } from 'react'

import { PageLoader } from '@/components/ui/page-loader'
import { useGetUserQuery } from '@/store/api/users/users'
import type { UserId } from '@/types/api'

export const AuthProvider: React.FC<PropsWithChildren> = ({ children }) => {
    const userId =
        (JSON.parse(localStorage.getItem('id') || 'null') as UserId)?.id ??
        (JSON.parse(sessionStorage.getItem('id') || 'null') as UserId)?.id

    const { isLoading } = useGetUserQuery(userId)

    if (isLoading) {
        return <PageLoader />
    }

    return children
}
