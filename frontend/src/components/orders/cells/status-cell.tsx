import { useEffect, useMemo, useState } from 'react'
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
import { usePatchItemMutation, usePatchOrderItemMutation } from '@/store/api/items/items'
import type { ItemsPatchData } from '@/store/api/items/items.types'
import { useAppSelector } from '@/store/hooks/hooks'
import { cn } from '@/utils/cn'
import { isErrorWithMessage } from '@/utils/is-error-with-message'
import { trunc } from '@/utils/trunc'

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

    const statuses = useMemo(
        () => flow?.stages?.slice().sort((a, b) => a.position - b.position),
        [flow?.stages]
    )

    const [defaultStatus, setDefaultStatus] = useState(stageId ? String(stageId) : '')

    useEffect(() => {
        setDefaultStatus(stageId ? String(stageId) : '')
    }, [stageId])

    const isCompleted = useAppSelector(selectOrders).isOrderCompleted

    const category = useAppSelector(selectCategory)

    const orderCompletedToast = () =>
        toast.success(`Order ${originOrderId}`, {
            description: 'Has been moved to Completed'
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
            description: <div>{description}</div>
        })
    }

    const errorToast = (message: string) =>
        toast.error(`Item ${item?.origin_item}`, {
            description: message
        })

    const [patchItem] = usePatchItemMutation()
    const [patchOrderItem] = usePatchOrderItemMutation()

    const patchFunction = category ? patchItem : patchOrderItem

    const handlePatchItem = async (data: ItemsPatchData) => {
        try {
            await patchFunction(data)
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

        setDefaultStatus(value)

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

    const hexToRGBA = (hex: string, opacity: number = 10) => {
        const r = parseInt(hex.substring(1, 3), 16)
        const g = parseInt(hex.substring(3, 5), 16)
        const b = parseInt(hex.substring(5, 7), 16)

        const alpha = opacity / 100

        return `rgba(${r}, ${g}, ${b}, ${alpha})`
    }

    return (
        <Select
            onValueChange={onValueChange}
            defaultValue={defaultStatus}
            value={defaultStatus}
            disabled={isDisabled}
            // key={flowId}
        >
            <SelectTrigger className='max-w-40'>
                <SelectValue placeholder='Select status' />
            </SelectTrigger>
            <SelectContent>
                {statuses?.map((status) => {
                    const wasSelected = status.item_ids.includes(item?.id!)
                    return (
                        <SelectItem
                            style={{
                                backgroundColor: wasSelected
                                    ? hexToRGBA(status.color, 10)
                                    : ''
                            }}
                            className='first:mt-0 mt-1'
                            key={status.id}
                            value={String(status.id)}>
                            <div className='flex items-center gap-x-1.5'>
                                <div
                                    className='w-3 h-3 rounded-sm'
                                    style={{
                                        backgroundColor: status.color
                                    }}></div>
                                {trunc(status.name, 14)}
                                {wasSelected ? (
                                    <div className='w-1 h-1 rounded-full bg-foreground'></div>
                                ) : null}
                            </div>
                        </SelectItem>
                    )
                })}
            </SelectContent>
        </Select>
    )
}
