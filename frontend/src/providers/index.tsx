import { Theme } from '@radix-ui/themes'
import { type PropsWithChildren } from 'react'
import { Provider } from 'react-redux'

import { AuthProvider } from './auth-provider'
import { ThemeProvider } from './theme-provider'
import { store } from '@/store/index'

export const Providers: React.FC<PropsWithChildren> = ({ children }) => {
    return (
        <Provider store={store}>
            <AuthProvider>
                <Theme accentColor='green'>
                    <ThemeProvider defaultTheme='light' storageKey='vite-ui-theme'>
                        {children}
                    </ThemeProvider>
                </Theme>
            </AuthProvider>
        </Provider>
    )
}
