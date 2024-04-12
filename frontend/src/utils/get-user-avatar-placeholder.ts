export const getUserAvatarPlaceholder = (email: string) => {
    const [username] = email?.split('@')
    const firstLetters = username?.charAt(0)
    return firstLetters?.toUpperCase()
}
