import type { CommentsData } from '../comments/comments.types'
import type { Flow, Stage } from '../items/items.types'
import type { SalesOrdersData } from '../sales-orders/sales-orders.types'
import type { UserComment } from '../users/users.types'

import type { BaseQueryParams, PatchData, Response } from '@/types/api'

export interface CalendarQueryParams {
    year: number
    month: number
}

export type CapacityKey = 'Rollforming' | 'Trim'
export interface DailyDataCategory {
    capacity: number
    count_orders: number
}

interface DailyDataEntry {
    'Standing seam': DailyDataCategory | null
    Rollforming: DailyDataCategory | null
    Trim: DailyDataCategory | null
    Accessories: DailyDataCategory | null
}

export interface EBMSItemData {
    ship_date: string
}
export type EBMSItemPatchData = PatchData<EBMSItemData>

interface DailyData {
    [date: string]: DailyDataEntry
}

interface CapacityData {
    Rollforming: number
    Trim: number
}

export interface CalendarResponse extends DailyData {
    capacity_data: CapacityData | any
}

export interface Capacity {
    capacity: number | null
    total_capacity: number | null
}
export interface CategoriesData extends Capacity {
    id: number
    guid: string
    name: string
    ar_aid: string
    autoid: string
    flow_count: number
    capacity_id: null | number
}

export interface CategoriesResponse extends Response<CategoriesData> {}

export interface CategoriesQueryParams extends BaseQueryParams {
    production_date: string
}

export interface AllCategoriesData extends Capacity {
    id: number
    name: string
}

export interface OrdersData {
    id: string
    invoice: string
    customer: string
    sales_order: SalesOrdersData
    origin_items: OriginItems[]
    start_date: string
    end_date: string
    ship_date: string
    c_name: string
    c_city: string
    count_items: number
    completed: boolean
}

export interface OrdersResponse extends Response<OrdersData> {}

export interface OrdersItemsData {
    id: number
    invoice: string
    origin_items: OriginItems[]
}

export interface ItemComment {
    id: number
    user: UserComment
    item: string
    text: string
    created_at: string
}
export interface Item {
    id: number
    order: number
    origin_item: string
    flow: Flow
    production_date: string
    time: string
    packages: number
    location: number
    priority: number
    comments: ItemComment[]
    stage: Stage | null
}
export interface OriginItems {
    id: string
    category: string
    description: string
    quantity: string
    shipped: string
    ship_date: string
    width: string
    weight: string
    length: string
    bends: string
    customer: string
    order: string
    id_inven: string
    origin_order: string
    completed: boolean
    profile: string
    color: string
    item: Item
    production_date: string
    priority: number
    comments: CommentsData[]
}

export interface OrdersItemsResponse extends Response<OrdersItemsData> {}

export interface EBMSItemsData {
    id: string
    category: string
    description: string
    quantity: string
    ship_date?: string
    width: string
    completed: boolean
    profile: string
    weight: string
    length: string
    color: string
    item: Item | null
    origin_order: string
    bends: string
    customer: string
    order: string
    id_inven: string
    shipped: string
}

export interface EBMSItemsResponse extends Response<EBMSItemsData> {}

export interface OrdersQueryParams extends BaseQueryParams {
    invoice: number
    name: string
    date: string
    is_scheduled: string | undefined
    created_at: string
    categories: string
    over_due: boolean

    completed: boolean
    search: string
    ordering: string
}

export interface OrderQueryParams extends BaseQueryParams {
    id: number
    category: string
    autoid: string
}
export interface OrderItemsQueryParams extends BaseQueryParams {
    id: number
    category: string
}
export interface EBMSItemsQueryParams extends BaseQueryParams {
    quan: number
    weight: number
    date_range: string
    search: string
    ordering: string
    width: string
    widthd: number
    over_due: boolean
    height: string
    completed: boolean
    heightd: number
    ship_date: string
    order: string
    is_scheduled: string | undefined
    category: string
    production_date: string
    has_comment: boolean
    flow: string
}
