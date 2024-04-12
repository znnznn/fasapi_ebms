import type { Row } from '@tanstack/react-table'

import type { OriginItems } from '@/store/api/ebms/ebms.types'

export const statusFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const statusA = rowA.original.item?.stage?.name as string
    const statusB = rowB.original.item?.stage?.name as string

    const order = ['unscheduled', 'assigned', 'unscheduled', 'wrapped', 'bent', 'done']

    return order.indexOf(statusA?.toLowerCase()) - order.indexOf(statusB?.toLowerCase())
}

export const dateFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const dateA = rowA.original.item?.production_date as string
    const dateB = rowB.original.item?.production_date as string

    return new Date(dateA).getTime() - new Date(dateB).getTime()
}

export const widthLengthFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const widthA = +rowA.original.width
    const widthB = +rowB.original.width
    const lengthA = +rowA.original.length
    const lengthB = +rowB.original.length

    return widthA + lengthA - widthB + lengthB
}

export const notesFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const notesA = rowA.original.item?.comments
    const notesB = rowB.original.item?.comments

    return notesA.length - notesB.length
}

export const flowFn = (rowA: Row<OriginItems>, rowB: Row<OriginItems>) => {
    const flowA = rowA.original.item?.flow?.name
    const flowB = rowB.original.item?.flow?.name

    return flowA.localeCompare(flowB)
}
