import { selectCategory } from '../store/orders'

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from '@/components/ui/select'
import type { Item } from '@/store/api/ebms/ebms.types'
import type { FlowsData } from '@/store/api/flows/flows.types'
import {
    useAddItemMutation,
    usePatchItemMutation,
    usePatchOrderItemMutation
} from '@/store/api/items/items'
import type { ItemsAddData, ItemsPatchData } from '@/store/api/items/items.types'
import { useAppSelector } from '@/store/hooks/hooks'

interface Props {
    item: Item | undefined
    orderId: string
    id: string
    flowsData: FlowsData[]
}

export const FlowCell: React.FC<Props> = ({ item, orderId, id, flowsData }) => {
    const { flow, id: itemId } = item || {}
    const flowId = flow?.id

    const defalueValue = flowId ? String(flowId) : ''

    const [patchItemStatus] = usePatchItemMutation()
    const [patchOrderStatus] = usePatchOrderItemMutation()

    const category = useAppSelector(selectCategory)

    const [addItem] = useAddItemMutation()

    const handlePatchItem = async (data: ItemsPatchData) => {
        try {
            if (category) {
                await patchItemStatus(data).unwrap()
            } else {
                await patchOrderStatus(data).unwrap()
            }
        } catch (error) {}
    }

    const handleAddItem = async (data: Partial<ItemsAddData>) => {
        try {
            await addItem(data).unwrap()
        } catch (error) {}
    }

    const onValueChange = (value: string) => {
        const flowName = flowsData?.find((flow) => flow.id === +value)?.name

        const data = {
            flow: +value,
            order: orderId,
            flowName
        }

        if (itemId) {
            handlePatchItem({
                id: itemId!,
                data
            })
        } else {
            handleAddItem({
                order: orderId,
                flowName,
                origin_item: id,
                flow: +value
            })
        }
    }

    return (
        <Select
            key={defalueValue}
            defaultValue={defalueValue}
            onValueChange={onValueChange}>
            <SelectTrigger className='w-40 text-left'>
                <SelectValue placeholder='Select flow' />
            </SelectTrigger>
            <SelectContent>
                {flowsData?.map((flow) => (
                    <SelectItem key={flow.id} value={String(flow.id)}>
                        {flow.name}
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    )
}
