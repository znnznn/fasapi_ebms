import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2, PlusCircle } from 'lucide-react'
import { useState } from 'react'
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
import { useAddUserMutation } from '@/store/api/users/users'
import type { UserRoles } from '@/store/api/users/users.types'
import { isErrorWithMessage } from '@/utils/is-error-with-message'
import { stopPropagation } from '@/utils/stop-events'

type FormData = zodInfer<typeof userSchema>

export const AddUserDialog = () => {
    const [open, setOpen] = useState(false)
    const [addUser, { isLoading }] = useAddUserMutation()

    const form = useForm<FormData>({
        resolver: zodResolver(userSchema),
        mode: 'onSubmit',
        shouldFocusError: true
    })

    const currentUserName = `${form.watch('first_name')} ${form.watch('last_name')}`

    const successToast = () =>
        toast.success(`User ${currentUserName}`, {
            description: 'Added successfully'
        })

    const errorToast = (message: string) =>
        toast.error(`User ${currentUserName}`, {
            description: message
        })

    const handleAddUser = async (data: FormData) => {
        try {
            await addUser({
                ...data,
                role: data.role as UserRoles
            })
                .unwrap()
                .then(successToast)
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)
            errorToast(isErrorMessage ? error.data.email : 'Something went wrong')
        }
        form.setValue('email', '')
        form.setValue('first_name', '')
        form.setValue('last_name', '')
        form.setValue('role', '')
        setOpen(false)
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => handleAddUser(formData)

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button onClick={stopPropagation} variant='ghost' size='sm'>
                    <PlusCircle className='h-4 w-4 mr-1' />
                    Add new user
                </Button>
            </DialogTrigger>
            <DialogContent className='rounded-md mx-2'>
                <DialogHeader className='text-left'>
                    <DialogTitle>Add new user</DialogTitle>
                </DialogHeader>
                <Form {...form}>
                    <form className='space-y-5' onSubmit={form.handleSubmit(onSubmit)}>
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
                        <FormField
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
                        <FormField
                            control={form.control}
                            name='role'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Role</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}>
                                        <SelectTrigger className='min-w-[160px] w-full text-left'>
                                            <SelectValue placeholder='Select role' />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value='admin'>Admin</SelectItem>
                                            <SelectItem disabled value='worker'>
                                                Worker
                                            </SelectItem>
                                            <SelectItem disabled value='manager'>
                                                Manager
                                            </SelectItem>
                                        </SelectContent>
                                    </Select>

                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <Button className='w-full' type='submit'>
                            {isLoading ? (
                                <Loader2 className='h-4 w-4 animate-spin' />
                            ) : (
                                'Add new user'
                            )}
                        </Button>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    )
}
