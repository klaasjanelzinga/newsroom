export interface NewsItem {
    _id: string
    feed_id: string
    feed_item_id: string

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
    saved_news_item_id: string | null
}

export interface GetNewsItemsResponse {
    token: string
    news_items: NewsItem[]
    number_of_unread_items: number
}

export interface GetReadNewsItemsResponse {
    token: string
    news_items: NewsItem[]
    number_of_unread_items: number
}
