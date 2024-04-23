import type { ColumnDef } from '@tanstack/react-table'
import { useEffect, useState } from 'react'

import { FlowCell } from '../cells/flow-cell'
import { InputCell } from '../cells/input-cell'
import { StatusCell } from '../cells/status-cell'
import { TooltipCell } from '../cells/tooltip-cell'
import { selectOrders } from '../store/orders'
import { TimePicker } from '../time-pciker/time-picker'
import { alignCell, createHeader } from '../utils/columns-helpers'

import { MultipatchPopover } from './multipatch-popover'
import { NotesSidebar } from './notes-sidebar'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { DatePicker } from '@/components/ui/date-picker'
import type { EBMSItemsData } from '@/store/api/ebms/ebms.types'
import { useAppSelector } from '@/store/hooks/hooks'
import { getValidValue } from '@/utils/get-valid-value'
import { trunc } from '@/utils/trunc'

export const columns: ColumnDef<EBMSItemsData>[] = [
    {
        id: 'select',
        header: ({ table }) => {
            return (
                <>
                    <Checkbox
                        checked={
                            table.getIsAllPageRowsSelected() ||
                            (table.getIsSomePageRowsSelected() && 'indeterminate')
                        }
                        onCheckedChange={(value) =>
                            table.toggleAllPageRowsSelected(!!value)
                        }
                        aria-label='Select all'
                    />
                    <MultipatchPopover table={table} />
                </>
            )
        },
        cell: ({ row }) => (
            <Checkbox
                checked={row.getIsSelected()}
                value={row.original.id}
                onCheckedChange={(value) => {
                    row.toggleSelected(!!value)
                }}
                aria-label='Select row'
            />
        ),
        enableSorting: false,
        enableHiding: false
    },
    {
        accessorKey: 'flow',
        header: ({ column }) => createHeader('Flow/Machine', column, '!w-40'),
        cell: ({ row }) => {
            const flowsData = useAppSelector(selectOrders).flowsData ?? []

            return (
                <FlowCell
                    key={row?.original?.id}
                    id={row?.original?.id}
                    flowsData={flowsData}
                    item={row.original.item!}
                    orderId={row.original.origin_order}
                />
            )
        }
    },
    {
        accessorKey: 'status',
        header: ({ column }) => createHeader('Status', column, '!w-40'),
        cell: ({ row }) => (
            <StatusCell
                key={row?.original?.id + row?.original?.item?.stage?.id}
                item={row.original.item}
                originOrderId={row.original.origin_order}
            />
        )
    },
    {
        accessorKey: 'production_date',
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
                    key={row.original?.id}
                    date={date}
                    setDate={setDate}
                    itemId={row.original?.item?.id}
                    disabled={!row.original.item?.flow?.id || row.original.completed}
                    orderId={row.original.origin_order}
                />
            )
        }
    },
    {
        accessorKey: 'time',
        header: ({ column }) => createHeader('Due by time', column, '!w-[144px]'),
        cell: ({ row }) => {
            return (
                <TimePicker
                    isDisabled={!row.original.item?.flow?.id || row.original.completed}
                    item={row?.original?.item}
                    originItemId={row.original?.id}
                    orderId={row.original.origin_order}
                />
            )
        }
    },
    {
        accessorKey: 'priority',
        header: ({ column }) => createHeader('Priority', column, 'w-[112px]'),
        cell: ({ row }) => (
            <InputCell
                key={row.original?.id}
                name='priority'
                value={row.original?.item?.priority!}
                itemId={row.original?.item?.id}
                orderId={row.original.origin_order}
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
        accessorKey: 'order',
        header: ({ column }) => createHeader('Order', column, 'w-28'),
        cell: ({ row }) => <div className='w-28'>{alignCell(row.original.order)}</div>
    },
    {
        accessorKey: 'quantity',
        header: ({ column }) => createHeader('Ordered', column, 'w-28'),
        cell: ({ row }) => <div className='w-28'>{alignCell(row.original.quantity)}</div>
    },
    {
        accessorKey: 'shipped',
        header: ({ column }) => createHeader('Shipped', column, 'w-28'),
        cell: ({ row }) => <div className='w-28'>{alignCell(row.original.shipped)}</div>
    },
    {
        accessorKey: 'color',
        header: ({ column }) => createHeader('Color', column, 'w-28'),
        cell: ({ row }) => (
            <div className='w-28'>{alignCell(getValidValue(row.original.color))}</div>
        )
    },
    {
        accessorKey: 'profile',
        header: ({ column }) => createHeader('Profile', column, 'w-28'),
        cell: ({ row }) => (
            <div className='w-28'>{alignCell(getValidValue(row.original.profile))}</div>
        )
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
        header: ({ column }) => (
            <div className='w-28'>
                {createHeader('ID', column, 'text-left justify-start')}
            </div>
        ),
        cell: ({ row }) => <div className='w-28 pl-4'>{row.original?.id_inven}</div>
    },
    {
        accessorKey: 'weight',
        header: ({ column }) => createHeader('Weight', column, 'w-28'),
        cell: ({ row }) => <div className='w-28'>{alignCell(row.original?.weight)}</div>
    },
    {
        accessorKey: 'w/l',
        header: ({ column }) => createHeader('W/L', column, 'w-32'),
        cell: ({ row }) => (
            <div className='w-32'>
                {alignCell(`${row.original?.width} / ${row.original?.length}`)}
            </div>
        )
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
        header: ({ column }) => createHeader('Notes', column, 'w-36'),
        cell: ({ row }) => (
            <NotesSidebar
                notes={row.original?.item?.comments!}
                itemId={row.original?.id}
                orderId={row.original?.order!}
            />
        )
    }
]
