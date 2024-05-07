import type { Table } from '@tanstack/react-table'

import { Pagination } from './pagination'
import { Search } from './search'
import { selectCategory, setScheduled } from './store/orders'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'

interface Props<TData> {
    table: Table<TData>
    page: 'orders' | 'items'
}
export function Statuses<TData>({ table, page }: Props<TData>) {
    const dispatch = useAppDispatch()
    const onValueChange = (tab: string) => dispatch(setScheduled(Boolean(tab)))

    const category = useAppSelector(selectCategory)
    const scheduled = useAppSelector((state) => state.orders.scheduled)

    const defaultValue = scheduled ? 'scheduled' : ''

    return (
        <div className='flex items-start justify-between flex-wrap gap-5 w-full py-2 border-t border-t-input'>
            <div className='flex items-center flex-wrap justify-between gap-6 max-sm:w-full'>
                <Tabs
                    key={category}
                    onValueChange={onValueChange}
                    defaultValue={defaultValue}>
                    <TabsList className='bg-secondary'>
                        <TabsTrigger value=''>Unscheduled</TabsTrigger>
                        <TabsTrigger value='scheduled'>Scheduled</TabsTrigger>
                    </TabsList>
                </Tabs>
                <Search table={table} />
            </div>

            <Pagination
                table={table}
                page={page}
            />
        </div>
    )
}
