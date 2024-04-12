import { Progress } from '@/components/ui/progress'
import { cn } from '@/utils/cn'

interface Props {
    currentCapacity: number
    maxCapacity: number
}

export const ProgressBar: React.FC<Props> = ({ currentCapacity, maxCapacity }) => {
    const currentPercentage = (currentCapacity / maxCapacity) * 100

    const colors = {
        green: 'bg-green-500',
        red: 'bg-destructive',
        yellow: 'bg-yellow-500'
    } as const

    const getCurrentColor = (currentPercentage: number) => {
        if (currentPercentage >= 0 && currentPercentage < 50) {
            return colors.green
        } else if (currentPercentage >= 50 && currentPercentage <= 80) {
            return colors.yellow
        } else if (currentPercentage > 80) {
            return colors.red
        }
    }

    const currentColorClass = getCurrentColor(currentPercentage)

    return (
        <div>
            <div className='text-sm text-neutral-400'>
                Rollforming: Max Capacity of Bends
            </div>

            <div className='flex items-center gap-x-2 mt-1'>
                <Progress className={cn(currentColorClass)} value={currentPercentage} />

                <div className={'text-sm text-neutral-700'}>
                    <span>{currentCapacity}</span>
                    &nbsp;/&nbsp;<span>{maxCapacity}</span>
                </div>
            </div>
        </div>
    )
}
