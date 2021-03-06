export interface GetFeedsResponse {
    user_is_subscribed: boolean
    feed: Feed
}

export interface Feed {
    _id: string
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
