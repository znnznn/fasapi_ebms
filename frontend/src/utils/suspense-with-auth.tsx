import { Suspense } from 'react'

import { PageLoader } from '@/components/ui/page-loader'
import { RequireAuthProvider } from '@/providers/require-auth-provider'

export const SuspenseWihAuth = (
    Component: React.LazyExoticComponent<any>,
    requireAuth = true
) => (
    <Suspense fallback={<PageLoader />}>
        {requireAuth ? (
            <RequireAuthProvider>
                <Component />
            </RequireAuthProvider>
        ) : (
            <Component />
        )}
    </Suspense>
)
