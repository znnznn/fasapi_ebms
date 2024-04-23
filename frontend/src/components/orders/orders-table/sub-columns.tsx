import type { ColumnDef } from '@tanstack/react-table'
import { useEffect, useState } from 'react'

import { FlowCell } from '../cells/flow-cell'
import { InputCell } from '../cells/input-cell'
import { StatusCell } from '../cells/status-cell'
import { TooltipCell } from '../cells/tooltip-cell'
import { NotesSidebar } from '../items-table/notes-sidebar'
import { TimePicker } from '../time-pciker/time-picker'
import { alignCell, createHeader } from '../utils/columns-helpers'
import { dateFn, flowFn, notesFn, statusFn, widthLengthFn } from '../utils/sorting'

import { Button } from '@/components/ui/button'
import { DatePicker } from '@/components/ui/date-picker'
import type { OriginItems } from '@/store/api/ebms/ebms.types'
import { useGetFlowsQuery } from '@/store/api/flows/flows'
import { getValidValue } from '@/utils/get-valid-value'
import { trunc } from '@/utils/trunc'

export const subColumns: ColumnDef<OriginItems>[] = [
    {
        accessorKey: 'category',
        header: ({ column }) =>
            createHeader('Prod. category', column, 'text-left justify-start !w-40'),
        cell: ({ row }) => <div className='pl-4'>{row.original?.category}</div>,
        enableHiding: false
    },
    {
        accessorKey: 'flow',
        header: ({ column }) => createHeader('Flow/Machine', column, '!w-40'),
        sortingFn: flowFn,
        cell: ({ row }) => {
            const { data: flowsData } = useGetFlowsQuery({
                category__prod_type: row.original.category
            })

            return (
                <FlowCell
                    key={row?.original?.id}
                    id={row?.original?.id}
                    flowsData={flowsData?.results!}
                    item={row.original.item!}
                    orderId={row.original?.origin_order}
                />
            )
        }
    },
    {
        accessorKey: 'status',
        sortingFn: statusFn,
        header: ({ column }) => createHeader('Status', column, '!w-40'),
        cell: ({ row }) => (
            <StatusCell
                key={row?.original?.id + row?.original?.item?.stage?.name}
                item={row.original.item}
                invoice={row.original?.order}
                originOrderId={row.original?.origin_order}
            />
        )
    },
    {
        accessorKey: 'priority',
        header: ({ column }) => createHeader('Priority', column, 'w-[112px]'),
        cell: ({ row }) => (
            <InputCell
                name='priority'
                value={row.original?.item?.priority!}
                itemId={row.original?.item?.id}
                orderId={row.original?.origin_order}
                order={row.original.order!}
                originItemId={row.original?.id}
            />
        ),
        accessorFn: (row) => row.item?.priority
    },
    {
        accessorKey: 'packages',
        header: ({ column }) => createHeader('Packages', column, 'w-[112px]'),
        cell: ({ row }) => (
            <InputCell
                key={row.original?.id}
                name='packages'
                value={row.original?.item?.packages!}
                itemId={row.original?.item?.id}
                orderId={row.original.origin_order}
                order={row.original.order!}
                originItemId={row.original?.id}
            />
        )
    },
    {
        accessorKey: 'location',
        header: ({ column }) => createHeader('Location', column, 'w-[112px]'),
        cell: ({ row }) => (
            <InputCell
                key={row.original?.id}
                name='location'
                value={row.original?.item?.location!}
                itemId={row.original?.item?.id}
                orderId={row.original.origin_order}
                order={row.original.order!}
                originItemId={row.original?.id}
            />
        )
    },
    {
        accessorKey: 'production_date',
        sortingFn: dateFn,
        header: ({ column }) => createHeader('Prod. date', column, '!w-40'),
        cell: ({ row }) => {
            const [date, setDate] = useState<Date | undefined>(
                row.original.item?.production_date!
                    ? new Date(row.original.item?.production_date!)
                    : undefined
            )

            useEffect(() => {
                setDate(
                    row.original.item?.production_date
                        ? new Date(row.original.item?.production_date!)
                        : undefined
                )
            }, [row.original.item?.production_date])

            return (
                <DatePicker
                    date={date}
                    setDate={setDate}
                    itemId={row.original?.item?.id}
                    disabled={!row.original.item?.flow?.id || row.original.completed}
                    orderId={row.original?.origin_order}
                />
            )
        }
    },
    {
        accessorKey: 'time',
        header: ({ column }) => createHeader('Due by time', column, '!w-40'),
        cell: ({ row }) => {
            return (
                <TimePicker
                    item={row?.original?.item}
                    originItemId={row.original?.id}
                    // key={row?.original?.item?.id + row?.original?.item?.time!}
                    isDisabled={!row.original.item?.flow?.id || row.original.completed}
                    orderId={row.original?.origin_order}
                />
            )
        }
    },
    {
        accessorKey: 'order',
        header: ({ column }) => createHeader('Order', column, '!w-28'),
        cell: ({ row }) => alignCell(row.original.order)
    },
    {
        accessorKey: 'quantity',
        header: ({ column }) => createHeader('Ordered', column, '!w-28'),
        cell: ({ row }) => alignCell(row.original.quantity),
        sortingFn: 'alphanumeric'
    },
    {
        accessorKey: 'shipped',
        header: ({ column }) => createHeader('Shipped', column, '!w-28'),
        cell: ({ row }) => alignCell(row?.original.shipped!),
        sortingFn: 'alphanumeric'
    },
    {
        accessorKey: 'color',
        header: ({ column }) => createHeader('Color', column, '!w-28'),
        cell: ({ row }) => alignCell(getValidValue(row.original.color))
    },
    {
        accessorKey: 'profile',
        header: ({ column }) => createHeader('Profile', column, '!w-28'),
        cell: ({ row }) => alignCell(getValidValue(row.original.profile))
    },
    {
        accessorKey: 'customer',
        header: ({ column }) =>
            createHeader('Customer', column, 'text-left justify-start'),
        cell: ({ row }) => (
            <div className='w-72 pl-4'>{getValidValue(row.original.customer)}</div>
        )
    },
    {
        accessorKey: 'id_inven',
        header: ({ column }) =>
            createHeader('ID', column, 'text-left justify-start !w-28'),
        cell: ({ row }) => <div className='w-28 pl-4'>{row.original?.id_inven}</div>
    },
    {
        accessorKey: 'bends',
        header: ({ column }) => createHeader('Bends', column, '!w-28'),
        cell: ({ row }) => alignCell(row.original?.bends),
        sortingFn: 'alphanumeric'
    },
    {
        accessorKey: 'weight',
        header: ({ column }) =>
            createHeader('Weight', column, 'text-left justify-start !w-28'),
        cell: ({ row }) => alignCell(row.original?.weight),
        sortingFn: 'alphanumeric'
    },
    {
        accessorKey: 'w/l',
        header: ({ column }) => createHeader('W/L', column, '!w-28'),
        sortingFn: widthLengthFn,
        cell: ({ row }) => alignCell(`${row.original?.width} / ${row.original?.length}`)
    },
    {
        accessorKey: 'description',
        header: () => (
            <Button variant='ghost' className='w-full justify-start'>
                Description
            </Button>
        ),

        cell: ({ row }) => (
            <div className='w-64 pl-4'>
                <TooltipCell
                    value={row.original?.description}
                    truncedValue={trunc(row.original?.description, 36)}
                />
            </div>
        )
    },
    {
        accessorKey: 'comments',
        sortingFn: notesFn,
        header: ({ column }) => createHeader('Notes', column, '!w-36'),
        cell: ({ row }) => (
            <NotesSidebar
                notes={row.original?.item?.comments!}
                itemId={row.original?.id}
                orderId={row.original?.origin_order}
            />
        )
    }
]
