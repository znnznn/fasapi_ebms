import { RouterProvider, createBrowserRouter } from 'react-router-dom'

import '@/assets/styles/global.css'
import { Layout } from '@/components/layout'
import { routes } from '@/config/routes'
import CalendarPage from '@/pages/calendar-page'
import CompanySettingsPage from '@/pages/company-settings'
import ErrorPage from '@/pages/error-page'
import FlowsPage from '@/pages/flows-page'
import LoginPage from '@/pages/login-page'
import OrdersPage from '@/pages/orders-page'
import PasswordResetConfirmPage from '@/pages/password-reset-confirm-page'
import UserSettingsPage from '@/pages/user-settings-page'
import UsersPage from '@/pages/users-page'
import { SuspenseWihAuth } from '@/utils/suspense-with-auth'

import '@radix-ui/themes/styles.css'

// const LoginPage = lazy(() => import('@/pages/login-page'))
// const ErrorPage = lazy(() => import('@/pages/error-page'))
// const OrdersPage = lazy(() => import('@/pages/orders-page'))
// const FlowsPage = lazy(() => import('@/pages/flows-page'))
// const UserSettingsPage = lazy(() => import('@/pages/user-settings-page'))
// const CompanySettingsPage = lazy(() => import('@/pages/company-settings'))
// const PasswordResetConfirmPage = lazy(() => import('@/pages/password-reset-confirm-page'))
// const UsersPage = lazy(() => import('@/pages/users-page'))
// const CalendarPage = lazy(() => import('@/pages/calendar-page'))

const router = createBrowserRouter([
    {
        path: routes.home,
        element: <Layout />,
        errorElement: <ErrorPage />,
        children: [
            {
                path: routes.login,
                element: SuspenseWihAuth(LoginPage, false)
            },
            {
                index: true,
                element: SuspenseWihAuth(OrdersPage)
            },

            {
                path: routes.flows,
                element: SuspenseWihAuth(FlowsPage)
            },
            {
                path: routes.userSettings,
                element: SuspenseWihAuth(UserSettingsPage)
            },
            {
                path: routes.companySettings,
                element: SuspenseWihAuth(CompanySettingsPage)
            },
            {
                path: routes.passwordResetConfirm,
                element: SuspenseWihAuth(PasswordResetConfirmPage)
            },
            {
                path: routes.users,
                element: SuspenseWihAuth(UsersPage)
            },
            {
                path: routes.calendar,
                element: SuspenseWihAuth(CalendarPage)
            }
        ]
    },
    {
        path: '*',
        element: SuspenseWihAuth(ErrorPage, false)
    }
])

export const App = () => <RouterProvider router={router} />
