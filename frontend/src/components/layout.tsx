import { lazy } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { Outlet } from 'react-router-dom'

import { Toaster } from './ui/sonner'
import { Head } from '@/components/head'

const ErrorPage = lazy(() => import('@/pages/error-page'))

export const Layout = () => (
    <>
        <Head />
        <main className='px-3'>
            <ErrorBoundary fallback={<ErrorPage message='Something went wrong' />}>
                <Outlet />
            </ErrorBoundary>
        </main>
        <Toaster richColors duration={5000} />
    </>
)
