import { Skeleton } from '@radix-ui/themes'

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useGetCategoriesQuery } from '@/store/api/ebms/ebms'

interface Props {
    onValueChange: (tab: string) => void
}

export const Categories: React.FC<Props> = ({ onValueChange }) => {
    const { data: categoriesData, isLoading } = useGetCategoriesQuery({})

    const filteredCategories = categoriesData?.results?.filter(
        (category) => category.name == 'Rollforming' || category.name === 'Trim'
    )

    return (
        <Tabs onValueChange={onValueChange} defaultValue={'Rollforming'}>
            {isLoading ? (
                <Skeleton className='w-40 h-10' />
            ) : (
                <TabsList className='bg-secondary'>
                    {filteredCategories?.map((tab) => (
                        <TabsTrigger className='flex-1' value={tab.name} key={tab.name}>
                            {tab.name}
                        </TabsTrigger>
                    ))}
                </TabsList>
            )}
        </Tabs>
    )
}
