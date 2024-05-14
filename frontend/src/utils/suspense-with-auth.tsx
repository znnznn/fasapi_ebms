import { RequireAuthProvider } from '@/providers/require-auth-provider'

export const SuspenseWihAuth = (
    // Component: React.LazyExoticComponent<any>,
    Component: React.FC,
    requireAuth = true
) =>
    // <Suspense fallback={<PageLoader />}>
    requireAuth ? (
        <RequireAuthProvider>
            <Component />
        </RequireAuthProvider>
    ) : (
        <Component />
    )
// </Suspense>
