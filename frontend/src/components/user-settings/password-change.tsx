import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2 } from 'lucide-react'
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
import { changePasswordSchema } from '@/config/validation-schemas'
import { useChangePasswordMutation } from '@/store/api/passwords/passwords'
import { useAppSelector } from '@/store/hooks/hooks'
import { selectUser } from '@/store/slices/auth'
import { isErrorWithMessage } from '@/utils/is-error-with-message'
import { stopPropagation } from '@/utils/stop-events'

type FormData = zodInfer<typeof changePasswordSchema>

export const PasswordChange = () => {
    const form = useForm<FormData>({
        resolver: zodResolver(changePasswordSchema),
        mode: 'onSubmit',
        shouldFocusError: true
    })

    const userId = useAppSelector(selectUser)?.id

    const successToast = () =>
        toast.success(`Password changed`, {
            description: 'Password changed successfully'
        })

    const errorToast = (description: string) =>
        toast.error('Something went wrong', { description })

    const [changePassword, { isLoading }] = useChangePasswordMutation()

    const reset = () => {
        form.setValue('old_password', '')
        form.setValue('new_password1', '')
        form.setValue('new_password2', '')
    }

    const handleChangePassword = async (data: FormData) => {
        try {
            await changePassword({ id: userId!, data })
                .unwrap()
                .then(() => successToast())
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            if (isErrorMessage) {
                errorToast(error.data.wrong_old_password)
            }
        }
        reset()
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => handleChangePassword(formData)

    return (
        <Card className='flex-1 min-w-80'>
            <CardHeader>
                <CardTitle> Change password</CardTitle>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form
                        method='POST'
                        className='w-full mx-auto mt-4 space-y-5'
                        onSubmit={form.handleSubmit(onSubmit)}>
                        <FormField
                            control={form.control}
                            name='old_password'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Old password</FormLabel>
                                    <FormControl>
                                        <Input
                                            type='password'
                                            placeholder='Old password'
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name='new_password1'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>New password</FormLabel>
                                    <FormControl>
                                        <Input
                                            type='password'
                                            placeholder='New password'
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name='new_password2'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Confirm password</FormLabel>
                                    <FormControl>
                                        <Input
                                            type='password'
                                            placeholder='Confirm password'
                                            {...field}
                                        />
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
                                'Save'
                            )}
                        </Button>
                    </form>
                </Form>
            </CardContent>
        </Card>
    )
}
