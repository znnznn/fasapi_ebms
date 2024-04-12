import { object, string } from 'zod'

import type { NewPassword } from '@/store/api/passwords/passwords.types'

const commonConstraints = {
    email: string().min(1, 'Email is required').email(),
    password: string()
        .min(1, 'Password is required')
        .min(8, 'Password must contain at least 8 characters'),
    text: (message: string) => string().min(1, message),
    confirmPassword: (data: NewPassword) => data.new_password1 === data.new_password2
} as const

export const loginSchema = object({
    email: commonConstraints.email,
    password: commonConstraints.password
})

export const commentSchema = object({
    text: string()
})

export const stageSchema = object({
    name: commonConstraints.text('Stage name is required'),
    description: string().optional()
})

export const flowSchema = object({
    name: commonConstraints.text('Flow name is required')
})

export const capacitySchema = object({
    per_day: commonConstraints.text('Per day is required')
})

const newPasswordSchema = object({
    new_password1: commonConstraints.password,
    new_password2: commonConstraints.text('New password confirmation is required')
})

export const changePasswordSchema = object({
    old_password: commonConstraints.password,
    ...newPasswordSchema.shape
}).refine(commonConstraints.confirmPassword, {
    message: "Passwords don't match",
    path: ['new_password2']
})

export const passwordResetConfirmSchema = object({
    ...newPasswordSchema.shape
}).refine(commonConstraints.confirmPassword, {
    message: "Passwords don't match",
    path: ['new_password2']
})

export const userPatchSchema = object({
    first_name: commonConstraints.text('First name is required'),
    last_name: commonConstraints.text('Last name is required'),
    email: commonConstraints.email
})

export const emailSchema = object({
    email: commonConstraints.email
})

export const userSchema = object({
    ...userPatchSchema.shape,
    role: string({
        required_error: 'Please select an role'
    })
})
