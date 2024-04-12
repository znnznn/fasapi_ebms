import { Time } from '@internationalized/date'
import { forwardRef, useEffect, useState } from 'react'
import type { TimeValue } from 'react-aria'
import { TimeFieldStateOptions } from 'react-stately'
import { toast } from 'sonner'

import { TimeField } from './time-field'
import type { Item } from '@/store/api/ebms/ebms.types'
import { useAddItemMutation, usePatchItemMutation } from '@/store/api/items/items'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

interface TimePickerProps extends Omit<TimeFieldStateOptions<TimeValue>, 'locale'> {
    item: Item | null
    originItemId: string
    orderId: string
}

const TimePicker = forwardRef<HTMLDivElement, TimePickerProps>((props, _) => {
    const [time, setTime] = useState<Time | undefined>()

    const hour = +props.item?.time?.split(':')[0]!
    const minute = +props.item?.time?.split(':')[1]!
    const second = +props.item?.time?.split(':')[2]!

    // const currentTime = `${hour}:${minute}:${second}`

    useEffect(() => {
        setTime(props.item?.time ? new Time(hour, minute, second) : undefined)
    }, [props.item?.production_date])

    // const successToast = (prevValue: string, currentValue: string) => {
    //     const description = time
    //         ? `Due by time has been changed from ${prevValue} ➝  to ${currentValue}`
    //         : `Due by time has been set to ${currentValue}`

    //     toast.success('Due by time', {
    //         description
    //     })
    // }

    const errorToast = (message: string) =>
        toast.error('Due by time', {
            description: message
        })

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
            // .then((data) => successToast(currentTime, data?.time))
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            const errorMessage = isErrorMessage
                ? error.data.detail
                : 'Something went wrong'

            errorToast(errorMessage)
        }
    }

    const handleAddOrder = async (value: string) => {
        try {
            await addItem({
                order: props.orderId,
                time: value,
                origin_item: props.originItemId
            }).unwrap()
            // .then((data) => successToast(currentTime, data?.time))
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            const errorMessage = isErrorMessage
                ? error.data.detail
                : 'Something went wrong'

            errorToast(errorMessage)
        }
    }

    const onChange = (value: TimeValue) => {
        if (props.item) {
            handlePatchOrder(value.toString())
        } else {
            handleAddOrder(value.toString())
        }

        const hour = +value.toString()?.split(':')[0]
        const minute = +value.toString()?.split(':')[1]
        const second = +value.toString()?.split(':')[2]

        setTime(new Time(hour, minute, second))
    }
    return <TimeField onChange={onChange} value={time} granularity='second' {...props} />
})

TimePicker.displayName = 'TimePicker'

export { TimePicker }
