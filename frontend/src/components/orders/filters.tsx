import { X } from 'lucide-react'
import { useEffect, useState } from 'react'

import { Badge } from '../ui/badge'
import { Button } from '../ui/button'

import { selectOrders, setDate, setOrderCompleted, setOverDue } from './store/orders'
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'

export const Filters = () => {
    const [filters, setFilters] = useState<string[]>()

    const date = useAppSelector(selectOrders).date

    const dispatch = useAppDispatch()

    const [overdue, setOverdue] = useState(false)
    const [done, setDone] = useState(false)

    useEffect(() => {
        const newFilters = []

        if (overdue) {
            newFilters.push('overdue')
            dispatch(setOverDue(true))
            dispatch(setDate(''))
        } else {
            dispatch(setOverDue(false))
        }

        if (done) {
            newFilters.push('completed')
            dispatch(setOrderCompleted(true))
        } else {
            dispatch(setOrderCompleted(false))
        }

        setFilters(newFilters)
    }, [overdue, done])

    useEffect(() => {
        setFilters((prev) => {
            if (date) {
                return prev?.filter((f) => f !== 'overdue')
            }
            return prev
        })

        if (date) {
            setOverdue(false)
        }
    }, [date])

    const removeFilter = (filter: string) => {
        setFilters((prev) => prev?.filter((f) => f !== filter))

        if (filter === 'overdue') setOverdue(false)
        if (filter === 'completed') setDone(false)
    }

    return (
        <div className='flex gap-5 items-center'>
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button
                        className='h-[45px]'
                        variant='outline'>
                        Filters
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align='end'>
                    <DropdownMenuCheckboxItem
                        checked={overdue}
                        onCheckedChange={setOverdue}>
                        Overdue
                    </DropdownMenuCheckboxItem>
                    <DropdownMenuCheckboxItem
                        checked={done}
                        onCheckedChange={setDone}>
                        Completed
                    </DropdownMenuCheckboxItem>
                </DropdownMenuContent>
            </DropdownMenu>

            <div className='flex items-center gap-2'>
                {filters?.map((filter) => (
                    <Badge
                        variant='outline'
                        className='capitalize cursor-pointer hover:border-destructive hover:text-destructive'
                        key={filter}
                        onClick={() => {
                            removeFilter(filter)
                        }}>
                        {filter}
                        <X className='ml-1 h-3 w-3 font-bold' />
                    </Badge>
                ))}
            </div>
        </div>
    )
}
