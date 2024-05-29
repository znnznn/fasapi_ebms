import type { ColumnDef } from '@tanstack/react-table'
import { useEffect, useState } from 'react'

import { FlowCell } from '../cells/flow-cell'
import { InputCell } from '../cells/input-cell'
import { StatusCell } from '../cells/status-cell'
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

export const columns: ColumnDef<EBMSItemsData>[] = [
    {
        id: 'select',
        header: ({ table }) => {
            return (
                <div className='!w-10'>
                    <Checkbox
                        className='!ml-2'
                        checked={
                            table.getIsAllPageRowsSelected() ||
                            (table.getIsSomePageRowsSelected() && 'indeterminate')
                        }
                        onCheckedChange={(value) => {
                            table.toggleAllPageRowsSelected(!!value)
                        }}
                        aria-label='Select all'
                    />
                    <MultipatchPopover table={table} />
                </div>
            )
        },
        cell: ({ row }) => (
            <Checkbox
                className='!ml-2 mr-4 data-[state=checked]:bg-muted-foreground border border-muted-foreground'
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
        header: ({ column }) => createHeader('Status', column, '!w-48'),
        cell: ({ row }) => {
            return (
                <StatusCell
                    key={row?.original?.id}
                    item={row.original?.item}
                    originOrderId={row.original.origin_order}
                />
            )
        }
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
                    // key={row.original?.id}
                    date={date}
                    setDate={setDate}
                    originItem={row.original.id}
                    defaultDate={row.original.item?.production_date}
                    itemId={row.original?.item?.id}
                    // disabled={!row.original.item?.flow?.id || row.original.completed}
                    disabled={row.original.completed}
                    orderId={row.original.origin_order}
                />
            )
        }
    },
    {
        accessorKey: 'time',
        header: ({ column }) => createHeader('Time', column, '!w-[90px]'),
        cell: ({ row }) => {
            return (
                <TimePicker
                    // isDisabled={!row.original.item?.flow?.id || row.original.completed}
                    isDisabled={row.original.completed}
                    item={row?.original?.item}
                    originItemId={row.original?.id}
                    orderId={row.original.origin_order}
                />
            )
        }
    },
    {
        accessorKey: 'priority',
        header: ({ column }) => createHeader('Prio.', column, '!w-20'),
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
        header: ({ column }) => createHeader('Pckgs.', column, '!w-20'),
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
        header: ({ column }) => createHeader('Loc.', column, '!w-20'),
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
    // {
    //     accessorKey: 'order',
    //     header: ({ column }) => createHeader('Order', column, 'w-28'),
    //     cell: ({ row }) => <div className='w-28'>{alignCell(row.original.order)}</div>
    // },
    {
        accessorKey: 'quantity',
        header: ({ column }) => createHeader('Ordered', column, '!w-28'),
        cell: ({ row }) => <div className='!w-28'>{alignCell(row.original.quantity)}</div>
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
    // {
    //     accessorKey: 'customer',
    //     header: ({ column }) =>
    //         createHeader('Customer', column, 'text-left justify-start !w-64'),
    //     cell: ({ row }) => (
    //         <div className='w-64 pl-4'>{getValidValue(row.original.customer)}</div>
    //     )
    // },
    {
        accessorKey: 'id_inven',
        header: ({ column }) =>
            createHeader('ID', column, 'text-left justify-start !w-24'),
        cell: ({ row }) => <div className='!w-24 pl-4'>{row.original?.id_inven}</div>
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
        header: () => {
            const groupedView = useAppSelector((store) => store.orders.groupedView)
            const category = !!useAppSelector((store) => store.orders.category)
            return (
                <Button
                    disabled={groupedView && category}
                    variant='ghost'
                    className='text-left justify-start !w-64'>
                    Description
                </Button>
            )
        },
        cell: ({ row }) => <div className='!w-64 pl-4'>{row.original?.description}</div>
    },
    {
        accessorKey: 'comments',
        header: ({ column }) => createHeader('Notes', column, '!w-32'),
        cell: ({ row }) => (
            <NotesSidebar
                notes={row.original?.item?.comments!}
                itemId={row.original?.id}
                orderId={row.original?.order!}
            />
        )
    }
]
