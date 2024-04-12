import React from 'react'

import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger
} from '@/components/ui/tooltip'

interface Props {
    value: string
    truncedValue: string
}
export const TooltipCell: React.FC<Props> = ({ truncedValue, value }) => {
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <span>{truncedValue}</span>
                </TooltipTrigger>
                <TooltipContent className='max-w-64'>
                    <span>{value}</span>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    )
}
