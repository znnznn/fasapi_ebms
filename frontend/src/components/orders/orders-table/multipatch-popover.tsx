import type { Table } from '@tanstack/react-table'
import { format } from 'date-fns'
import { Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

import { selectOrders } from '../store/orders'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DatePicker } from '@/components/ui/multipatch-date-picker'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { datesFormat } from '@/config/app'
import type { OrdersData } from '@/store/api/ebms/ebms.types'
import {
    useMultiPatchItemsMutation,
    useMultiPatchOrdersMutation
} from '@/store/api/multiupdates/multiupdate'
import type {
    MultiPatchItemsData,
    MultiPatchOrdersData
} from '@/store/api/multiupdates/multiupdate.types'
import { useAppSelector } from '@/store/hooks/hooks'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

interface Props {
    table: Table<OrdersData>
}

export const MultipatchPopover: React.FC<Props> = ({ table }) => {
    const selectedRows = table.getSelectedRowModel().rows

    const orderItems = selectedRows.map((row) => row.original.origin_items).flat()
    const originItemsIds = orderItems.map((row) => row.id)

    const originOrdersIds = selectedRows.map((row) => row.original.id)

    // const orderItemsWithoutFlow = orderItems.filter(
    //     (item) => !item?.item?.flow?.id
    // ).length

    const [currentRows, setCurrentRows] = useState(selectedRows)

    useEffect(() => {
        if (JSON.stringify(selectedRows) !== JSON.stringify(currentRows)) {
            setCurrentRows(selectedRows)
        }
    }, [selectedRows])

    // const removeItemsWithoutFlow = () => {
    //     const rowsWithFlow = selectedRows.filter(
    //         (row) => row?.original?.origin_items?.every((item) => item?.item?.flow?.id)
    //     )

    //     table.resetRowSelection()

    //     const obj = rowsWithFlow
    //         .map((obj) => {
    //             return { [obj.id]: true }
    //         })
    //         .reduce((acc, val) => {
    //             return { ...acc, ...val }
    //         }, {})

    //     table.setRowSelection(obj)
    //     setCurrentRows(rowsWithFlow)
    // }

    const handleRowReset = () => table.resetRowSelection()

    const [open, setOpen] = useState(false)
    const [date, setDate] = useState<Date | undefined>(undefined)
    const [shipDate, setShipDate] = useState<Date | undefined>(undefined)

    const [flow, setFlow] = useState(-1)

    const close = () => setOpen(false)

    const [patchItems, { isLoading }] = useMultiPatchItemsMutation()
    const [patchOrders] = useMultiPatchOrdersMutation()

    const scheduled = !useAppSelector(selectOrders).scheduled
    const completed = useAppSelector(selectOrders).isOrderCompleted

    const successToast = (date: string, isOrders: boolean = false) => {
        const message = (
            <span>
                {date && isOrders && scheduled ? (
                    <>
                        Order(s) move to <span className='font-semibold'>Scheduled</span>.
                        Production date ➝ <span className='font-semibold'>{date}</span>
                        <br />
                    </>
                ) : (
                    <>
                        Production date ➝ <span className='font-semibold'>{date}</span>
                        <br />
                    </>
                )}
            </span>
        )
        toast.success(
            `${isOrders ? originOrdersIds.length : originItemsIds.length} ${
                isOrders ? 'order' : 'item'
            }(s) updated`,
            {
                description: message
            }
        )
    }

    const errorToast = (message: string) =>
        toast.error('Something went wrong', {
            description: message
        })

    const handlePatchItem = async (date: string | null) => {
        const dataToPatch: MultiPatchItemsData = {
            origin_items: originItemsIds,
            production_date: date
        }

        try {
            await patchItems(dataToPatch)
                .unwrap()
                .then((response) => {
                    successToast(format(response.production_date!, datesFormat.dashes))
                })
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            const errorMessage = isErrorMessage ? error.data.detail : 'Unknown error'

            errorToast(errorMessage)
        }
    }

    const handlePatchOrder = async (date: string | null, shipDate: string | null) => {
        const dataToPatch: MultiPatchOrdersData = {
            origin_orders: originOrdersIds,
            production_date: date!
        }

        if (shipDate) {
            dataToPatch.ship_date = shipDate
        }

        try {
            await patchOrders(dataToPatch)
                .unwrap()
                .then((response) =>
                    successToast(
                        format(response.production_date!, datesFormat.dashes),
                        true
                    )
                )
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            const errorMessage = isErrorMessage ? error.data.detail : 'Unknown error'

            errorToast(errorMessage)
        }
    }

    const onSave = () => {
        const dateToPatch = date ? format(date!, datesFormat.dashes) : null
        const shipDateToPatch = shipDate ? format(shipDate!, datesFormat.dashes) : null

        if (originItemsIds.length > 0 && dateToPatch) {
            handlePatchItem(dateToPatch)
        }

        handlePatchOrder(dateToPatch, shipDateToPatch)
        close()
        setFlow(-1)
        setDate(undefined)
        handleRowReset()
    }

    useEffect(() => setOpen(originOrdersIds.length > 0), [originOrdersIds.length])

    const isSaveDisabled = flow === -1 && !date && !shipDate

    return (
        <Popover
            open={open}
            onOpenChange={setOpen}>
            <PopoverTrigger className='fixed left-1/2 bottom-20 -translate-x-1/2 z-10'></PopoverTrigger>
            <PopoverContent className='w-96'>
                <div className='grid gap-4'>
                    <div className='space-y-2'>
                        <h4 className='flex items-center gap-x-2 font-medium leading-none'>
                            <Badge className='hover:bg-primary'>
                                {originOrdersIds.length}
                            </Badge>
                            Row(s) selected
                        </h4>
                    </div>

                    {/* {orderItemsWithoutFlow ? (
                        <p className='text-sm text-gray-500'>
                            <span className='font-bold'>{orderItemsWithoutFlow} </span>
                            line item(s) have no flow, please select flow for all items or{' '}
                            <Button
                                onClick={removeItemsWithoutFlow}
                                className='p-0 h-fit'
                                variant='link'
                                size='sm'>
                                remove
                            </Button>{' '}
                            orders with these items from selection to set date
                        </p>
                    ) : null} */}

                    {completed ? (
                        <p className='text-sm text-gray-500'>
                            You can't update date for completed orders
                        </p>
                    ) : null}
                    <div className='flex items-center gap-x-3'>
                        <DatePicker
                            date={date}
                            setDate={setDate}
                            disabled={completed}
                        />
                        <DatePicker
                            date={shipDate}
                            setDate={setShipDate}
                            disabled={completed}
                            placeholder='Pick a ship date'
                        />
                    </div>
                    <div className='flex items-center gap-x-2 justify-between'>
                        <Button
                            onClick={onSave}
                            className='flex-1'
                            disabled={isSaveDisabled}>
                            {isLoading ? (
                                <Loader2 className='h-4 w-4 animate-spin' />
                            ) : (
                                'Save'
                            )}
                        </Button>
                        <Button
                            onClick={close}
                            className='flex-1'
                            variant='secondary'>
                            Cancel
                        </Button>
                    </div>
                </div>
            </PopoverContent>
        </Popover>
    )
}
