import { Search } from '../orders/search'

import { AddUserDialog } from './actions/add-user-dialog'

export const Controls = () => (
    <div className='flex items-center flex-wrap gap-4'>
        <Search />
        <AddUserDialog />
    </div>
)
