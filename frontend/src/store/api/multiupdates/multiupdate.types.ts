import type { ItemsAddData } from '../items/items.types'

export interface MultiPatchItemsData
    extends Partial<Omit<ItemsAddData, 'origin_item' | 'order'>> {
    origin_items: string[]
}

export interface MultiPatchOrdersData {
    origin_orders: string[]
    packages?: number
    location?: number
    priority?: number
    production_date?: string
    time?: string
}
