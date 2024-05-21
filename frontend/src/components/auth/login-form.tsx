import { zodResolver } from '@hookform/resolvers/zod'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { type SubmitHandler, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import type { infer as zodInfer } from 'zod'

import { Button } from '../ui/button'
import { Checkbox } from '../ui/checkbox'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from '../ui/form'
import { Input } from '../ui/input'

import { ForgetPasswordModal } from './forget-password-modal'
import { loginSchema } from '@/config/validation-schemas'
import { useLoginMutation } from '@/store/api'

type FormData = zodInfer<typeof loginSchema>

export const LoginForm = () => {
    const [rememberMe, setRememberMe] = useState<boolean>(false)

    if (rememberMe) {
        localStorage.setItem('rememberMe', JSON.stringify({ rememberMe: true }))
    } else {
        localStorage.removeItem('rememberMe')
    }

    const onRememberMe = () => setRememberMe((prev) => !prev)

    const navigate = useNavigate()

    const [login, { isLoading }] = useLoginMutation()

    const handleLogin = async (data: FormData) => {
        try {
            await login(data).unwrap()
            if (!rememberMe) {
                sessionStorage.setItem('rememberMe', JSON.stringify({ rememberMe: true }))
            }
            navigate('/')
        } catch (error) {
            error
        }
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => handleLogin(formData)

    const form = useForm<FormData>({
        resolver: zodResolver(loginSchema),
        mode: 'onSubmit',
        shouldFocusError: true
    })

    return (
        <div className='h-screen flex justify-center items-center'>
            <div className='w-[300px] mx-auto'>
                <Form {...form}>
                    <form
                        className='space-y-5'
                        onSubmit={form.handleSubmit(onSubmit)}>
                        <FormField
                            disabled={isLoading}
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
                            disabled={isLoading}
                            control={form.control}
                            name='password'
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Password</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder='.......'
                                            type='password'
                                            {...field}
                                        />
                                    </FormControl>

                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <Button
                            className='w-full'
                            disabled={isLoading}
                            type='submit'>
                            {isLoading ? (
                                <Loader2 className='h-4 w-4 animate-spin' />
                            ) : (
                                'Log In'
                            )}
                        </Button>
                    </form>
                </Form>
                <div className='flex justify-between mt-5'>
                    <div className='flex items-center space-x-2'>
                        <Checkbox
                            disabled={isLoading}
                            id='terms'
                            aria-label='Remember me'
                            onClick={onRememberMe}
                        />
                        <label
                            htmlFor='terms'
                            className='text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70'>
                            Remember me
                        </label>
                    </div>

                    <ForgetPasswordModal disabled={isLoading} />
                </div>
            </div>
        </div>
    )
}
