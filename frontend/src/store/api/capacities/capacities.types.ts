import type { PatchData, Response } from '@/types/api'

export interface CapacitiesData {
    id: number
    category: number
    per_day: number
}

export type CapacitiesAddData = Omit<CapacitiesData, 'id'>

export type CapacitiesPatchData = PatchData<CapacitiesAddData>

export type CapacitiesResponse = Response<CapacitiesData>
