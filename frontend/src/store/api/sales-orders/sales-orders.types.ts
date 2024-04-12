import type { PatchData, Response } from '@/types/api'

export interface SalesOrdersData {
    id: number
    order: string
    priority: number
    production_date: string | null
}

export type SalesOrdersAddData = Partial<Omit<SalesOrdersData, 'id'>>

export type SalesOrdersPatchData = PatchData<SalesOrdersAddData>

export type SalesOrdersResponse = Response<SalesOrdersData>
