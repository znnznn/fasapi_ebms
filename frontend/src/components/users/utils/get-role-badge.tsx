import { Badge } from '@/components/ui/badge'
import type { UserRoles } from '@/store/api/users/users.types'
import { cn } from '@/utils/cn'

export const getRoleBadge = (role: UserRoles) => {
    const colors = {
        admin: 'text-yellow-500 border-yellow-500',
        worker: 'text-blue-500 border-blue-500',
        manager: 'text-green-500 border-green-500'
    } as const

    return (
        <Badge className={cn(colors[role])} variant='outline'>
            {role}
        </Badge>
    )
}
