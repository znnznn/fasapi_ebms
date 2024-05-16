import { format } from 'date-fns'
import { Calendar as CalendarIcon } from 'lucide-react'
import * as React from 'react'
import { type DateRange } from 'react-day-picker'

import { ToggleGroupItem } from './toggle-group'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { datesFormat } from '@/config/app'
import { cn } from '@/utils/cn'

interface Props extends React.HTMLAttributes<HTMLDivElement> {
    date: DateRange | undefined
    setDate: React.Dispatch<React.SetStateAction<DateRange | undefined>>
}

export const DatePickerWithRange: React.FC<Props> = ({ className, date, setDate }) => {
    return (
        <div className={cn('grid gap-2', className)}>
            <Popover>
                <PopoverTrigger asChild>
                    <ToggleGroupItem
                        className='w-60 bg-secondary text-secondary-foreground '
                        value='4'
                        key='4'>
                        <CalendarIcon className='mr-2 h-3 w-3 flex-shrink-0' />
                        {date?.from ? (
                            date.to ? (
                                <>
                                    {format(date.from, datesFormat.dots)} -{' '}
                                    {format(date.to, datesFormat.dots)}
                                </>
                            ) : (
                                format(date.from, datesFormat.dots)
                            )
                        ) : (
                            <span>Pick a date</span>
                        )}
                    </ToggleGroupItem>
                </PopoverTrigger>
                <PopoverContent
                    className='w-auto p-0'
                    align='start'>
                    <Calendar
                        initialFocus
                        mode='range'
                        defaultMonth={date?.from}
                        selected={date}
                        onSelect={setDate}
                        numberOfMonths={2}
                    />
                </PopoverContent>
            </Popover>
        </div>
    )
}
