interface ErrorWithMessage {
    data: {
        email: string
        detail: string
        package: string
        location: string
        priority: string
        order: string
        wrong_old_password: string
    }
}

export const isErrorWithMessage = (error: unknown): error is ErrorWithMessage =>
    typeof error === 'object' &&
    error !== null &&
    'data' in error &&
    typeof (error as Record<string, unknown>).data === 'object'
