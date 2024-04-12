import { useEffect } from 'react'

import { selectOrders, setCategory, setCurrentCapacity } from './store/orders'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useGetAllCategoriesQuery } from '@/store/api/ebms/ebms'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'

export const Nav = () => {
    const dispatch = useAppDispatch()
    const category = useAppSelector(selectOrders).category

    const { data, isLoading } = useGetAllCategoriesQuery()

    const onValueChange = (tab: string) => dispatch(setCategory(tab))

    const tabs = data?.map((category) => category.name)
    tabs?.unshift('All')

    useEffect(() => {
        const currentCategory = data?.find(
            (dataCategory) => dataCategory.name === category
        )

        const { capacity, total_capacity } = currentCategory || {
            capacity: 0,
            total_capacity: 0
        }

        dispatch(setCurrentCapacity({ capacity, total_capacity }))
    }, [data, category])

    const defaultTab = category ? category : 'All'

    return (
        <div className='flex items-start flex-wrap justify-between gap-x-6'>
            <Tabs
                onValueChange={onValueChange}
                defaultValue={defaultTab}
                className='w-fit py-3'>
                {isLoading ? (
                    <Skeleton className='w-[427px] h-10' />
                ) : (
                    <TabsList className='bg-secondary h-[43px]'>
                        {tabs?.map((tab) => (
                            <TabsTrigger value={tab} key={tab}>
                                {tab}
                            </TabsTrigger>
                        ))}
                    </TabsList>
                )}
            </Tabs>
        </div>
    )
}
