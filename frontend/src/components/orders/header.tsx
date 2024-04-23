import { UserMenu } from '../user-menu'

import { Filters } from './filters'
import { WeekFilters } from './items-table/week-filters'
import { Nav } from './nav'
import { SideBar } from '@/components/sidebar'

export const Header = () => {
    // const onValueChange = (tab: string) => dispatch(setOrderCompleted(Boolean(tab)))

    return (
        <header className='relative'>
            <div className='flex items-center h-20 justify-between gap-6'>
                <div className='flex items-center gap-x-6 py-5'>
                    <div className='flex items-center gap-x-2'>
                        <SideBar />
                    </div>
                    {/* <Tabs
                        onValueChange={onValueChange}
                        defaultValue=''
                        className='w-[400px]'>
                        <TabsList className='bg-secondary h-[43px]'>
                            <TabsTrigger value=''>All Orders</TabsTrigger>
                            <TabsTrigger value='completed'>Completed orders</TabsTrigger>
                        </TabsList>
                    </Tabs> */}
                    <Nav />
                </div>
                <UserMenu />
            </div>
            <div className='flex flex-wrap items-center justify-between gap-4 mb-3'>
                <Filters />
                <WeekFilters />
            </div>
        </header>
    )
}
