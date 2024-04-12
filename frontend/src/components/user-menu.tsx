import { LogOut, Settings } from 'lucide-react'
// @ts-ignore
import { Link } from 'react-router-dom'

import { ThemeToggle } from './theme-toggle'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { routes } from '@/config/routes'
import { useAppDispatch, useAppSelector } from '@/store/hooks/hooks'
import { logout, selectUser } from '@/store/slices/auth'
import { getUserAvatarPlaceholder } from '@/utils/get-user-avatar-placeholder'

export const UserMenu = () => {
    const currentUser = useAppSelector(selectUser)
    const dispatch = useAppDispatch()

    const avatarFallback = currentUser?.first_name
        ? currentUser?.first_name?.charAt(0).toUpperCase()! +
          currentUser?.last_name?.charAt(0).toUpperCase()
        : getUserAvatarPlaceholder(currentUser?.email!)

    const handleLogOut = () => dispatch(logout())

    return (
        <DropdownMenu>
            <DropdownMenuTrigger>
                <Avatar>
                    <AvatarImage src='/' />
                    <AvatarFallback className='bg-secondary border border-foreground'>
                        {avatarFallback}
                    </AvatarFallback>
                </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent className='mr-2'>
                <DropdownMenuLabel
                    onClick={handleLogOut}
                    className='flex flex-col items-start font-normal '>
                    <span>{`${currentUser?.first_name} ${currentUser?.last_name}`}</span>
                    <span className='text-muted-foreground'>{currentUser?.email}</span>
                </DropdownMenuLabel>

                <DropdownMenuSeparator />

                <DropdownMenuGroup>
                    <Link to={routes.userSettings}>
                        <DropdownMenuItem>
                            <Settings className='mr-2 h-4 w-4' />
                            <span>User Profile</span>
                        </DropdownMenuItem>
                    </Link>
                    <Link to={routes.companySettings}>
                        <DropdownMenuItem>
                            <Settings className='mr-2 h-4 w-4' />
                            <span>Company settings</span>
                        </DropdownMenuItem>
                    </Link>
                    <ThemeToggle />
                </DropdownMenuGroup>

                <DropdownMenuSeparator />

                <DropdownMenuItem onClick={handleLogOut}>
                    <LogOut className='mr-2 h-4 w-4' />
                    <span>Log out</span>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
