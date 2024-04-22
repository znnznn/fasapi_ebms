import { Time } from '@internationalized/date'
import { forwardRef, useEffect, useState } from 'react'
import type { TimeValue } from 'react-aria'
import { TimeFieldStateOptions } from 'react-stately'

import { TimeField } from './time-field'
import { useCallbackDebounce } from '@/hooks/use-callback-debounce'
import type { Item } from '@/store/api/ebms/ebms.types'
import { usePatchItemMutation } from '@/store/api/items/items'

interface TimePickerProps extends Omit<TimeFieldStateOptions<TimeValue>, 'locale'> {
    item: Item | null
    originItemId: string
    orderId: string
}

const TimePicker = forwardRef<HTMLDivElement, TimePickerProps>((props, _) => {
    const [hour, minute, second] = props?.item?.time?.split(':')?.map(Number) ?? []

    const [time, setTime] = useState(
        props.item?.time ? new Time(hour, minute, second) : undefined
    )

    useEffect(() => {
        setTime(new Time(hour, minute, second))
    }, [props.item?.time])

    const [patchItem] = usePatchItemMutation()

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

    const debouncedRequest = useCallbackDebounce((value: TimeValue) => {
        handlePatchOrder(value.toString())
    }, 400)

    const onChange = (value: TimeValue) => {
        const [hour, minute, second] = value?.toString().split(':')?.map(Number)

        setTime(new Time(hour, minute, second))

        debouncedRequest(value)
    }

    return <TimeField onChange={onChange} value={time} granularity='second' {...props} />
})

TimePicker.displayName = 'TimePicker'

export { TimePicker }
