import { zodResolver } from '@hookform/resolvers/zod'
import { format } from 'date-fns'
import { Loader2, PlusCircleIcon, Send } from 'lucide-react'
import { type SubmitHandler, useForm } from 'react-hook-form'
import type { infer as zodInfer } from 'zod'

import { selectOrders } from '../store/orders'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from '@/components/ui/card'
import { Form, FormControl, FormField, FormItem } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
    Sheet,
    SheetContent,
    SheetFooter,
    SheetHeader,
    SheetTitle,
    SheetTrigger
} from '@/components/ui/sheet'
import { datesFormat } from '@/config/app'
import { commentSchema } from '@/config/validation-schemas'
import {
    useAddItemCommentMutation,
    useAddOrderCommentMutation
} from '@/store/api/comments/comments'
import type { ItemComment } from '@/store/api/ebms/ebms.types'
import { useAppSelector } from '@/store/hooks/hooks'
import { getUserAvatarPlaceholder } from '@/utils/get-user-avatar-placeholder'

interface Props {
    notes: ItemComment[]
    itemId: string
    orderId: string
}
type FormData = zodInfer<typeof commentSchema>

export const NotesSidebar: React.FC<Props> = ({ notes, itemId, orderId }) => {
    const notesLength = notes?.length

    const [addOrderComments, { isLoading: isOrderLoading }] = useAddOrderCommentMutation()
    const [addItemComments, { isLoading: isItemLoading }] = useAddItemCommentMutation()

    const category = useAppSelector(selectOrders).category

    const isOrder = category === ''

    const handleFunction = isOrder ? addOrderComments : addItemComments

    const form = useForm<FormData>({
        resolver: zodResolver(commentSchema),
        mode: 'onSubmit',
        shouldFocusError: true
    })

    const inputValue = form.watch('text')

    const userId = useAppSelector((state) => state.auth?.user?.id)

    const handleAddComments = async (text: string) => {
        form.setValue('text', '')

        try {
            await handleFunction({
                order: orderId,
                item: itemId,
                user: userId!,
                text
            }).unwrap()
        } catch (error) {}
    }

    const onSubmit: SubmitHandler<FormData> = (formData) => {
        handleAddComments(formData.text.trim())
    }

    return (
        <Sheet>
            <SheetTrigger asChild>
                <Button
                    className='!w-32'
                    variant='outline'>
                    {notesLength ? (
                        <div className='flex items-center justify-center w-full gap-x-10'>
                            Notes <Badge>{notesLength}</Badge>
                        </div>
                    ) : (
                        <>
                            <PlusCircleIcon className='w-4 h-4 mr-1' />
                            Add note
                        </>
                    )}
                </Button>
            </SheetTrigger>
            <SheetContent className='p-5'>
                <SheetHeader>
                    <SheetTitle>Notes</SheetTitle>
                </SheetHeader>
                {notesLength ? (
                    <ScrollArea className='h-[85vh] pr-3'>
                        <div className='py-4 flex flex-col justify-center gap-y-3'>
                            {notes.map((note) => (
                                <Card key={note.id}>
                                    <CardHeader className='px-4 pt-4 pb-2'>
                                        <div className='flex items-center gap-x-2'>
                                            <Avatar>
                                                <AvatarFallback>
                                                    {getUserAvatarPlaceholder(
                                                        note?.user?.email ?? ''
                                                    )}
                                                </AvatarFallback>
                                            </Avatar>
                                            <div>
                                                <CardTitle className='text-[16px] font-medium'>
                                                    {note.user.email}
                                                </CardTitle>
                                                <CardDescription>
                                                    {format(
                                                        note.created_at,
                                                        datesFormat.dots
                                                    )}
                                                </CardDescription>
                                            </div>
                                        </div>
                                    </CardHeader>
                                    <CardContent className='px-4 pt-2 pb-4'>
                                        <p>{note.text}</p>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </ScrollArea>
                ) : (
                    <div className='flex items-center flex-col justify-center gap-4 py-4 h-full'>
                        Your notes will appear here
                    </div>
                )}

                <SheetFooter className='absolute h-20 p-4 bottom-0 left-0 right-0 w-full'>
                    <Form {...form}>
                        <form
                            className='relative w-full flex items-center justify-between gap-x-1'
                            autoComplete='off'
                            onSubmit={form.handleSubmit(onSubmit)}>
                            <FormField
                                control={form.control}
                                name='text'
                                render={({ field }) => (
                                    <FormItem className='h-full w-full flex-1'>
                                        <FormControl>
                                            <Input
                                                className='w-full h-full'
                                                placeholder='Leave your note here...'
                                                {...field}
                                            />
                                        </FormControl>
                                    </FormItem>
                                )}
                            />
                            <Button
                                disabled={isItemLoading || isOrderLoading || !inputValue}
                                size='icon'
                                className='h-[calc(100%-10px)] transition-all absolute top-1/2  right-1.5 -translate-y-1/2'
                                type='submit'>
                                {isItemLoading || isOrderLoading ? (
                                    <Loader2 className='h-4 w-4 animate-spin' />
                                ) : (
                                    <Send className='h-5 w-5' />
                                )}
                            </Button>
                        </form>
                    </Form>
                </SheetFooter>
            </SheetContent>
        </Sheet>
    )
}
