export interface GetFeedsResponse {
    user_is_subscribed: boolean
    feed: Feed
}

export interface Feed {
    feed_id: string
    url: string
    title: string
    description: string

    image_url: string
    image_title: string
    image_link: string
}

export interface UserProfileRequest {
    display_name: string | null
}

export interface UserResponse {
    display_name: string | null
    email_address: string
    is_approved: boolean
    totp_enabled: boolean
}

export interface ConfirmTotpResponse {
    otp_confirmed: boolean
}

export interface OTPRegistrationResponse {
    generated_secret: string
    uri: string
    backup_codes: string[]
}

export interface ErrorResponse {
    detail: string
}

export interface NewsItem {
    news_item_id: string
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
