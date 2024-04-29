import { zodResolver } from '@hookform/resolvers/zod'
import { Edit2Icon, Loader2 } from 'lucide-react'
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
import { usePatchStageMutation } from '@/store/api/stages/stages'
import type { StagesPatchData } from '@/store/api/stages/stages.types'
import { stopPropagation } from '@/utils/stop-events'

interface Props {
    id: number
    name: string
    description: string
    color: string
}

type FormData = zodInfer<typeof stageSchema>

export const EditStatusDialog: React.FC<Props> = ({ id, name, description, color }) => {
    const form = useForm<FormData>({
        resolver: zodResolver(stageSchema),
        mode: 'onSubmit',
        shouldFocusError: true,
        values: {
            name,
            description: description || ''
        }
    })

    const [editStage, { isLoading }] = usePatchStageMutation()

    const handleEditStage = async (data: StagesPatchData) => {
        try {
            await editStage(data).unwrap()
            form.reset()
            setOpen(false)
        } catch (error) {}
    }

    const [colorValue, setColorValue] = useState(color)

    const onSubmit: SubmitHandler<FormData> = (formData) => {
        const dataToAdd = {
            ...formData,
            color: colorValue
        }

        handleEditStage({ id, data: dataToAdd })
    }

    const [open, setOpen] = useState(false)

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

    const onValueChange = (value: string) => setColorValue(value)

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button
                    onClick={stopPropagation}
                    className='justify-start'
                    variant='ghost'
                    size='sm'>
                    <Edit2Icon className='h-3.5 w-3.5 mr-1' />
                    Edit
                </Button>
            </DialogTrigger>
            <DialogContent className='rounded-md mx-2'>
                <DialogHeader className='text-left'>
                    <DialogTitle>Edit status</DialogTitle>
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
                        <Tabs onValueChange={onValueChange} defaultValue={color}>
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
                                'Edit'
                            )}
                        </Button>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
