export interface SavedNewsItem {
    saved_news_item_id: string
    feed_id: string
    feed_item_id: string
    news_item_id: string

    published: string
    title: string
    description: string
    link: string
    feed_title: string

    alternate_links: string[]
    alternate_title_links: string[]
    alternate_favicons: string[]
    favicon: string

    is_read: boolean
    is_saved: boolean
}

export interface UpsertSavedNewsItemResponse {
    saved_news_item_id: string
}

export interface ScrollableItemsResponse<T> {
    token: string
    items: [T]
}
