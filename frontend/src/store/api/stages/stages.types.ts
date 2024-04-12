import type { BaseQueryParams, PatchData, Response } from '@/types/api'

export interface StagesData {
    id: number
    name: string
    description?: string
    position?: number
    default?: boolean
    color: string
    flow?: number
}

export interface StagesQueryParams extends BaseQueryParams {
    position: number
    flow: number
    search: string
    ordering: string
}

export type StagesAddData = Omit<StagesData, 'id'>

export type StagesPatchData = PatchData<StagesAddData>

export type StagesResponse = Response<StagesData>
