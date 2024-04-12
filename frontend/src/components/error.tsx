import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import type { ErrorMessage } from '@/types/error'

export const Error: React.FC<ErrorMessage> = ({ message }) => {
    const navigate = useNavigate()
    const onClick = () => navigate('/')

    return (
        <div className='min-h-[100vh] flex items-center justify-center'>
            <div className='flex flex-col items-center gap-y-5'>
                <h1 className='text-5xl text-center'>{message}</h1>
                <Button onClick={onClick}>Go to homepage</Button>
            </div>
        </div>
    )
}
