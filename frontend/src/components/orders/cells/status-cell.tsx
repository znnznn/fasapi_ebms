import { useMemo } from 'react'
import { toast } from 'sonner'

import { selectCategory, selectOrders } from '../store/orders'

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from '@/components/ui/select'
import { useLazyGetOrderQuery } from '@/store/api/ebms/ebms'
import type { Item } from '@/store/api/ebms/ebms.types'
import { usePatchItemMutation } from '@/store/api/items/items'
import type { ItemsPatchData } from '@/store/api/items/items.types'
import { useAppSelector } from '@/store/hooks/hooks'
import { cn } from '@/utils/cn'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

interface Props {
    item: Item | null
    invoice?: string
    originOrderId: string
}

export const StatusCell: React.FC<Props> = ({ item, originOrderId, invoice }) => {
    const { flow, stage, id: itemId } = item || {}
    const [trigger] = useLazyGetOrderQuery()

    const stageId = stage?.id
    const flowId = flow?.id
    const isFlow = !!flowId

    const statuses = useMemo(() => {
        return flow?.stages?.slice().sort((a, b) => a.position - b.position)
    }, [flow?.stages])

    const defaultStatus = stageId ? String(stageId) : ''

    const [patchStatus] = usePatchItemMutation()

    const isCompleted = useAppSelector(selectOrders).isOrderCompleted

    const category = useAppSelector(selectCategory)

    const orderCompletedToast = () =>
        toast.success(`Order ${originOrderId}`, {
            description: 'Has been moved to Completed',
            classNames: {
                toast: '!bg-green-50',
                description: '!text-green-700',
                success: '!text-green-700'
            }
        })

    const successToast = (status: string, color: string) => {
        const isDone = status === 'Done'

        const isFromMessage = stage?.color && stage?.name

        const fromMessage = (
            <span>
                from{' '}
                {
                    <div
                        className='inline-block align-middle  w-3 h-3 rounded-sm'
                        style={{
                            backgroundColor: stage?.color
                        }}></div>
                }{' '}
                {stage?.name}
            </span>
        )

        const toMessage = (
            <span>
                to{' '}
                {
                    <div
                        className='inline-block align-middle  w-3 h-3 rounded-sm'
                        style={{
                            backgroundColor: color
                        }}></div>
                }{' '}
                {status}
            </span>
        )

        const isItemDone = isDone && category

        const allOrdersDescription = isItemDone ? (
            'Has been moved to Completed'
        ) : isFromMessage ? (
            <span>
                Status has been changed {fromMessage} ➝ {toMessage}
            </span>
        ) : (
            <span>Status has been changed {toMessage}</span>
        )

        const completedDescription = !isDone
            ? 'Has been moved to All orders'
            : 'Status has been changed to Done'

        const description = isCompleted ? completedDescription : allOrdersDescription

        const successHeading = category
            ? `Item ${item?.id}`
            : `Item ${item?.id} of Order ${invoice}`

        toast.success(successHeading, {
            description: <div>{description}</div>,
            classNames: {
                toast: cn(isItemDone && '!bg-green-50'),
                description: cn(isItemDone && '!text-green-700'),
                success: cn(isItemDone && '!text-green-700')
            }
        })
    }

    const errorToast = (message: string) =>
        toast.error(`Item ${item?.id}`, {
            description: message
        })

    const handlePatchItem = async (data: ItemsPatchData) => {
        try {
            await patchStatus(data)
                .unwrap()
                .then(() => {
                    if (!category) {
                        trigger({
                            autoid: originOrderId
                        })
                            .unwrap()
                            .then((response) => {
                                response.completed ? orderCompletedToast() : null
                            })
                    }
                })
                .then(() => successToast(data.stageName!, data.stageColor!))
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)
            errorToast(isErrorMessage ? error.data.detail : 'Something went wrong')
        }
    }

    const onValueChange = (value: string) => {
        const currentStatus = statuses?.find((stage) => stage.id === +value)

        const stageName = currentStatus?.name
        const stageColor = currentStatus?.color

        const data = {
            order: originOrderId,
            stage: +value
        }

        handlePatchItem({
            id: itemId!,
            data,
            stageName,
            stageColor
        })
    }

    const isDisabled = !isFlow || flow.stages.length === 0

    return (
        <Select
            onValueChange={onValueChange}
            defaultValue={defaultStatus}
            disabled={isDisabled}
            key={flowId}>
            <SelectTrigger className='max-w-40'>
                <SelectValue placeholder='Select status' />
            </SelectTrigger>
            <SelectContent>
                {statuses?.map((status) => (
                    <SelectItem
                        className='first:mt-0 mt-1'
                        key={status.id}
                        value={String(status.id)}>
                        <div className='flex items-center gap-x-1.5'>
                            <div
                                className='w-3 h-3 rounded-sm'
                                style={{
                                    backgroundColor: status.color
                                }}></div>
                            {status.name}
                        </div>
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    )
}