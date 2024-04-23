import { useEffect, useState } from 'react'
import { toast } from 'sonner'

import { Label } from '../ui/label'
import { Switch } from '../ui/switch'

import {
    useAddCompanyProfilesMutation,
    useGetCompanyProfilesQuery
} from '@/store/api/profiles/profiles'
import type { CompanyProfileData } from '@/store/api/profiles/profiles.types'
import { isErrorWithMessage } from '@/utils/is-error-with-message'

export const CompanySettings = () => {
    const { data } = useGetCompanyProfilesQuery()
    const [addCompanyProfiles] = useAddCompanyProfilesMutation()

    const handleAddCompanyProfiles = async (data: CompanyProfileData) => {
        try {
            addCompanyProfiles(data).unwrap()
        } catch (error) {
            const isErrorMessage = isErrorWithMessage(error)
            errorToast(isErrorMessage ? error.data.detail : 'Something went wrong')
        }
    }

    const errorToast = (message: string) => {
        toast.error('Working weekend', {
            description: message
        })
    }

    const [checked, setChecked] = useState(data?.working_weekend)

    useEffect(() => {
        setChecked(data?.working_weekend)
    }, [data?.working_weekend])

    const onCheckedChange = (checked: boolean) => {
        setChecked(checked)
        handleAddCompanyProfiles({ working_weekend: checked })
    }

    return (
        <section className='px-3 max-w-[1120px] mx-auto mt-5'>
            <div className='mx-auto bg-muted/40 border p-4 rounded-md w-64 flex items-center justify-between gap-x-4 mt-10'>
                <Label htmlFor='working_weekend'>Working weekend</Label>

                <Switch
                    checked={checked}
                    onCheckedChange={onCheckedChange}
                    id='working_weekend'
                />
            </div>
        </section>
    )
}
