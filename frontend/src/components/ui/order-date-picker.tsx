import { format } from 'date-fns'
import { Calendar as CalendarIcon, RotateCcw } from 'lucide-react'
import * as React from 'react'
import { useEffect, useState } from 'react'
import type { Matcher } from 'react-day-picker'
import { toast } from 'sonner'

import { selectOrders } from '../orders/store/orders'

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './tooltip'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { datesFormat } from '@/config/app'
import { useGetCompanyProfilesQuery } from '@/store/api/profiles/profiles'
import {
    useAddSalesOrderMutation,
    usePatchSalesOrderMutation
} from '@/store/api/sales-orders/sales-orders'
import type {
    SalesOrdersAddData,
    SalesOrdersPatchData
} from '@/store/api/sales-orders/sales-orders.types'
import { useAppSelector } from '@/store/hooks/hooks'
import { cn } from '@/utils/cn'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

interface Props {
    date: Date | undefined
    itemId: number | undefined
    orderId: string
    disabled?: boolean
    defaultDate?: string | null
    setDate: React.Dispatch<React.SetStateAction<Date | undefined>>
}
export const OrderDatePicker: React.FC<Props> = ({
    date,
    setDate,
    itemId,
    defaultDate = null,
    disabled = false,
    orderId
}) => {
    const [open, setOpen] = React.useState(false)

    const close = () => setOpen(false)

    const [patchSalesOrder] = usePatchSalesOrderMutation()

    const [addSalesOrder] = useAddSalesOrderMutation()

    const isScheduled = useAppSelector(selectOrders).scheduled

    const successToast = (date: string | null) => {
        const isDateNull = date === null

        const dateMessage = isDateNull
            ? 'Production date has been reset'
            : `Production date has been changed to ${date}`

        const scheduledDescription = !isDateNull
            ? dateMessage
            : 'Production date has been reset. Order moved to Unscheduled'

        const unscheduledDescription = isDateNull
            ? dateMessage
            : `Production date has been ${
                  itemId ? 'updated' : 'added'
              }. Order moved to Scheduled`

        const description =
            isScheduled === 'true' ? scheduledDescription : unscheduledDescription

        toast.success(`Order ${orderId}`, { description })
    }

    const errorToast = (message: string) => {
        toast.error(`Order ${orderId}`, {
            description: message
        })
    }

    const handlePatchSalesOrder = async (data: SalesOrdersPatchData) => {
        try {
            await patchSalesOrder(data)
                .unwrap()
                .then(() => successToast(data.data.production_date!))
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)
            errorToast(isErrorMessage ? error.data.detail : 'Something went wrong')
        }
    }

    const handleAddSalesOrder = async (data: SalesOrdersAddData) => {
        try {
            await addSalesOrder(data)
                .unwrap()
                .then(() => {
                    successToast(data.production_date!)
                })
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            const errorMessage = isErrorMessage
                ? error.data.detail
                : 'Something went wrong'

            errorToast(errorMessage)
        }
    }

    const handleSetDate = () => {
        const productionDate = format(date!, datesFormat.dashes)

        const data = {
            production_date: productionDate,
            order: orderId
        }

        if (!itemId) {
            handleAddSalesOrder(data)
        } else {
            handlePatchSalesOrder({
                id: itemId!,
                data
            })
        }

        close()
    }

    const handleResetDate = () => {
        const data = {
            production_date: null,
            order: orderId
        }

        handlePatchSalesOrder({
            id: itemId!,
            data
        })

        setDate(undefined)
        close()
    }

    const { data } = useGetCompanyProfilesQuery()
    const isWorkingWeekend = data?.working_weekend

    const [disabledDays, setDisabledDays] = useState<Matcher[]>([])

    useEffect(() => {
        if (!isWorkingWeekend) {
            setDisabledDays([{ dayOfWeek: [0, 6] }])
        }
    }, [isWorkingWeekend])

    return (
        <Popover
            open={open}
            onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    disabled={disabled}
                    variant='outline'
                    className={cn(
                        '!w-40 text-left font-normal justify-start',
                        !date && 'text-muted-foreground'
                    )}>
                    <CalendarIcon className='mr-2 h-3 w-3 flex-shrink-0' />

                    {date ? format(date, 'dd.MM.yyyy EEE') : <span>Pick a date</span>}
                </Button>
            </PopoverTrigger>
            <PopoverContent className='w-auto p-0'>
                <Calendar
                    disabled={disabledDays}
                    mode='single'
                    selected={date}
                    onSelect={setDate}
                    initialFocus
                />
                <div
                    className='flex items-center justify-start gap-x-3 p-3 pt-0 w-full
            '>
                    <Button
                        className='flex-1'
                        onClick={handleSetDate}>
                        Set Date
                    </Button>
                    <Button
                        onClick={close}
                        className='flex-1'
                        variant='secondary'>
                        Cancel
                    </Button>
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    disabled={!defaultDate}
                                    onClick={handleResetDate}
                                    size='icon'
                                    variant='destructive'>
                                    <RotateCcw className='w-4 h-4' />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <span>Reset date</span>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                </div>
            </PopoverContent>
        </Popover>
    )
}
