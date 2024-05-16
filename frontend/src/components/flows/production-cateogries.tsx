import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger
} from '../ui/accordion'
import { Badge } from '../ui/badge'

import { AddCapacityDialog } from './add-capacity-dialog'
import { FlowAccordion } from './flow-accordion'
import { AddFlowDialog } from './flow-actions/add-flow-dialog'
import { FlowsSkeleton } from './flows-skeleton'
import { useGetCategoriesQuery } from '@/store/api/ebms/ebms'
import { useGetAllFlowsQuery } from '@/store/api/flows/flows'
import { getValidValue } from '@/utils/get-valid-value'

export const ProductionCategories = () => {
    const { data, isLoading: isCategoriesLoading } = useGetCategoriesQuery({})
    const { data: flowsData, isLoading: isFlowsLoading } = useGetAllFlowsQuery({})

    const isLoading = isCategoriesLoading || isFlowsLoading
    return (
        <section className='px-3 max-w-[1000px] mx-auto mt-5'>
            <h1 className='text-2xl font-semibold'>EBMS Production Categories:</h1>

            {isLoading ? (
                <FlowsSkeleton />
            ) : (
                <Accordion
                    type='single'
                    collapsible
                    className='w-full'>
                    {data?.results?.map((category) => {
                        const currentFlows = flowsData?.filter(
                            (flow) => flow.category === category.id
                        )

                        const isCapacity =
                            category?.name === 'Trim' || category?.name === 'Rollforming'

                        return (
                            <AccordionItem
                                className='mt-4 border bg-card rounded-md'
                                value={category.name}
                                key={category.id}>
                                <AccordionTrigger className='min-h-20 px-4 items-center flex'>
                                    <div className='flex flex-col gap-y-2 items-start'>
                                        <div className='flex gap-x-2'>
                                            <span className='text-sm font-semibold'>
                                                {category.name}
                                            </span>
                                            <Badge variant='outline'>
                                                {category.flow_count} flows
                                            </Badge>
                                        </div>
                                        {isCapacity ? (
                                            <div className='flex gap-x-2'>
                                                <span className='text-sm'>
                                                    Daily Capacity:
                                                </span>
                                                <div className='flex items-center gap-x-1'>
                                                    <span className='text-sm font-bold'>
                                                        {getValidValue(
                                                            category?.capacity
                                                        )}
                                                    </span>
                                                    <AddCapacityDialog
                                                        capacityId={category?.capacity_id}
                                                        categoryId={category.id}
                                                        capacity={category?.capacity!}
                                                    />
                                                </div>
                                            </div>
                                        ) : (
                                            ''
                                        )}
                                    </div>
                                </AccordionTrigger>
                                <AccordionContent className='flex flex-col gap-y-3 px-4 pt-1'>
                                    <AccordionItem
                                        className='border-none'
                                        value='add-flow'>
                                        <AddFlowDialog categoryId={category.id} />
                                    </AccordionItem>
                                    {currentFlows?.map((flow) => (
                                        <FlowAccordion
                                            flow={flow}
                                            key={flow.id}
                                        />
                                    ))}
                                </AccordionContent>
                            </AccordionItem>
                        )
                    })}
                </Accordion>
            )}
        </section>
    )
}
