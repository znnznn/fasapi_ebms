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

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { flowSchema } from '@/config/validation-schemas'
import { usePatchFlowMutation } from '@/store/api/flows/flows'
import type { FlowsPatchData } from '@/store/api/flows/flows.types'
import { stopPropagation } from '@/utils/stop-events'

interface Props {
    id: number
    name: string
}

type FormData = zodInfer<typeof flowSchema>

export const EditFlowDialog: React.FC<Props> = ({ id, name }) => {
    const form = useForm<FormData>({
        resolver: zodResolver(flowSchema),
        mode: 'onSubmit',
        shouldFocusError: true,
        values: {
            name
        }
    })

    const [patch, { isLoading }] = usePatchFlowMutation()

    const handlePatch = async (data: FlowsPatchData) => {
        try {
            await patch(data).unwrap()
            form.reset()
            setOpen(false)
        } catch (error) {
            error
        }
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => {
        handlePatch({ id, data: formData })
    }

    const [open, setOpen] = useState(false)

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
                    <DialogTitle>Edit flow</DialogTitle>
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
                                'Edit'
                            )}
                        </Button>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
