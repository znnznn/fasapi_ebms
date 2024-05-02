import { zodResolver } from '@hookform/resolvers/zod'
import { Edit2Icon, Loader2 } from 'lucide-react'
import React, { useState } from 'react'
import { type SubmitHandler, useForm } from 'react-hook-form'
import { toast } from 'sonner'
import type { infer as zodInfer } from 'zod'

import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from '../../ui/form'

import { Button } from '@/components/ui/button'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from '@/components/ui/select'
import { userSchema } from '@/config/validation-schemas'
import { usePatchUserMutation } from '@/store/api/users/users'
import type { UserRoles, UsersData } from '@/store/api/users/users.types'
import { isErrorWithMessage } from '@/utils/is-error-with-message'
import { stopPropagation } from '@/utils/stop-events'

type FormData = zodInfer<typeof userSchema>

interface Props {
    user: UsersData
}

export const EditUserDialog: React.FC<Props> = ({ user }) => {
    const { first_name, id, last_name } = user

    const userName = `${first_name} ${last_name}`

    const form = useForm<FormData>({
        resolver: zodResolver(userSchema),
        mode: 'onSubmit',
        shouldFocusError: true,
        defaultValues: user
    })

    const [patchUser, { isLoading }] = usePatchUserMutation()

    const [open, setOpen] = useState(false)

    const successToast = () =>
        toast.success(`User ${userName}`, {
            description: 'Edited successfully'
        })

    const errorToast = (message: string) =>
        toast.error(`User ${userName}`, {
            description: message
        })

    const handlePatchUser = async (data: FormData) => {
        try {
            await patchUser({
                id,
                data: {
                    ...data,
                    role: data.role as UserRoles
                }
            })
                .unwrap()
                .then(successToast)
            setOpen(false)
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)
            errorToast(isErrorMessage ? error.data.detail : 'Something went wrong')
        }
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => handlePatchUser(formData)

    // const isDisabled = user.role === 'admin'

    return (
        <Dialog
            open={open}
            onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button
                    onClick={stopPropagation}
                    className='justify-start'
                    variant='ghost'
                    size='sm'>
                    <Edit2Icon className='h-3.5 w-3.5 mr-2' />
                    Edit
                </Button>
            </DialogTrigger>
            <DialogContent className='rounded-md mx-2'>
                <DialogHeader className='text-left'>
                    <DialogTitle>Edit {userName} ?</DialogTitle>
                </DialogHeader>
                <Form {...form}>
                    <form
                        className='space-y-5'
                        onSubmit={form.handleSubmit(onSubmit)}>
                        <FormField
                            control={form.control}
                            // disabled={isDisabled}
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
                        <FormField
                            control={form.control}
                            // disabled={isDisabled}
                            name='first_name'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>First name</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder='John'
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            // disabled={isDisabled}
                            control={form.control}
                            name='last_name'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Last name</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder='Doe'
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name='role'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Role</FormLabel>
                                    <Select
                                        // disabled={isDisabled}
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}>
                                        <SelectTrigger className='min-w-[160px] w-full text-left'>
                                            <SelectValue placeholder='Select role' />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value='admin'>Admin</SelectItem>
                                            <SelectItem
                                                disabled
                                                value='worker'>
                                                Worker
                                            </SelectItem>
                                            <SelectItem
                                                disabled
                                                value='manager'>
                                                Manager
                                            </SelectItem>
                                        </SelectContent>
                                    </Select>

                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <Button
                            className='w-full'
                            type='submit'
                            // disabled={isDisabled}
                        >
                            {isLoading ? (
                                <Loader2 className='h-4 w-4 animate-spin' />
                            ) : false ? (
                                "You can't edit admin"
                            ) : (
                                'Edit user'
                            )}
                        </Button>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
