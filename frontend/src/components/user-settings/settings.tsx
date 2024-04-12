import { toast } from 'sonner'

import { Button } from '../ui/button'

import { PasswordChange } from './password-change'
import { UserSettingsForms } from './user-settings'
import { useRemoveUserProfilesMutation } from '@/store/api/profiles/profiles'

export const UserSettings = () => {
    const successToast = () =>
        toast.success('Account settings', {
            description: 'Column settings reset successfully'
        })

    const [removeUserProfiles] = useRemoveUserProfilesMutation()

    const handleRemoveUserProfiles = async () => {
        try {
            await removeUserProfiles()
                .unwrap()
                .then(() => {
                    successToast()
                })
        } catch (error) {}
    }

    return (
        <section className='px-3 max-w-[1120px] mx-auto mt-10 p-4 '>
            <div className='flex flex-wrap gap-5 mt-5'>
                <UserSettingsForms />
                <PasswordChange />
            </div>
            <div className='mt-10'>
                <h2 className='text-xl text-secondary-foreground font-semibold'>
                    Accounts settings
                </h2>

                <div className='mt-5'>
                    <Button onClick={handleRemoveUserProfiles} variant='outline'>
                        Reset columns settings
                    </Button>
                </div>
            </div>
        </section>
    )
}
