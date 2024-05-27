import type { Table } from '@tanstack/react-table'
import { ArrowLeft, ArrowRight, SkipBack, SkipForward } from 'lucide-react'
import { useEffect, useState } from 'react'

import { Toggle } from '../ui/toggle'

import { selectCategory, setGroupedView } from './store/orders'
import { Button } from '@/components/ui/button'
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from '@/components/ui/select'
import {
    useAddUsersProfilesMutation,
    useGetUsersProfilesQuery
} from '@/store/api/profiles/profiles'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'

interface Props<TData> {
    table: Table<TData>
    page: 'orders' | 'items'
}

export function Pagination<TData>({ table, page }: Props<TData>) {
    const { data: usersProfilesData } = useGetUsersProfilesQuery()
    const [addUsersProfiles] = useAddUsersProfilesMutation()

    const dispatch = useAppDispatch()

    const profiles = usersProfilesData?.find((profile) => profile.page === page)
    const showColumns = profiles?.show_columns?.split(',')

    const [visibleColumns, setVisibleColumns] = useState<string[]>([])

    useEffect(() => {
        if (showColumns) {
            setVisibleColumns(showColumns)
        } else {
            const tableColumns = table
                .getAllColumns()
                .map((column) => column.id)
                .filter((col) => col !== 'select' && col !== 'arrow')

            setVisibleColumns(tableColumns)
        }
    }, [usersProfilesData])

    const onCheckedChange = (column: string, value: boolean) => {
        const newVisibleColumns = value
            ? [...visibleColumns, column]
            : visibleColumns.filter((col) => col !== column)

        addUsersProfiles({
            page,
            show_columns: newVisibleColumns.join(',')
        })
    }

    const isPageCount = !table.getPageCount()

    const [grouped, setGrouped] = useState(true)
    // const [ungrouped, setUngrouped] = useState(false)

    const category = useAppSelector(selectCategory)

    // const handleSetGrouped = (value: boolean) => {
    //     setGrouped(value)
    //     setUngrouped(!value)

    //     dispatch(setGroupedView(value))
    // }

    // const handleSetUngrouped = (value: boolean) => {
    //     setUngrouped(value)
    //     setGrouped(!value)

    //     dispatch(setGroupedView(!value))
    // }

    const handleSetGrouped = (value: boolean) => {
        setGrouped(value)
        dispatch(setGroupedView(value))
    }

    return (
        <div className='flex items-center gap-3 py-2'>
            <div className='flex items-center space-x-2'>
                <p className='text-sm font-medium'>Rows per page</p>
                <Select
                    disabled={isPageCount}
                    value={`${table.getState().pagination.pageSize}`}
                    onValueChange={(value) => {
                        table.setPageSize(Number(value))
                    }}>
                    <SelectTrigger className='h-8 w-[70px]'>
                        <SelectValue placeholder={table.getState().pagination.pageSize} />
                    </SelectTrigger>
                    <SelectContent side='top'>
                        {[10, 20, 30, 40, 50].map((pageSize) => (
                            <SelectItem
                                key={pageSize}
                                value={`${pageSize}`}>
                                {pageSize}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>
            <div className='flex w-[105px] items-center justify-center text-sm font-medium text-left'>
                Page {table.getState().pagination.pageIndex + 1} of{' '}
                {table.getPageCount() || 0}
            </div>

            <div className='flex items-center space-x-2'>
                <Button
                    variant='outline'
                    className='h-8 w-8 p-0 flex'
                    onClick={() => table.setPageIndex(0)}
                    disabled={!table.getCanPreviousPage() || isPageCount}>
                    <span className='sr-only'>Go to first page</span>
                    <SkipBack className='h-4 w-4' />
                </Button>
                <Button
                    variant='outline'
                    className='h-8 w-8 p-0'
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage() || isPageCount}>
                    <span className='sr-only'>Go to previous page</span>
                    <ArrowLeft className='h-4 w-4' />
                </Button>
                <Button
                    variant='outline'
                    className='h-8 w-8 p-0'
                    onClick={() => table.nextPage()}
                    disabled={!table.getCanNextPage() || isPageCount}>
                    <span className='sr-only'>Go to next page</span>
                    <ArrowRight className='h-4 w-4' />
                </Button>
                <Button
                    variant='outline'
                    className='h-8 w-8 p-0 flex'
                    onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                    disabled={!table.getCanNextPage() || isPageCount}>
                    <span className='sr-only'>Go to last page</span>
                    <SkipForward className='h-4 w-4' />
                </Button>
            </div>

            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button
                        variant='outline'
                        className='ml-auto'>
                        Columns
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align='end'>
                    {table
                        .getAllColumns()
                        .filter((column) => column.getCanHide())
                        .filter(
                            (column) =>
                                column.id !== 'production_date' &&
                                column.id !== 'flow' &&
                                column.id !== 'status'
                        )
                        .map((column) => (
                            <DropdownMenuCheckboxItem
                                key={column.id}
                                className='capitalize'
                                checked={column.getIsVisible()}
                                onCheckedChange={(value) => {
                                    column.toggleVisibility(!!value)
                                    onCheckedChange(column.id, !!value)
                                }}>
                                {column.id.replace(/c_/g, '').replace(/_/g, ' ')}
                            </DropdownMenuCheckboxItem>
                        ))}
                </DropdownMenuContent>
            </DropdownMenu>

            {category ? (
                // <DropdownMenu>
                //     <DropdownMenuTrigger asChild>
                //         <Button
                //             variant='outline'
                //             className='ml-auto'>
                //             View
                //         </Button>
                //     </DropdownMenuTrigger>
                //     <DropdownMenuContent align='end'>
                //         <DropdownMenuCheckboxItem
                //             className='capitalize'
                //             checked={grouped}
                //             onCheckedChange={handleSetGrouped}>
                //             Grouped
                //         </DropdownMenuCheckboxItem>
                //         <DropdownMenuCheckboxItem
                //             className='capitalize'
                //             checked={ungrouped}
                //             onCheckedChange={handleSetUngrouped}>
                //             Ungrouped
                //         </DropdownMenuCheckboxItem>
                //     </DropdownMenuContent>
                // </DropdownMenu>
                <Toggle
                    pressed={grouped}
                    onPressedChange={handleSetGrouped}
                    className='data-[state=on]:bg-background data-[state=on]:border-primary data-[state=on]:text-primary data=[state=on]:border'
                    variant='outline'
                    aria-label='Toggle grouped'>
                    Grouped
                </Toggle>
            ) : (
                ''
            )}
        </div>
    )
}
