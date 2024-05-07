import type { Table } from '@tanstack/react-table'

import { Search } from '../orders/search'

import { AddUserDialog } from './actions/add-user-dialog'

interface Props<TData> {
    table: Table<TData>
}

export function Controls<TData>({ table }: Props<TData>) {
    return (
        <div className='flex items-center flex-wrap gap-4'>
            <Search table={table} />
            <AddUserDialog />
        </div>
    )
}
