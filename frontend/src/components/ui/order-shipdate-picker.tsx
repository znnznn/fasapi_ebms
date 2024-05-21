import { format } from 'date-fns'
import { Calendar as CalendarIcon } from 'lucide-react'
import * as React from 'react'
import { useEffect, useState } from 'react'
import type { Matcher } from 'react-day-picker'
import { toast } from 'sonner'

import { selectOrders } from '../orders/store/orders'

import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { datesFormat } from '@/config/app'
import { usePatchEBMSItemMutation } from '@/store/api/ebms/ebms'
import type { EBMSItemPatchData } from '@/store/api/ebms/ebms.types'
import { useGetCompanyProfilesQuery } from '@/store/api/profiles/profiles'
import { useAppSelector } from '@/store/hooks/hooks'
import { cn } from '@/utils/cn'

interface Props {
    date: Date | undefined
    orderId: string
    disabled?: boolean
    setDate: React.Dispatch<React.SetStateAction<Date | undefined>>
}
export const OrderShipDatePicker: React.FC<Props> = ({
    date,
    setDate,
    disabled = false,
    orderId
}) => {
    const [open, setOpen] = React.useState(false)

    const close = () => setOpen(false)

    const [patchSalesOrder] = usePatchEBMSItemMutation()

    const isScheduled = useAppSelector(selectOrders).scheduled

    const successToast = (date: string | null) => {
        const isDateNull = date === null

        const dateMessage = isDateNull
            ? 'Ship date has been reset'
            : `Ship date has been changed to ${date}`

        const scheduledDescription = !isDateNull
            ? dateMessage
            : 'Ship date has been reset.'

        const unscheduledDescription = isDateNull
            ? dateMessage
            : `Ship date has been ${!!date ? 'updated' : 'added'}.`

        const description = isScheduled ? scheduledDescription : unscheduledDescription

        toast.success(`Order ${orderId}`, { description })
    }

    const errorToast = (message: string) => {
        toast.error(`Order ${orderId} ship date`, {
            description: message
        })
    }

    const handlePatchSalesOrder = async (data: EBMSItemPatchData) => {
        try {
            await patchSalesOrder(data)
                .unwrap()
                .then(() => successToast(data.data.ship_date!))
        } catch {
            // const isErrorMessage = isErrorWithMessage(error)
            // errorToast(isErrorMessage ? error?.data?.detail : 'Something went wrong')
            errorToast('Something went wrong')
        }
    }

    const handleSetDate = () => {
        const productionDate = format(date!, datesFormat.dashes)

        const data = {
            ship_date: productionDate
        }

        handlePatchSalesOrder({
            id: orderId!,
            data
        })

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
                        'w-full text-left font-normal justify-start',
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
                </div>
            </PopoverContent>
        </Popover>
    )
}
