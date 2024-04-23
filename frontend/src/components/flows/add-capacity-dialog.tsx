import { zodResolver } from '@hookform/resolvers/zod'
import { Edit2Icon, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { type SubmitHandler, useForm } from 'react-hook-form'
import type { infer as zodInfer } from 'zod'

import { Button } from '../ui/button'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from '../ui/form'

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { capacitySchema } from '@/config/validation-schemas'
import {
    useAddCapacityMutation,
    usePatchCapacityMutation
} from '@/store/api/capacities/capacities'
import type {
    CapacitiesAddData,
    CapacitiesPatchData
} from '@/store/api/capacities/capacities.types'
import { stopPropagation } from '@/utils/stop-events'

interface Props {
    categoryId: number
    capacityId: number | null
    capacity: number
}

type FormData = zodInfer<typeof capacitySchema>

export const AddCapacityDialog: React.FC<Props> = ({
    categoryId,
    capacity,
    capacityId
}) => {
    const form = useForm<FormData>({
        resolver: zodResolver(capacitySchema),
        mode: 'onSubmit',
        shouldFocusError: true,
        values: {
            per_day: String(capacity ?? '')
        }
    })

    const [addCapacity, { isLoading }] = useAddCapacityMutation()
    const [patchCapacity, { isLoading: isPatching }] = usePatchCapacityMutation()

    const handleAddCapacity = async (data: CapacitiesAddData) => {
        try {
            await addCapacity(data).unwrap()
            form.reset()
            setOpen(false)
        } catch (error) {
            error
        }
    }

    const handlePatchCapacity = async (data: CapacitiesPatchData) => {
        try {
            await patchCapacity(data).unwrap()
            form.reset()
            setOpen(false)
        } catch (error) {
            error
        }
    }

    // const handleRemoveCapacity = async (id: number) => {
    //     try {
    //         await removeCapacity(id).unwrap()
    //         setOpen(false)
    //     } catch (error) {
    //         error
    //     }
    // }

    // const onRemove = () => (capacityId ? handleRemoveCapacity(capacityId) : () => null)

    const onSubmit: SubmitHandler<FormData> = (formData) => {
        const dataToAdd = {
            per_day: +formData.per_day,
            category: categoryId
        }

        if (capacityId) {
            handlePatchCapacity({ id: capacityId, data: { per_day: +formData.per_day } })
        } else {
            handleAddCapacity(dataToAdd)
        }
    }

    const [open, setOpen] = useState(false)

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button
                    onClick={stopPropagation}
                    className='w-5 h-5'
                    size='icon'
                    variant='ghost'>
                    <Edit2Icon width='12px' />
                </Button>
            </DialogTrigger>
            <DialogContent className='rounded-md mx-2'>
                <DialogHeader className='text-left'>
                    <DialogTitle>Сapacity</DialogTitle>
                </DialogHeader>
                <Form {...form}>
                    <form
                        method='POST'
                        className='w-full mx-auto space-y-5'
                        onSubmit={form.handleSubmit(onSubmit)}>
                        <FormField
                            control={form.control}
                            name='per_day'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Per day</FormLabel>
                                    <FormControl>
                                        <Input placeholder='500' {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <div className='flex items-center gap-x-3'>
                            {/* <Button
                                onClick={onRemove}
                                className='w-full'
                                variant='destructive'
                                type='button'>
                                {isRemoving ? (
                                    <Loader2 className='h-4 w-4 animate-spin' />
                                ) : (
                                    'Remove'
                                )}
                            </Button> */}
                            <Button className='w-full' type='submit'>
                                {isLoading || isPatching ? (
                                    <Loader2 className='h-4 w-4 animate-spin' />
                                ) : capacityId ? (
                                    'Save'
                                ) : (
                                    'Add'
                                )}
                            </Button>
                        </div>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
