export const getValidValue = (
    value: string | undefined | number | null,
    fallback = '-'
) => value || fallback
