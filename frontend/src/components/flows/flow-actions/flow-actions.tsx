import { MoreHorizontal } from 'lucide-react'

import { EditFlowDialog } from './edit-flow-dialog'
import { RemoveFlowDialog } from './remove-flow-dialog'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { stopPropagation } from '@/utils/stop-events'

interface Props {
    id: number
    name: string
}

export const FlowActions: React.FC<Props> = ({ id, name }) => {
    return (
        <Popover>
            <PopoverTrigger onClick={stopPropagation}>
                <Button
                    className='-mt-1.5'
                    variant='ghost'
                    size='icon'>
                    <MoreHorizontal />
                </Button>
            </PopoverTrigger>
            <PopoverContent className='w-fit p-2 flex flex-col'>
                <EditFlowDialog
                    id={id}
                    name={name}
                />
                <RemoveFlowDialog
                    id={id}
                    name={name}
                />
            </PopoverContent>
        </Popover>
    )
}
