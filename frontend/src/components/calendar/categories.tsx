import { Skeleton } from '@radix-ui/themes'

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useGetCategoriesQuery } from '@/store/api/ebms/ebms'

interface Props {
    onValueChange: (tab: string) => void
}

export const Categories: React.FC<Props> = ({ onValueChange }) => {
    const { data: categoriesData, isLoading } = useGetCategoriesQuery({})

    const filteredCategories = categoriesData?.results?.filter(
        (category) => category.prod_type == 'Rollforming' || category.prod_type === 'Trim'
    )
    return (
        <Tabs onValueChange={onValueChange} defaultValue={'Rollforming'}>
            {isLoading ? (
                <Skeleton className='w-40 h-10' />
            ) : (
                <TabsList className='bg-secondary'>
                    {filteredCategories?.map((tab) => (
                        <TabsTrigger
                            className='flex-1'
                            value={tab.prod_type}
                            key={tab.prod_type}>
                            {tab.prod_type}
                        </TabsTrigger>
                    ))}
                </TabsList>
            )}
        </Tabs>
    )
}
