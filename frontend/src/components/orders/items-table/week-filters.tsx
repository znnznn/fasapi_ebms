import { Skeleton } from '@radix-ui/themes'
import { useEffect, useState } from 'react'

import { Progress } from '../../ui/progress'
import { ToggleGroup, ToggleGroupItem } from '../../ui/toggle-group'
import { selectCategory, selectOrders, setDate, setOverDue } from '../store/orders'
import { type FormattedDate, getWorkingDays } from '../utils/get-current-weeks-date'

import { useGetCategoriesQuery } from '@/store/api/ebms/ebms'
import { useGetCompanyProfilesQuery } from '@/store/api/profiles/profiles'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'
import { getValidValue } from '@/utils/get-valid-value'

export const WeekFilters = () => {
    const { data } = useGetCompanyProfilesQuery()

    const category = useAppSelector(selectOrders).category
    const scheduled = useAppSelector(selectOrders).scheduled
    const overdue = useAppSelector(selectOrders).overdue

    const isWorkingWeekend = data?.working_weekend
    const currentWeeksDates = getWorkingDays(isWorkingWeekend)

    const dispatch = useAppDispatch()

    const onValueChange = (value: string) => {
        if (overdue) {
            dispatch(setOverDue(overdue ? false : true))
            dispatch(setDate(''))
        } else {
            dispatch(setOverDue(false))

            dispatch(setDate(value))
        }
    }

    const [defaultDate, setDefaultDate] = useState(currentWeeksDates?.[0].date)

    useEffect(() => {
        if (
            (category === 'Rollforming' || category === 'Trim') &&
            scheduled === 'true' &&
            !overdue
        ) {
            setDefaultDate(currentWeeksDates?.[0].date)
        } else {
            setDefaultDate('')
        }
    }, [currentWeeksDates, overdue, scheduled])

    useEffect(() => {
        return () => {
            dispatch(setDate(''))
        }
    }, [category, scheduled])

    useEffect(() => {
        if (scheduled !== 'true') {
            dispatch(setDate(''))
        } else {
            if (category === 'Rollforming' || category === 'Trim') {
                dispatch(setDate(defaultDate))
            }
        }
    }, [scheduled, defaultDate])

    return (category === 'Rollforming' || category === 'Trim') && scheduled === 'true' ? (
        <div className='flex max-[1118px]:w-full items-center gap-y-10 gap-x-1 overflow-x-scroll p-0.5'>
            <ToggleGroup
                key={defaultDate}
                className=''
                defaultValue={defaultDate}
                onValueChange={onValueChange}
                type='single'>
                {currentWeeksDates.map((date) => (
                    <WeekFilter
                        key={date.date}
                        {...date}
                    />
                ))}
            </ToggleGroup>
        </div>
    ) : null
}

const WeekFilter: React.FC<FormattedDate> = ({ date, dateToDisplay }) => {
    const category = useAppSelector(selectCategory)

    const { data, isLoading } = useGetCategoriesQuery({
        production_date: date
    })

    const currentCategory = data?.results?.find(
        (dataCategory) => dataCategory.name === category
    )

    const { capacity, total_capacity } = currentCategory || {}

    const currentPercentage = ((total_capacity ?? 0) / capacity!) * 100 || 0

    const colors = {
        green: 'bg-green-500',
        red: 'bg-red-500',
        yellow: 'bg-yellow-500'
    } as const

    const getCurrentColor = (currentPercentage: number) => {
        if (currentPercentage >= 0 && currentPercentage < 50) {
            return colors.green
        } else if (currentPercentage >= 50 && currentPercentage < 80) {
            return colors.yellow
        } else if (currentPercentage > 80) {
            return colors.red
        }
    }

    const currentColorClass = getCurrentColor(currentPercentage)

    return (
        <ToggleGroupItem
            value={date}
            className='data-[state=on]:shadow-custom shadow-foreground text-[13px] data-[state=on]: -outline-offset-1 max-[1118px]:flex-1 data-[state=on]:outline-1 data-[state=on]:outline-foreground data-[state=on]:outline text-secondary-foreground bg-secondary flex flex-col gap-0.5 h-[41px] py-2 px-1 w-[176px]'>
            {isLoading ? (
                <Skeleton className='w-full h-5' />
            ) : (
                <span className='font-medium'>
                    {dateToDisplay} ({getValidValue(total_capacity, '0')} / {capacity})
                </span>
            )}

            <Progress
                indicatorClassName={currentColorClass}
                className='h-1.5 bg-neutral-200'
                value={currentPercentage > 100 ? 100 : currentPercentage}
            />
        </ToggleGroupItem>
    )
}
