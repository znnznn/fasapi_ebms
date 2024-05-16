import {
    DndContext,
    type DragEndEvent,
    MouseSensor,
    TouchSensor,
    closestCenter,
    useSensor,
    useSensors
} from '@dnd-kit/core'
import {
    SortableContext,
    arrayMove,
    useSortable,
    verticalListSortingStrategy
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useEffect, useState } from 'react'

import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger
} from '../ui/accordion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'

import { FlowActions } from './flow-actions/flow-actions'
import { AddStatusDialog } from './status-actions/add-status-dialog'
import { StatusActions } from './status-actions/status-actions'
import type { FlowsData } from '@/store/api/flows/flows.types'
import { useGetStagesQuery, usePatchStageMutation } from '@/store/api/stages/stages'
import type { StagesData, StagesPatchData } from '@/store/api/stages/stages.types'

interface Props {
    flow: FlowsData
}

interface SortableCardProps {
    stage: StagesData
}

export const FlowAccordion: React.FC<Props> = ({ flow }) => {
    const [patchStage] = usePatchStageMutation()

    const { data } = useGetStagesQuery({ flow: flow.id })

    const currentStages = data?.results || []

    const [items, setItems] = useState<StagesData[]>(currentStages)

    useEffect(() => {
        setItems(currentStages)
    }, [currentStages])

    const handlePatchStage = async (data: StagesPatchData) => {
        try {
            await patchStage(data).unwrap()
        } catch (error) {}
    }

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event

        if (active.id !== over?.id) {
            setItems((items) => {
                const oldIndex = items.findIndex((item) => item.id === active.id)
                const newIndex = items.findIndex((item) => item.id === over?.id)

                return arrayMove(items, oldIndex, newIndex)
            })
        }

        const currentData = event.over?.data?.current!

        if (currentData.stageName !== 'Unscheduled' && currentData.stageName !== 'Done') {
            handlePatchStage({
                id: event.active.id as number,
                data: {
                    position: currentData.position as unknown as number,
                    flow: flow.id
                }
            })
        }
    }

    const sensors = useSensors(
        useSensor(MouseSensor, {
            activationConstraint: {
                distance: 12
            }
        }),
        useSensor(TouchSensor, {
            activationConstraint: {
                delay: 50,
                tolerance: 8
            }
        })
    )

    const doneStage = currentStages.find((stage) => stage.name === 'Done')
    const unscheduledStage = currentStages.find((stage) => stage.name === 'Unscheduled')

    return (
        <Accordion
            type='single'
            collapsible
            key={flow.id}
            className='w-full'>
            <AccordionItem
                className='border-none'
                value='item-1'>
                <Card>
                    <AccordionTrigger className='px-4'>
                        <CardHeader className='p-1 pr-4 flex flex-row items-center justify-between gap-x-4 w-full'>
                            <CardTitle className='text-lg'>{flow.name}</CardTitle>
                            <FlowActions
                                id={flow.id}
                                name={flow.name}
                            />
                        </CardHeader>
                    </AccordionTrigger>

                    <AccordionContent>
                        <CardContent className='flex flex-col gap-y-3'>
                            <AddStatusDialog
                                flowId={flow.id}
                                statuses={currentStages}
                            />

                            <Card>
                                <CardHeader>
                                    <CardTitle className='flex items-center justify-between gap-x-4'>
                                        <div className='flex items-center gap-x-2 text-lg'>
                                            <div
                                                style={{
                                                    backgroundColor:
                                                        unscheduledStage?.color
                                                }}
                                                className='w-5 h-5 rounded-md'></div>
                                            {unscheduledStage?.name}{' '}
                                        </div>
                                    </CardTitle>

                                    <CardDescription>
                                        {unscheduledStage?.description}
                                    </CardDescription>
                                </CardHeader>
                            </Card>

                            <DndContext
                                sensors={sensors}
                                collisionDetection={closestCenter}
                                onDragEnd={handleDragEnd}>
                                <SortableContext
                                    items={items}
                                    strategy={verticalListSortingStrategy}>
                                    {items.map((stage) =>
                                        stage.name !== 'Done' &&
                                        stage.name !== 'Unscheduled' ? (
                                            <SortableCard
                                                key={stage.id}
                                                stage={stage}
                                            />
                                        ) : null
                                    )}
                                </SortableContext>
                            </DndContext>

                            <Card>
                                <CardHeader>
                                    <CardTitle className='flex items-center justify-between gap-x-4'>
                                        <div className='flex items-center gap-x-2 text-lg'>
                                            <div
                                                style={{
                                                    backgroundColor: doneStage?.color
                                                }}
                                                className='w-5 h-5 rounded-md'></div>
                                            {doneStage?.name}
                                        </div>
                                    </CardTitle>

                                    <CardDescription>
                                        {doneStage?.description}
                                    </CardDescription>
                                </CardHeader>
                            </Card>
                        </CardContent>
                    </AccordionContent>
                </Card>
            </AccordionItem>
        </Accordion>
    )
}

const SortableCard: React.FC<SortableCardProps> = ({ stage }) => {
    const disabled = stage.name === 'Unscheduled' || stage.name === 'Done'

    const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
        id: stage.id,
        disabled,
        data: {
            position: stage.position,
            stageName: stage.name
        }
    })

    const style = {
        transform: CSS.Transform.toString(transform),
        transition
    }

    return (
        <Card
            ref={setNodeRef}
            style={style}
            {...attributes}
            {...listeners}>
            <CardHeader>
                <CardTitle className='flex items-center justify-between gap-x-4'>
                    <div className='flex items-center gap-x-2 text-lg'>
                        <div
                            style={{
                                backgroundColor: stage.color
                            }}
                            className='w-5 h-5 rounded-md'></div>
                        {stage.name}
                    </div>
                    {disabled ? null : (
                        <StatusActions
                            color={stage.color}
                            description={stage?.description!}
                            id={stage.id}
                            name={stage.name}
                        />
                    )}
                </CardTitle>

                <CardDescription>{stage.description}</CardDescription>
            </CardHeader>
        </Card>
    )
}
