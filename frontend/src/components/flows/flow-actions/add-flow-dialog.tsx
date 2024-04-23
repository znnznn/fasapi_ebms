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

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { flowSchema } from '@/config/validation-schemas'
import { useAddFlowMutation } from '@/store/api/flows/flows'
import type { FlowsAddData } from '@/store/api/flows/flows.types'
import { stopPropagation } from '@/utils/stop-events'

interface Props {
    categoryId: number
}

type FormData = zodInfer<typeof flowSchema>

export const AddFlowDialog: React.FC<Props> = ({ categoryId }) => {
    const form = useForm<FormData>({
        resolver: zodResolver(flowSchema),
        mode: 'onSubmit',
        shouldFocusError: true
    })

    const [addFlow, { isLoading }] = useAddFlowMutation()

    const handleAddFlow = async (data: FlowsAddData) => {
        try {
            await addFlow(data).unwrap()
            form.reset()
            setOpen(false)
        } catch (error) {
            error
        }
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => {
        const dataToAdd = {
            ...formData,
            category: categoryId
        }

        handleAddFlow(dataToAdd)
    }

    const [open, setOpen] = useState(false)

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button
                    onClick={stopPropagation}
                    className='flex items-center gap-x-1.5 w-full'
                    size='lg'>
                    <PlusCircleIcon width='16px' />
                    Add Flow
                </Button>
            </DialogTrigger>
            <DialogContent className='rounded-md mx-2'>
                <DialogHeader className='text-left'>
                    <DialogTitle>Add flow</DialogTitle>
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
                                    <FormLabel>Flow name</FormLabel>
                                    <FormControl>
                                        <Input placeholder='flow' {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

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
