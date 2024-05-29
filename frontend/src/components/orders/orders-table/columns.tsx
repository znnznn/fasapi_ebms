import type { ColumnDef } from '@tanstack/react-table'
import { ChevronDown } from 'lucide-react'
import { useEffect, useState } from 'react'

import { alignCell, createHeader } from '../utils/columns-helpers'

import { SalesOrderCell } from './cells/sales-order-cell'
import { MultipatchPopover } from './multipatch-popover'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { CollapsibleTrigger } from '@/components/ui/collapsible'
import { OrderDatePicker } from '@/components/ui/order-date-picker'
import { OrderShipDatePicker } from '@/components/ui/order-shipdate-picker'
import type { OrdersData } from '@/store/api/ebms/ebms.types'
import { cn } from '@/utils/cn'
import { getValidValue } from '@/utils/get-valid-value'

export const columns: ColumnDef<OrdersData>[] = [
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
                        onCheckedChange={(value) =>
                            table.toggleAllPageRowsSelected(!!value)
                        }
                        aria-label='Select all'
                    />
                    <MultipatchPopover table={table} />
                </div>
            )
        },
        cell: ({ row }) => (
            <Checkbox
                className='!ml-2 mt-[3px]'
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
        header: () => (
            <Button
                variant='ghost'
                className='w-full'>
                <div className='h-4 w-4 flex-shrink-0' />
            </Button>
        ),
        id: 'arrow',
        enableHiding: false,
        cell: ({ row }) => (
            <CollapsibleTrigger
                asChild
                className='data-[state=open]:-rotate-90 transition-transform duration-15 '
                disabled={!row.original?.origin_items?.length}>
                <Button
                    variant='ghost'
                    size='icon'>
                    <ChevronDown
                        className={cn(
                            'w-4 h-4 transition-transform duration-15',
                            !row.original.origin_items?.length &&
                                'cursor-not-allowed opacity-50'
                        )}
                    />
                </Button>
            </CollapsibleTrigger>
        )
    },
    {
        accessorKey: 'invoice',
        header: ({ column }) => createHeader('Invoice', column, 'w-[103px]'),
        cell: ({ row }) => (
            <div className='w-[103px]'>{alignCell(row.original?.invoice)}</div>
        )
    },
    {
        accessorKey: 'customer',
        header: ({ column }) =>
            createHeader('Customer', column, 'text-left justify-start w-[256px]'),
        cell: ({ row }) => (
            <div className='w-[256px] pl-4 pr-1'>
                {getValidValue(row.original?.customer)}
            </div>
        )
    },
    {
        accessorKey: 'priority',
        header: ({ column }) => createHeader('Prio.', column, '!w-20]'),
        cell: ({ row }) => (
            <SalesOrderCell
                key={row.original?.id}
                name='priority'
                invoice={row.original?.invoice!}
                value={row.original?.sales_order?.priority!}
                itemId={row.original?.sales_order?.id}
                orderId={row.original.id}
            />
        )
    },
    {
        accessorKey: 'production_date',
        header: ({ column }) => createHeader('Prod. date', column, 'w-40'),
        cell: ({ row }) => {
            const productionDate = row.original.sales_order?.production_date
            const [date, setDate] = useState<Date | undefined>(
                productionDate ? new Date(productionDate) : undefined
            )

            useEffect(() => {
                setDate(productionDate ? new Date(productionDate) : undefined)
            }, [productionDate, row.original?.id])

            return (
                <OrderDatePicker
                    defaultDate={productionDate}
                    disabled={row.original.completed}
                    key={row.original?.id}
                    date={date}
                    setDate={setDate}
                    itemId={row.original?.sales_order?.id}
                    orderId={row.original.id}
                />
            )
        }
    },
    {
        accessorKey: 'ship_date',
        header: ({ column }) => createHeader('Ship date', column, 'w-40'),
        cell: ({ row }) => {
            const shipDate = row.original?.ship_date
            const [date, setDate] = useState<Date | undefined>(
                shipDate ? new Date(shipDate) : undefined
            )

            useEffect(() => {
                setDate(shipDate ? new Date(shipDate) : undefined)
            }, [shipDate, row.original?.id])

            return (
                <OrderShipDatePicker
                    disabled={row.original.completed}
                    key={row.original?.id}
                    date={date}
                    setDate={setDate}
                    orderId={row.original.id}
                />
            )
        }
    },
    {
        accessorKey: 'c_name',
        header: ({ column }) =>
            createHeader(
                'Name',
                column,
                'text-left justify-start max-w-64 min-w-[256px]'
            ),
        cell: ({ row }) => (
            <div className='w-64 pl-4 pr-1'>{getValidValue(row.original.c_name)}</div>
        )
    },
    {
        accessorKey: 'c_city',
        header: ({ column }) => createHeader('City', column, 'w-32'),
        cell: ({ row }) => (
            <div className='w-32'>{alignCell(getValidValue(row.original.c_city))}</div>
        )
    },
    {
        accessorKey: 'count_items',
        header: ({ column }) => createHeader('Line Items', column, 'w-28'),
        cell: ({ row }) => (
            <div className='w-28'>{alignCell(row.original?.count_items)}</div>
        )
    }
]
