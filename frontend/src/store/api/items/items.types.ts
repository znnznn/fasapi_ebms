import type { CommentsData } from '../comments/comments.types'

import type { PatchData, Response } from '@/types/api'

export interface ItemsData {
    id: number
    order?: number
    origin_item: number
    flow?: Flow
    production_date: string
    time: string
    priority: number
    comments: CommentsData[]
    stage: Stage[]
}

export interface Flow {
    id: number
    name: string
    stages: Stage[]
}

export interface Stage {
    id: number
    name: string
    position: number
    color: string
    flow: number
    default?: boolean
    item_ids: number[]
}

export interface ItemsAddData {
    order: string
    origin_item: string
    flow?: number
    priority?: number
    time?: string
    location?: number
    packages?: number
    production_date?: string | null
    stage?: number
    flowName?: string
}

export type ItemsPatchData = PatchData<ItemsAddData> & {
    stageName?: string
    stageColor?: string
}
export type ItemsResponse = Response<ItemsData>
