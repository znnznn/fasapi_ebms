import { useEffect, useState } from 'react'

export const useCurrentValue = <T>(value: T): T | undefined => {
    const [currentValue, setCurrentValue] = useState<T | undefined>()
    useEffect(() => {
        if (value !== undefined) {
            setCurrentValue(value)
        }
    }, [value])
    return currentValue
}
