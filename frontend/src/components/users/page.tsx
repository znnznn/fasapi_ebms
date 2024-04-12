import { columns } from './columns'
import { UsersTable } from './table'
import { useGetAllUsersQuery } from '@/store/api/users/users'

export const UsersTablePage = () => {
    const { data, isLoading } = useGetAllUsersQuery({})

    return (
        <div className='mx-auto pt-2'>
            <UsersTable columns={columns} data={data! || []} isLoading={isLoading} />
        </div>
    )
}
