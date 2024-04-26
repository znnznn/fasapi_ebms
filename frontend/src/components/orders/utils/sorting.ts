import type { Row } from '@tanstack/react-table'

import type { OriginItems } from '@/store/api/ebms/ebms.types'

export const statusFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const statusA = rowA.original.item?.stage?.name?.toLowerCase() ?? ''
    const statusB = rowB.original.item?.stage?.name?.toLowerCase() ?? ''
    const order = {
        unscheduled: 0,
        done: 2
    } as Record<string, number>

    const orderA = order[statusA] !== undefined ? order[statusA] : 1
    const orderB = order[statusB] !== undefined ? order[statusB] : 1

    if (orderA === orderB) {
        return statusA?.localeCompare(statusB)
    }

    return orderA - orderB
}

export const dateFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const dateA = rowA.original?.item?.production_date ?? '0'
    const dateB = rowB.original?.item?.production_date ?? '0'

    return new Date(dateA)?.setHours(0, 0, 0, 0) - new Date(dateB)?.setHours(0, 0, 0, 0)
}

export const widthLengthFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const widthA = +rowA.original?.width || 0
    const widthB = +rowB.original?.width || 0
    const lengthA = +rowA.original?.length || 0
    const lengthB = +rowB.original?.length || 0

    return widthA + lengthA - widthB + lengthB
}

export const notesFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const notesA = rowA.original?.item?.comments
    const notesB = rowB.original?.item?.comments

    return notesA?.length || 0 - notesB?.length || 0
}

export const flowFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const flowA = rowA.original?.item?.flow?.name
    const flowB = rowB.original?.item?.flow?.name

    if (flowA === undefined && flowB === undefined) {
        return 0
    } else if (flowA === undefined) {
        return -1
    } else if (flowB === undefined) {
        return 1
    } else {
        return flowA.localeCompare(flowB)
    }
}

export const priorityFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const priorityA = rowA.original?.item?.priority || 0
    const priorityB = rowB.original?.item?.priority || 0

    return priorityB - priorityA
}

export const locationFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const locationA = rowA.original?.item?.location || 0
    const locationB = rowB.original?.item?.location || 0

    return locationB - locationA
}

export const packagesFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const packagesA = rowA.original?.item?.packages || 0
    const packagesB = rowB.original?.item?.packages || 0

    return packagesB - packagesA
}

export const timeFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const [hour, minute, second] = rowA.original?.item?.time?.split(':')?.map(Number) ?? [
        0, 0, 0
    ]

    const timeA = new Date()?.setHours(hour, minute, second)

    const [hourB, minuteB, secondB] = rowB.original?.item?.time
        ?.split(':')
        ?.map(Number) ?? [0, 0, 0]

    const timeB = new Date()?.setHours(hourB, minuteB, secondB)

    return timeA - timeB
}
