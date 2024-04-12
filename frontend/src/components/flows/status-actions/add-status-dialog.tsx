import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2, PlusCircleIcon } from 'lucide-react'
import { useState } from 'react'
import { type SubmitHandler, useForm } from 'react-hook-form'
import type { infer as zodInfer } from 'zod'

import { Button } from '../../ui/button'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from '../../ui/form'
import { Tabs, TabsList, TabsTrigger } from '../../ui/tabs'
import { Textarea } from '../../ui/textarea'

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { stageSchema } from '@/config/validation-schemas'
import { useAddStageMutation } from '@/store/api/stages/stages'
import type { StagesAddData, StagesData } from '@/store/api/stages/stages.types'
import { stopPropagation } from '@/utils/stop-events'

interface Props {
    flowId: number
    statuses: StagesData[]
}

type FormData = zodInfer<typeof stageSchema>

export const AddStatusDialog: React.FC<Props> = ({ flowId }) => {
    const form = useForm<FormData>({
        resolver: zodResolver(stageSchema),
        mode: 'onSubmit',
        shouldFocusError: true
    })

    const [addStage, { isLoading }] = useAddStageMutation()

    const handleAddStage = async (data: StagesAddData) => {
        try {
            await addStage(data).unwrap()
            form.reset()
            setOpen(false)
        } catch (error) {
            error
        }
    }

    const colorPresets = [
        '#0090FF',
        '#09D8B5',
        '#222222',
        '#FFCA14',
        '#EF5E01',
        '#3E9B4F',
        '#CA244C',
        '#8145B5',
        '#CE2C31'
    ]

    const defaultColor = colorPresets[0]

    const [color, setColor] = useState(defaultColor)

    const onSubmit: SubmitHandler<FormData> = (formData) => {
        const dataToAdd = {
            ...formData,
            color,
            flow: flowId
        }

        handleAddStage(dataToAdd)
    }

    const [open, setOpen] = useState(false)

    const onValueChange = (value: string) => {
        setColor(value)
    }
    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button
                    onClick={stopPropagation}
                    className='flex items-center gap-x-1.5 w-full mt-1'
                    variant='outline'
                    size='lg'>
                    <PlusCircleIcon width='16px' />
                    Add Status
                </Button>
            </DialogTrigger>
            <DialogContent className='rounded-md mx-2'>
                <DialogHeader className='text-left'>
                    <DialogTitle>Add status</DialogTitle>
                </DialogHeader>
                <Form {...form}>
                    <form
                        method='POST'
                        className='w-full mx-auto space-y-5'
                        onSubmit={form.handleSubmit(onSubmit)}>
                        <FormField
                            control={form.control}
                            name='name'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Stage name</FormLabel>
                                    <FormControl>
                                        <Input placeholder='done' {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name='description'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Stage description</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            className='resize-none'
                                            placeholder='Enter status description'
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <Tabs onValueChange={onValueChange} defaultValue={defaultColor}>
                            <TabsList className='gap-x-2 bg-transparent p-0'>
                                {colorPresets.map((color) => (
                                    <TabsTrigger
                                        key={color}
                                        value={color}
                                        className='data-[state=active]:outline data-[state=active]:outline-offset-2 w-6 h-6 rounded-sm'
                                        style={{ backgroundColor: color }}
                                    />
                                ))}
                            </TabsList>
                        </Tabs>

                        <Button
                            onClick={stopPropagation}
                            className='w-full'
                            type='submit'>
                            {isLoading ? (
                                <Loader2 className='h-4 w-4 animate-spin' />
                            ) : (
                                'Add'
                            )}
                        </Button>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
