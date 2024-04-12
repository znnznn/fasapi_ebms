import { Loader2, X } from 'lucide-react'
import { useState } from 'react'

import { Button } from '../../ui/button'

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from '@/components/ui/dialog'
import { useRemoveFlowMutation } from '@/store/api/flows/flows'
import { stopPropagation } from '@/utils/stop-events'

interface Props {
    id: number
    name: string
}

export const RemoveFlowDialog: React.FC<Props> = ({ id, name }) => {
    const [removeFlow, { isLoading }] = useRemoveFlowMutation()

    const [open, setOpen] = useState(false)

    const handleRemoveFlow = async (id: number) => {
        try {
            await removeFlow(id).unwrap()
            setOpen(false)
        } catch (error) {
            error
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button
                    onClick={stopPropagation}
                    className='justify-start'
                    variant='ghost'
                    size='sm'>
                    <X className='h-3.5 w-3.5 mr-1' />
                    Remove
                </Button>
            </DialogTrigger>
            <DialogContent className='sm:max-w-[470px]'>
                <DialogHeader className='text-left'>
                    <DialogTitle>
                        Do you want to remove{' '}
                        <span className='text-destructive'>{name}</span> flow?
                    </DialogTitle>
                </DialogHeader>
                <Button
                    onClick={(e) => {
                        e.stopPropagation()
                        handleRemoveFlow(id)
                    }}
                    variant='destructive'
                    className='flex items-center gap-x-1.5 w-24 '>
                    {isLoading ? (
                        <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                    ) : (
                        'Remove'
                    )}
                </Button>
            </DialogContent>
        </Dialog>
    )
}
