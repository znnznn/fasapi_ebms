import { useEffect, useState } from 'react'
import { DebounceInput } from 'react-debounce-input'
import { toast } from 'sonner'

import { Input } from '@/components/ui/input'
import { useAddItemMutation, usePatchItemMutation } from '@/store/api/items/items'
import type { InputEvent } from '@/types/common'
import { capitalize } from '@/utils/capitalize'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

interface Props {
    name: 'priority' | 'packages' | 'location'
    value: number
    orderId: string
    order: string
    itemId: number | undefined
    originItemId: string | undefined
}

export const InputCell: React.FC<Props> = ({
    name,
    orderId,
    itemId,
    value,
    order,
    originItemId
}) => {
    const [addItem] = useAddItemMutation()
    const [patchItem] = usePatchItemMutation()

    const successToast = (message: string) =>
        toast.success(`${capitalize(name)} of ${order} order`, {
            description: message + ' successfully'
        })

    const errorToast = (message: string) =>
        toast.error(`${capitalize(name)} of ${order} order`, {
            description: message
        })

    const handleAddOrder = async (priority: number) => {
        try {
            await addItem({
                order: orderId,
                priority,
                origin_item: originItemId
            })
                .unwrap()
                .then(() => {
                    successToast('Added')
                })
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            const errorMessage = isErrorMessage
                ? error.data.detail
                : 'Something went wrong'

            errorToast(errorMessage)
        }
    }

    const handlePatchOrder = async (value: number, id: number) => {
        try {
            await patchItem({
                id,
                data: {
                    order: orderId,
                    [name]: value,
                    origin_item: originItemId
                }
            })
                .unwrap()
                .then(() => {
                    successToast('Updated')
                })
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            const errorMessage = isErrorMessage
                ? error.data.detail
                : 'Something went wrong'

            errorToast(errorMessage)
        }
    }

    const handleItemMutation = (value: number) => {
        if (!itemId) {
            handleAddOrder(value)
        } else {
            handlePatchOrder(value, itemId)
        }
    }

    const [priorityValue, setPriorityValue] = useState(value)

    useEffect(() => {
        setPriorityValue(value)
    }, [value])

    const onPriorityChange = (e: InputEvent) => {
        const value = +e.target.value

        setPriorityValue(value)
        handleItemMutation(value)
    }

    return (
        <div className='!w-20'>
            <DebounceInput
                element={Input as any}
                value={priorityValue}
                type='number'
                inputMode='numeric'
                placeholder='0'
                debounceTimeout={400}
                onChange={onPriorityChange}
            />
        </div>
    )
}
