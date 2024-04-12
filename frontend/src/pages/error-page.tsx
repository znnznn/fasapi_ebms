import { Error } from '@/components/error'
import type { ErrorMessage } from '@/types/error'

const ErrorPage: React.FC<ErrorMessage> = ({ message = 'This page doest not found' }) => (
    <Error message={message} />
)

export default ErrorPage
