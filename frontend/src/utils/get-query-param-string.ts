export const getQueryParamString = <T>(params: T) => {
    const searchParams = new URLSearchParams()

    for (const key in params) {
        if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
            searchParams.append(key, params[key]!.toString())
        }
    }

    return searchParams.toString()
}
