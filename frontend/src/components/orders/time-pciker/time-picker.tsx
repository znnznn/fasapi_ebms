import { Time } from '@internationalized/date'
import { forwardRef, useEffect, useState } from 'react'
import type { TimeValue } from 'react-aria'
import { type TimeFieldStateOptions } from 'react-stately'
import { toast } from 'sonner'

import { TimeField } from './time-field'
import { useCallbackDebounce } from '@/hooks/use-callback-debounce'
import type { Item } from '@/store/api/ebms/ebms.types'
import { useAddItemMutation, usePatchItemMutation } from '@/store/api/items/items'
import type { ItemsAddData } from '@/store/api/items/items.types'

interface TimePickerProps extends Omit<TimeFieldStateOptions<TimeValue>, 'locale'> {
    item: Item | null
    originItemId: string
    orderId: string
}

const TimePicker = forwardRef<HTMLDivElement, TimePickerProps>((props, _) => {
    const [hour, minute] = props?.item?.time?.split(':')?.map(Number) ?? []

    const [time, setTime] = useState(props.item?.time ? new Time(hour, minute) : null)

    useEffect(() => {
        setTime(props.item?.time ? new Time(hour, minute) : null)
    }, [props.item?.time])

    const [patchItem] = usePatchItemMutation()
    const [addItem] = useAddItemMutation()

    const handlePatchOrder = async (value: string) => {
        try {
            await patchItem({
                id: props?.item?.id!,
                data: {
                    origin_item: props.originItemId,
                    time: value
                }
            }).unwrap()
        } catch {}
    }

    const errorToast = ({ message, title }: { message: string; title: string }) => {
        toast.error(title, {
            description: message
        })
    }

    const handleAddItem = async (data: ItemsAddData) => {
        try {
            await addItem(data).unwrap()
        } catch (error) {
            errorToast({
                message: 'Error adding item',
                title: 'Something went wrong'
            })
        }
    }

    const debouncedRequest = useCallbackDebounce((value: TimeValue) => {
        if (props.item?.id) {
            handlePatchOrder(value.toString())
        } else {
            handleAddItem({
                order: props.orderId,
                origin_item: props.originItemId,
                time: value.toString()
            })
        }
    }, 400)

    const onChange = (value: TimeValue) => {
        const [hour, minute] = value?.toString().split(':')?.map(Number)

        setTime(new Time(hour, minute))

        debouncedRequest(value)
    }

    return (
        <TimeField
            onChange={onChange}
            value={time}
            granularity='minute'
            {...props}
        />
    )
})

TimePicker.displayName = 'TimePicker'

export { TimePicker }
