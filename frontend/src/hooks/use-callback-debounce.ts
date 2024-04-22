import debounce from 'lodash/debounce'
import { useEffect, useMemo, useRef } from 'react'

export const useCallbackDebounce = <T extends (...args: any[]) => any>(
    callback: T,
    delay: number = 500
) => {
    const ref = useRef<T | null>(null)

    useEffect(() => {
        ref.current = callback
    }, [callback])

    const debouncedCallback = useMemo(() => {
        const func = (...args: Parameters<T>) => {
            ref.current?.(...args)
        }

        return debounce(func, delay)
    }, [delay])

    return debouncedCallback
}
