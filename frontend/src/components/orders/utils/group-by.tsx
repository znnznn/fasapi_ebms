type KeyFinder<T> = ((item: T) => string) | keyof T

type Grouped<T> = Array<[string, T[]]>

export const groupBy = <T,>(values: T[], keyFinder: KeyFinder<T>): Grouped<T> => {
    const groupedObj: { [key: string]: T[] } = values.reduce((a: any, b: any) => {
        const key = typeof keyFinder === 'function' ? keyFinder(b) : b[keyFinder].order

        if (!a[key]) {
            a[key] = [b]
        } else {
            a[key] = [...a[key], b]
        }

        return a
    }, {})

    return Object.entries(groupedObj)
}
