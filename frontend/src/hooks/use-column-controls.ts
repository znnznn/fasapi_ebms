import type { ColumnDef, VisibilityState } from '@tanstack/react-table'
import type { Table } from '@tanstack/react-table'
import { useEffect, useState } from 'react'
import type { DragEvent } from 'react'

import type { UsersProfileData } from '@/store/api/profiles/profiles.types'

export const useColumnOrder = (
    usersProfilesData: UsersProfileData[],
    page: 'items' | 'orders'
) => {
    const defaultOrder = usersProfilesData
        ?.find((profile) => profile.page === page)
        ?.show_columns?.split(',')

    const [columnOrder, setColumnOrder] = useState(defaultOrder)

    useEffect(() => {
        setColumnOrder(defaultOrder)
    }, [usersProfilesData])

    const defaultColumns = ['select', 'arrow']

    if (page === 'items') {
        defaultColumns.push('flow', 'status', 'production_date')
    }

    return {
        columnOrder: [...defaultColumns, ...(columnOrder ?? [])]
    }
}

export const useColumnVisibility = (
    usersProfilesData: UsersProfileData[],
    page: 'items' | 'orders',
    columns: ColumnDef<any, any>[]
) => {
    const defaultColumnVisibility = usersProfilesData
        ?.filter((profile) => profile.page === page)
        ?.map((profile) => {
            const tableColumns = columns
                .map((column) => (column as any).accessorKey)
                ?.filter(Boolean)

            const showColumns = profile.show_columns?.split(',')

            const columnVisibility: VisibilityState = {}

            tableColumns.forEach((column) => {
                if (showColumns?.includes(column)) {
                    columnVisibility[column] = true
                } else {
                    columnVisibility[column] = false
                }
            })

            return columnVisibility
        })

    const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})

    useEffect(() => {
        setColumnVisibility(defaultColumnVisibility?.[0]!)
    }, [usersProfilesData])

    return {
        columnVisibility
    }
}

export function useColumnDragDrop<T>(table: Table<T>, page: string, handleFunction: any) {
    let columnBeingDragged: number

    const onDragStart = (e: DragEvent<HTMLElement>) =>
        (columnBeingDragged = Number(e.currentTarget.dataset.columnIndex))

    const onDrop = (e: DragEvent<HTMLElement>) => {
        e.preventDefault()
        const newPosition = Number(e.currentTarget.dataset.columnIndex)
        const currentCols = table.getVisibleLeafColumns().map((c: any) => c.id)
        const colToBeMoved = currentCols.splice(columnBeingDragged, 1)

        currentCols.splice(newPosition, 0, colToBeMoved[0])

        table.setColumnOrder(currentCols!)

        const filterdCols = currentCols.filter(
            (col) => col !== 'select' && col !== 'arrow'
        )

        try {
            handleFunction({ show_columns: filterdCols.join(','), page })
        } catch (error) {}
    }

    return { onDragStart, onDrop }
}
