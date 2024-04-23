import type { UserComment } from '../users/users.types'

import type { PatchData, Response } from '@/types/api'

export interface CommentsData {
    id: number
    user: UserComment
    item: number
    text: string
    created_at: string
}

export interface CommentsAddData {
    user: number
    item: string
    text: string
    order: string
}

export type CommentsPatchData = PatchData<CommentsAddData>

export type CommentsResponse = Response<CommentsData>
