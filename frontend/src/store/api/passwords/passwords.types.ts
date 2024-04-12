export interface PasswordReset {
    email: string
}
export interface PasswordResetResponse {
    message: string
}

export interface NewPassword {
    new_password1: string
    new_password2: string
}
export interface PasswordResetConfirm extends NewPassword {
    token: string
    uidb64: string
}

export interface PasswordChangeData extends NewPassword {
    old_password: string
}

export interface PasswordChange {
    id: number
    data: PasswordChangeData
}
