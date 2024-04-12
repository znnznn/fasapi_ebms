import type { ColumnDef, SortingState } from '@tanstack/react-table'

export interface BaseTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[]
    data: TData[]
    isLoading: boolean
}

export interface TableProps<TData, TValue> extends BaseTableProps<TData, TValue> {
    pageCount: number
    limit: number
    offset: number
    isFetching?: boolean
    setPagination: React.Dispatch<
        React.SetStateAction<{
            pageSize: number
            pageIndex: number
        }>
    >
    sorting: SortingState
    setSorting: React.Dispatch<React.SetStateAction<SortingState>>
}
