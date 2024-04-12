import { zodResolver } from '@hookform/resolvers/zod'
import { Edit, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { type SubmitHandler, useForm } from 'react-hook-form'
import { toast } from 'sonner'
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
import { Input } from '../ui/input'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger
} from '@/components/ui/collapsible'
import { userPatchSchema } from '@/config/validation-schemas'
import { usePatchUserMutation } from '@/store/api/users/users'
import { useAppSelector } from '@/store/hooks/hooks'
import { selectUser } from '@/store/slices/auth'
import { isErrorWithMessage } from '@/utils/is-error-with-message'
import { stopPropagation } from '@/utils/stop-events'

type FormData = zodInfer<typeof userPatchSchema>

export const UserSettingsForms = () => {
    const { id: userId, email, first_name, last_name } = useAppSelector(selectUser)!

    const form = useForm<FormData>({
        resolver: zodResolver(userPatchSchema),
        mode: 'onSubmit',
        shouldFocusError: true,
        values: {
            email,
            first_name,
            last_name
        }
    })

    const successToast = () =>
        toast.success(`User Settings`, {
            description: 'Data changed successfully'
        })

    const errorToast = (description: string) =>
        toast.error('Something went wrong', { description })

    const [patchUser, { isLoading }] = usePatchUserMutation()

    const handlePatchUser = async (data: FormData) => {
        try {
            await patchUser({ id: userId!, data }).unwrap().then(successToast)
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            if (isErrorMessage) {
                errorToast(error.data.wrong_old_password)
            }
        }
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => handlePatchUser(formData)

    const [open, setOpen] = useState(false)

    return (
        <Collapsible open={open} onOpenChange={setOpen} className='flex-1 min-w-80'>
            <Card className='h-[430px]'>
                <CardHeader>
                    <CardTitle className='flex items-center justify-between gap-x-4'>
                        User info
                        <CollapsibleTrigger asChild>
                            <Edit className='h-4 w-4 cursor-pointer' />
                        </CollapsibleTrigger>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <Form {...form}>
                        <form
                            method='POST'
                            className='w-full mx-auto mt-4 space-y-5'
                            onSubmit={form.handleSubmit(onSubmit)}>
                            <FormField
                                disabled={!open}
                                control={form.control}
                                name='email'
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Email</FormLabel>
                                        <FormControl>
                                            <Input
                                                type='email'
                                                placeholder='nickname@gmail.com'
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                disabled={!open}
                                control={form.control}
                                name='first_name'
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>First name</FormLabel>
                                        <FormControl>
                                            <Input placeholder='John' {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                disabled={!open}
                                control={form.control}
                                name='last_name'
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Last name</FormLabel>
                                        <FormControl>
                                            <Input placeholder='Doe' {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <CollapsibleContent>
                                <Button
                                    onClick={stopPropagation}
                                    className='w-full'
                                    type='submit'>
                                    {isLoading ? (
                                        <Loader2 className='h-4 w-4 animate-spin' />
                                    ) : (
                                        'Save'
                                    )}
                                </Button>
                            </CollapsibleContent>
                        </form>
                    </Form>
                </CardContent>
            </Card>
        </Collapsible>
    )
}
