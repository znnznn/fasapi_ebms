import { MoreHorizontal } from 'lucide-react'

import { EditStatusDialog } from './edit-status-dialog'
import { RemoveStatusDialog } from './remove-status-dialog'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { stopPropagation } from '@/utils/stop-events'

interface Props {
    id: number
    name: string
    description: string
    color: string
}

export const StatusActions: React.FC<Props> = ({ id, name, color, description }) => {
    return (
        <Popover>
            <PopoverTrigger onClick={stopPropagation}>
                <Button variant='ghost' size='icon'>
                    <MoreHorizontal />
                </Button>
            </PopoverTrigger>
            <PopoverContent className='w-fit p-2 flex flex-col'>
                <EditStatusDialog
                    id={id}
                    name={name}
                    color={color}
                    description={description}
                />
                <RemoveStatusDialog id={id} name={name} />
            </PopoverContent>
        </Popover>
    )
}
