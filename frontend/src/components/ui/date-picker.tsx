import { format } from 'date-fns'
import { Calendar as CalendarIcon, RotateCcw } from 'lucide-react'
import * as React from 'react'
import type { Matcher } from 'react-day-picker'
import { toast } from 'sonner'

import { selectOrders } from '../orders/store/orders'

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './tooltip'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { datesFormat } from '@/config/app'
import { usePatchItemMutation } from '@/store/api/items/items'
import type { ItemsPatchData } from '@/store/api/items/items.types'
import { useGetCompanyProfilesQuery } from '@/store/api/profiles/profiles'
import { useAppSelector } from '@/store/hooks/hooks'
import { cn } from '@/utils/cn'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

interface Props {
    date: Date | undefined
    itemId: number | undefined
    orderId: string
    disabled?: boolean
    setDate: React.Dispatch<React.SetStateAction<Date | undefined>>
}
export const DatePicker: React.FC<Props> = ({
    date,
    setDate,
    itemId,
    disabled = false,
    orderId
}) => {
    const [open, setOpen] = React.useState(false)

    const close = () => setOpen(false)

    const [patchItem] = usePatchItemMutation()

    const isScheduled = useAppSelector(selectOrders).scheduled

    const successToast = (date: string | null) => {
        const isDateNull = date === null
        const formattedDate = isDateNull ? '' : format(date!, datesFormat.dots)

        const dateMessage = isDateNull
            ? 'Date has been reset'
            : `Date has been changed to ${formattedDate}`

        const scheduledDescription = !isDateNull
            ? dateMessage
            : 'Production date has been reset. Order moved to Unscheduled'

        const unscheduledDescription = isDateNull
            ? dateMessage
            : 'Production date has been updated. Order moved to Scheduled'

        const description = isScheduled ? scheduledDescription : unscheduledDescription

        toast.success(`Item ${itemId}`, { description })
    }

    const errorToast = (message: string) => {
        toast.error(`Item ${itemId}`, {
            description: message
        })
    }
    const handlePatchItem = async (data: ItemsPatchData) => {
        try {
            await patchItem(data)
                .unwrap()
                .then(() => successToast(data.data.production_date!))
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)
            errorToast(isErrorMessage ? error.data.detail : 'Something went wrong')
        }
    }

    const handleSetDate = () => {
        const productionDate = format(date!, datesFormat.dashes)

        const data = {
            production_date: productionDate,
            order: orderId
        }

        handlePatchItem({
            id: itemId!,
            data
        })

        close()
    }

    const handleResetDate = () => {
        const data = {
            production_date: null,
            order: orderId
        }

        handlePatchItem({
            id: itemId!,
            data
        })

        setDate(undefined)
        close()
    }

    const { data } = useGetCompanyProfilesQuery()
    const isWorkingWeekend = data?.working_weekend

    const [disabledDays, setDisabledDays] = React.useState<Matcher[]>([])

    React.useEffect(() => {
        if (!isWorkingWeekend) {
            setDisabledDays([{ dayOfWeek: [0, 6] }])
        }
    }, [isWorkingWeekend])

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    disabled={disabled}
                    variant={'outline'}
                    className={cn(
                        'w-40 justify-start text-left font-normal',
                        !date && 'text-muted-foreground'
                    )}>
                    <CalendarIcon className='mr-2 h-4 w-4' />
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
                    <Button className='flex-1' onClick={handleSetDate}>
                        Set Date
                    </Button>
                    <Button onClick={close} className='flex-1' variant='secondary'>
                        Cancel
                    </Button>
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
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
