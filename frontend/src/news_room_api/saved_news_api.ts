import { NewsItem } from "./news_item_api"

export interface SavedNews {
    saved_news_item_id: string
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
}

export interface UpsertSavedNewsItemResponse {
    saved_news_item_id: string
}

export class SavedNewsApi {
    saved_news(): NewsItem[] {
        return []
    }

    delete_saved_news_items(saved_news_item_ids: string[]): void {
        // pass
    }

    save_news_item(news_item_id: string): void {
        // pass
    }
}
