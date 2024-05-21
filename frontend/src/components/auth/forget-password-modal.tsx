import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { type SubmitHandler, useForm } from 'react-hook-form'
import { toast } from 'sonner'
import type { infer as zodInfer } from 'zod'

import { Button } from '../ui/button'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from '../ui/dialog'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from '../ui/form'
import { Input } from '../ui/input'

import { emailSchema } from '@/config/validation-schemas'
import { usePasswordResetMutation } from '@/store/api/passwords/passwords'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

type FormData = zodInfer<typeof emailSchema>

interface ForgetPasswordModalProps {
    disabled: boolean
}

export const ForgetPasswordModal: React.FC<ForgetPasswordModalProps> = ({ disabled }) => {
    const [open, setOpen] = useState(false)
    const handleClose = () => setOpen(false)

    const form = useForm<FormData>({
        resolver: zodResolver(emailSchema),
        mode: 'onSubmit',
        shouldFocusError: true
    })

    const [passwordReset, { isLoading }] = usePasswordResetMutation()

    const successToast = (message: string) =>
        toast.success('Password reset', {
            description: message
        })

    const errorToast = (message: string) =>
        toast.error('Password reset', {
            description: message
        })

    const handlePasswordReset = async (data: FormData) => {
        try {
            await passwordReset(data)
                .unwrap()
                .then((response) => successToast(response.message))

            form.setValue('email', '')
            handleClose()
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)
            errorToast(isErrorMessage ? error.data.detail : 'Something went wrong')
        }
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => handlePasswordReset(formData)

    return (
        <Dialog
            open={open}
            onOpenChange={setOpen}>
            <DialogTrigger
                disabled={disabled}
                className='text-sm text-neutral-400 hover:text-neutral-600 transition-colors'>
                Forgot password?
            </DialogTrigger>
            <DialogContent className='rounded-md mx-2'>
                <DialogHeader className='text-left'>
                    <DialogTitle>Password reset</DialogTitle>
                </DialogHeader>
                <Form {...form}>
                    <form
                        className='w-full mx-auto space-y-5'
                        onSubmit={form.handleSubmit(onSubmit)}>
                        <FormField
                            control={form.control}
                            name='email'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Email</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder='nickname@gmail.com'
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <Button
                            className='w-full'
                            type='submit'>
                            {isLoading ? (
                                <Loader2 className='h-4 w-4 animate-spin' />
                            ) : (
                                'Send reset link'
                            )}
                        </Button>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
