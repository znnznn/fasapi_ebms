import type { ColumnDef } from '@tanstack/react-table'
import { MoreHorizontal } from 'lucide-react'

import { createHeader } from '../orders/utils/columns-helpers'

import { EditUserDialog } from './actions/edit-user-dialog'
import { RemoveUserDialog } from './actions/remove-user-dialog'
import { getRoleBadge } from './utils/get-role-badge'
import { Button } from '@/components/ui/button'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import type { UsersData } from '@/store/api/users/users.types'

export const columns: ColumnDef<UsersData>[] = [
    {
        accessorKey: 'email',
        header: ({ column }) =>
            createHeader('Email', column, 'text-left justify-start !w-60'),
        cell: ({ row }) => <div className='pl-4'>{row.original.email}</div>
    },
    {
        accessorKey: 'first_name',
        header: ({ column }) => (
            <div className='w-40'>
                {createHeader('First Name', column, 'text-left justify-start !w-60')}
            </div>
        ),
        cell: ({ row }) => <div className='pl-4'>{row.original?.first_name}</div>
    },
    {
        accessorKey: 'last_name',
        header: ({ column }) => (
            <div className='w-40'>
                {createHeader('Last Name', column, 'text-left justify-start !w-60')}
            </div>
        ),
        cell: ({ row }) => <div className='pl-4'>{row.original?.last_name}</div>
    },
    {
        accessorKey: 'role',
        header: ({ column }) => createHeader('Role', column, 'w-24'),
        cell: ({ row }) => <div className='pl-5'>{getRoleBadge(row.original.role)}</div>
    },
    {
        id: 'actions',
        header: () => (
            <Button variant='ghost' className='w-full'>
                <div className='h-4 w-4 flex-shrink-0' />
            </Button>
        ),
        cell: ({ row }) => {
            return (
                <DropdownMenu>
                    <DropdownMenuTrigger className='mx-auto' asChild>
                        <Button variant='ghost' className='h-8 w-8 p-0'>
                            <span className='sr-only'>Open menu</span>
                            <MoreHorizontal className='h-4 w-4' />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className='flex flex-col'>
                        <DropdownMenuItem asChild>
                            <RemoveUserDialog user={row.original} />
                        </DropdownMenuItem>
                        <DropdownMenuItem asChild>
                            <EditUserDialog user={row.original} />
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            )
        },
        enableSorting: false,
        enableHiding: false
    }
]
