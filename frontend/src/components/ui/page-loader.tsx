import { Loader2 } from 'lucide-react'

export const PageLoader = () => (
    <div className='fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2  text-primary'>
        <Loader2 className='animate-spin h-10 w-10' />
    </div>
)
