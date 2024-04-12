import ReactDOM from 'react-dom/client'

import { App } from '@/components/app'
import { Providers } from '@/providers'

ReactDOM.createRoot(document.getElementById('root')!).render(
    <Providers>
        <App />
    </Providers>
)
