import { format } from 'date-fns'

export interface FormattedDate {
    dateToDisplay: string
    date: string
}

export const getWorkingDays = (includeWeekends: boolean = false): FormattedDate[] => {
    const today: Date = new Date()
    const workingDays: Date[] = [today]

    let currentDay: Date = new Date(today)

    if (!includeWeekends && (currentDay.getDay() === 6 || currentDay.getDay() === 0)) {
        workingDays.pop()
    }

    while (workingDays.length < 5) {
        currentDay.setDate(currentDay.getDate() + 1)
        if (currentDay.getDay() !== 6 && currentDay.getDay() !== 0) {
            workingDays.push(new Date(currentDay))
        } else if (includeWeekends) {
            workingDays.push(new Date(currentDay))
        }
    }

    return workingDays.map((date) => ({
        dateToDisplay: format(date, 'd MMM, EEE'),
        date: format(date, 'yyyy-MM-dd')
    }))
}
