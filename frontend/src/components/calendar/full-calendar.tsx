import {
    add,
    eachDayOfInterval,
    endOfMonth,
    endOfWeek,
    format,
    isSameMonth,
    isToday,
    isWeekend,
    parse,
    startOfToday,
    startOfWeek
} from 'date-fns'
import { ArrowLeft, ArrowRight } from 'lucide-react'
import { useState } from 'react'

import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { Skeleton } from '../ui/skeleton'

import { Categories } from './categories'
import { useGetCalendarQuery } from '@/store/api/ebms/ebms'
import type {
    CalendarResponse,
    CapacityKey,
    DailyDataCategory
} from '@/store/api/ebms/ebms.types'
import { useGetCompanyProfilesQuery } from '@/store/api/profiles/profiles'
import { cn } from '@/utils/cn'
import { getValidValue } from '@/utils/get-valid-value'

export const FullCalendar = () => {
    const today = startOfToday()
    const [currentMonth, setCurrentMonth] = useState(format(today, 'MMM yyyy'))

    const firstDayCurrentMonth = parse(currentMonth, 'MMM yyyy', new Date())

    const getNextMonth = () => {
        const firstDayNextMonth = add(firstDayCurrentMonth, { months: 1 })
        setCurrentMonth(format(firstDayNextMonth, 'MMM yyyy'))
    }

    const getPreviousMonth = () => {
        const firstDayPreviousMonth = add(firstDayCurrentMonth, { months: -1 })
        setCurrentMonth(format(firstDayPreviousMonth, 'MMM yyyy'))
    }

    const getCurrentMonthDays = () => {
        return eachDayOfInterval({
            start: startOfWeek(firstDayCurrentMonth, { weekStartsOn: 0 }),
            end: endOfWeek(endOfMonth(firstDayCurrentMonth), { weekStartsOn: 0 })
        })
    }

    const year = +format(firstDayCurrentMonth, 'yyyy')
    const month = +format(firstDayCurrentMonth, 'M')

    const { data: calendarData, isFetching } = useGetCalendarQuery({
        month,
        year
    })

    const [category, setCategory] = useState('Rollforming')
    const onValueChange = (value: string) => setCategory(value)

    return (
        <>
            <div className='flex flex-wrap-reverse gap-4 items-center justify-between py-3 px-3 '>
                <Categories onValueChange={onValueChange} />
                <div className='flex items-center justify-between gap-x-4 w-[218px] max-[440px]:w-full'>
                    <Button
                        onClick={getPreviousMonth}
                        variant='outline'
                        className='h-8 w-8 p-0'>
                        <ArrowLeft className='h-4 w-4' />
                    </Button>

                    <h1 className='scroll-m-20 font-bold '>
                        {format(firstDayCurrentMonth, 'MMM yyyy')}
                    </h1>

                    <Button
                        onClick={getNextMonth}
                        variant='outline'
                        className='h-8 w-8 p-0'>
                        <ArrowRight className='h-4 w-4' />
                    </Button>
                </div>
            </div>

            <div className=' !w-full overflow-x-auto'>
                <Weeks />
                <Body
                    category={category as CapacityKey}
                    caledarData={calendarData!}
                    isFetching={isFetching}
                    currentDays={getCurrentMonthDays()}
                    firstDayCurrentMonth={firstDayCurrentMonth}
                />
            </div>
        </>
    )
}

const Day = ({
    date,
    firstDayCurrentMonth,
    caledarData,
    isFetching,
    category
}: {
    date: Date
    firstDayCurrentMonth: Date
    caledarData: CalendarResponse
    isFetching: boolean
    category: CapacityKey
}) => {
    const isDisabled = isWeekend(date)

    const { data } = useGetCompanyProfilesQuery()
    const isWorkingWeekend = data?.working_weekend

    const currentDate = format(date, 'yyyy-MM-dd')

    const capacity = caledarData?.[currentDate]?.[category]!
    const totalCapacity = caledarData?.capacity_data?.[category]!

    return (
        <div
            className={cn(
                'flex flex-col justify-between flex-1 rounded-sm border p-3 min-w-[187px] gap-y-2',
                isToday(date) && 'border-primary',

                !isSameMonth(date, firstDayCurrentMonth) && 'opacity-50'
            )}>
            <span
                className={cn(
                    'self-end',
                    isToday(date) &&
                        'flex items-center justify-center bg-primary w-8 h-8 rounded-full text-background'
                )}>
                {format(date, 'd')}
            </span>
            {isDisabled && !isWorkingWeekend ? (
                ''
            ) : isFetching ? (
                <Skeleton className='w-full h-8' />
            ) : (
                <Capacity dailyData={capacity} totalCapacity={totalCapacity} />
            )}
        </div>
    )
}

const Body = ({
    currentDays,
    firstDayCurrentMonth,
    caledarData,
    isFetching,
    category
}: {
    currentDays: Date[]
    caledarData: CalendarResponse
    isFetching: boolean
    firstDayCurrentMonth: Date
    category: CapacityKey
}) => {
    return (
        <div className='grid grid-cols-[repeat(7,1fr)] gap-2 px-3'>
            {currentDays.map((currentDate) => (
                <Day
                    category={category}
                    caledarData={caledarData}
                    isFetching={isFetching}
                    date={currentDate}
                    key={currentDate.toString()}
                    firstDayCurrentMonth={firstDayCurrentMonth}
                />
            ))}
        </div>
    )
}

const Weeks = () => {
    return (
        <div className='grid grid-cols-[repeat(7,1fr)] gap-2 px-3 '>
            <div className='text-center p-4 min-w-[187px]'>Sunday</div>
            <div className='text-center p-4 min-w-[187px]'>Monday</div>
            <div className='text-center p-4 min-w-[187px]'>Tuesday</div>
            <div className='text-center p-4 min-w-[187px]'>Wednesday</div>
            <div className='text-center p-4 min-w-[187px]'>Thursday</div>
            <div className='text-center p-4 min-w-[187px]'>Friday</div>
            <div className='text-center p-4 min-w-[187px]'>Saturday</div>
        </div>
    )
}

const Capacity = ({
    dailyData,
    totalCapacity
}: {
    dailyData: DailyDataCategory
    totalCapacity: number
}) => {
    return (
        <div className='text-sm'>
            <div className='h-8 bg-muted/40 mx-auto rounded-md border px-2 flex items-center justify-between gap-x-2'>
                <Badge
                    className='pointer-events-none'
                    variant={dailyData?.count_orders ? 'default' : 'outline'}>
                    {getValidValue(dailyData?.count_orders, '0')}
                </Badge>
                {getValidValue(dailyData?.capacity, '0')} / {totalCapacity}
            </div>
        </div>
    )
}
