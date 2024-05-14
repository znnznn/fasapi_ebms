import type { Stage } from '../items/items.types'

import type { BaseQueryParams, PatchData, Response } from '@/types/api'

export interface FlowsData {
    id: number
    name: string
    description: string
    position: number
    category: number
    created_at: string
    stages: Stage[]
}

export interface FlowsAddData {
    name: string
    description?: string
    category: number
}

export type FlowsPatchData = PatchData<FlowsAddData>

export type FlowsResponse = Response<FlowsData>

export interface FlowsQueryParams extends BaseQueryParams {
    category__prod_type: string
    search: string
    ordering: string
}
