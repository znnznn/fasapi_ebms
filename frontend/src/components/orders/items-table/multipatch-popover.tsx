import type { Table } from '@tanstack/react-table'
import { format } from 'date-fns'
import { Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

import { selectOrders } from '../store/orders'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DatePicker } from '@/components/ui/multipatch-date-picker'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from '@/components/ui/select'
import { datesFormat } from '@/config/app'
import type { EBMSItemsData } from '@/store/api/ebms/ebms.types'
import { useGetFlowsQuery } from '@/store/api/flows/flows'
import { useMultiPatchItemsMutation } from '@/store/api/multiupdates/multiupdate'
import type { MultiPatchItemsData } from '@/store/api/multiupdates/multiupdate.types'
import { useAppSelector } from '@/store/hooks/hooks'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

interface Props {
    table: Table<EBMSItemsData>
}
export const MultipatchPopover: React.FC<Props> = ({ table }) => {
    const rows = table.getSelectedRowModel().rows.map((row) => row.original)

    const handleRowReset = () => table.resetRowSelection()

    const [open, setOpen] = useState(false)
    const [date, setDate] = useState<Date | undefined>(undefined)

    const [currentRows, setCurrentRows] = useState(rows)

    // const itemsWithoutFlow = currentRows.filter((row) => !row?.item?.flow?.id).length

    // const isItemsWithoutFlow = itemsWithoutFlow > 0

    useEffect(() => {
        if (JSON.stringify(rows) !== JSON.stringify(currentRows)) {
            setCurrentRows(rows)
        }
    }, [rows])

    // const removeItemsWithoutFlow = () => {
    //     const rowsWithFlow = table
    //         .getSelectedRowModel()
    //         .rows.filter((row) => row?.original?.item?.flow?.id)

    //     table.resetRowSelection()

    //     const obj = rowsWithFlow
    //         .map((obj) => {
    //             return { [obj.id]: true }
    //         })
    //         .reduce((acc, val) => {
    //             return { ...acc, ...val }
    //         }, {})

    //     table.setRowSelection(obj)
    //     setCurrentRows(rowsWithFlow.map((row) => row.original))
    // }

    const category = useAppSelector(selectOrders).category
    const scheduled = !useAppSelector(selectOrders).scheduled
    const completed = useAppSelector(selectOrders).isOrderCompleted

    const { data } = useGetFlowsQuery({ category__prod_type: category })

    const [flow, setFlow] = useState(-1)

    const close = () => setOpen(false)

    const flowsData = data?.results

    const [patchItems, { isLoading }] = useMultiPatchItemsMutation()

    const successToast = (date: string, flow: number) => {
        const flowName = flowsData?.find((item) => item.id === flow)?.name

        const message = (
            <span>
                {date && scheduled ? (
                    <>
                        Item(s) move to <span className='font-semibold'>Scheduled</span>.
                        Production date ➝ <span className='font-semibold'>{date}</span>
                        <br />
                    </>
                ) : (
                    date && (
                        <>
                            Production date ➝{' '}
                            <span className='font-semibold'>{date}</span>
                            <br />
                        </>
                    )
                )}
                {flow !== -1 && (
                    <>
                        Flow ➝ <span className='font-semibold'>{flowName}</span>
                    </>
                )}
            </span>
        )

        toast.success(`${currentRows.length} item(s) updated`, {
            description: message
        })
    }

    const errorToast = (message: string) =>
        toast.error('Something went wrong', {
            description: message
        })

    const handlePatchItem = async (flow: number, date: string | null) => {
        const dataToPatch: MultiPatchItemsData = {
            origin_items: currentRows.map((row) => row.id)
        }

        if (flow !== -1) dataToPatch.flow = flow
        if (date) dataToPatch.production_date = date

        try {
            await patchItems(dataToPatch)
                .unwrap()
                .then(() => successToast(dataToPatch.production_date!, flow))
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)

            const errorMessage = isErrorMessage ? error.data.detail : 'Unknown error'

            errorToast(errorMessage)
        }
    }

    const onSave = () => {
        const dateToPatch = date ? format(date!, datesFormat.dashes) : null

        handlePatchItem(flow, dateToPatch)
        close()
        setFlow(-1)
        setDate(undefined)
        handleRowReset()
    }

    const onValueChange = (value: string) => setFlow(+value)

    useEffect(() => setOpen(currentRows.length > 0), [currentRows.length])

    const isSaveDisabled = flow === -1 && !date

    return (
        <Popover
            open={open}
            onOpenChange={setOpen}>
            <PopoverTrigger className='fixed left-1/2 bottom-20 -translate-x-1/2 z-10'></PopoverTrigger>
            <PopoverContent className='w-96'>
                <div className='grid gap-4'>
                    <div className='space-y-2'>
                        <h4 className='flex items-center gap-x-2 font-medium leading-none'>
                            <Badge className='pointer-events-none'>
                                {currentRows.length}
                            </Badge>
                            Row(s) selected
                        </h4>
                    </div>

                    {/* {isItemsWithoutFlow ? (
                        <p className='text-sm text-gray-500'>
                            <span className='font-bold'>{itemsWithoutFlow} </span>
                            item(s) have no flow, please select flow for all items or{' '}
                            <Button
                                onClick={removeItemsWithoutFlow}
                                className='p-0 h-fit'
                                variant='link'
                                size='sm'>
                                remove
                            </Button>{' '}
                            this item(s) from selection to set date
                        </p>
                    ) : null} */}
                    {completed ? (
                        <p className='text-sm text-gray-500'>
                            You can't update date for completed orders
                        </p>
                    ) : null}
                    <div className='flex items-center gap-x-2'>
                        <DatePicker
                            disabled={completed}
                            date={date}
                            setDate={setDate}
                        />
                        <Select onValueChange={onValueChange}>
                            <SelectTrigger className='w-[140px] text-left flex-1'>
                                <SelectValue placeholder='Select flow' />
                            </SelectTrigger>
                            <SelectContent>
                                {flowsData?.map((flow) => (
                                    <SelectItem
                                        key={flow.id}
                                        value={String(flow.id)}>
                                        {flow.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <div className='flex items-center gap-x-2 justify-between'>
                        <Button
                            onClick={onSave}
                            className='flex-1'
                            disabled={isSaveDisabled}>
                            {isLoading ? (
                                <Loader2 className='h-4 w-4 animate-spin' />
                            ) : (
                                'Save'
                            )}
                        </Button>
                        <Button
                            onClick={close}
                            className='flex-1'
                            variant='secondary'>
                            Cancel
                        </Button>
                    </div>
                </div>
            </PopoverContent>
        </Popover>
    )
}
