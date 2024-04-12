import { Skeleton } from '@/components/ui/skeleton'

export const FlowsSkeleton = () => (
    <div className='flex flex-col gap-y-2 mt-4'>
        {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className='w-full h-20 mt-1' />
        ))}
    </div>
)
