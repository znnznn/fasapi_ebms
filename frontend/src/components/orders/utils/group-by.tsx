type KeyFinder<T> = ((item: T) => string) | keyof T
type Grouped<T> = Array<[string, T[]]>

export const groupBy = <T,>(values: T[], keyFinder: KeyFinder<T>): Grouped<T> => {
    const groupedObj: Map<string, T[]> = values?.reduce(
        (map: Map<string, T[]>, item: T) => {
            const key =
                typeof keyFinder === 'function'
                    ? keyFinder(item)
                    : (item?.[keyFinder] as { order: string })?.order

            if (!map?.has(key)) {
                map?.set(key, [item])
            } else {
                map?.get(key)?.push(item)
            }

            return map
        },
        new Map<string, T[]>()
    )

    return Array.from(groupedObj.entries())
}
