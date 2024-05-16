import { format } from 'date-fns'
import { Calendar as CalendarIcon } from 'lucide-react'
import * as React from 'react'
import type { Matcher } from 'react-day-picker'

import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { useGetCompanyProfilesQuery } from '@/store/api/profiles/profiles'
import { cn } from '@/utils/cn'

interface Props {
    date: Date | undefined
    disabled?: boolean
    setDate: React.Dispatch<React.SetStateAction<Date | undefined>>
}
export const DatePicker: React.FC<Props> = ({ date, setDate, disabled = false }) => {
    const [open, setOpen] = React.useState(false)

    const close = () => setOpen(false)

    const { data } = useGetCompanyProfilesQuery()
    const isWorkingWeekend = data?.working_weekend

    const [disabledDays, setDisabledDays] = React.useState<Matcher[]>([])

    React.useEffect(() => {
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
                    variant={'outline'}
                    className={cn(
                        'w-40 justify-start text-left font-normal flex-1',
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
                        onClick={close}>
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
