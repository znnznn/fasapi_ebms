import { UserMenu } from '../user-menu'

import { Nav } from './nav'
import { SideBar } from '@/components/sidebar'

export const Header = () => {
    // const onValueChange = (tab: string) => dispatch(setOrderCompleted(Boolean(tab)))

    return (
        <header className='relative'>
            <div className='flex items-center h-20 justify-between gap-6'>
                <div className='flex items-center gap-x-7 py-5'>
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
        </header>
    )
}