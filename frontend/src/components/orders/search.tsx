import { useEffect, useState } from 'react'

import { setSearch } from './store/orders'
import { Input } from '@/components/ui/input'
import { useDebounce } from '@/hooks/use-debounce'
import { useAppDispatch } from '@/store/hooks/hooks'
import type { InputEvent } from '@/types/common'

export const Search: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('')
    const debouncedSearchTerm = useDebounce(searchTerm)

    const dispatch = useAppDispatch()

    useEffect(() => {
        dispatch(setSearch(debouncedSearchTerm))
    }, [debouncedSearchTerm, dispatch])

    useEffect(() => {
        return () => {
            dispatch(setSearch(''))
        }
    }, [dispatch])

    const handleSearch = (e: InputEvent) => setSearchTerm(e.target.value)

    return (
        <Input
            onChange={handleSearch}
            className='h-10 min-w-48 max-w-48 max-sm:min-w-full max-sm:max-w-ful'
            placeholder='Search...'
        />
    )
}
