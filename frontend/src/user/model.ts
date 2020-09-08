export interface GetFeedsResponse {
    user_is_subscribed: boolean;
    feed: Feed;
}

export interface Feed {
    feed_id: string;
    url: string;
    title: string;
    description: string;

    image_url: string;
    image_title: string;
    image_link: string;
}

export interface UserProfileResponse {
    given_name: string;
    family_name: string;
    email: string;
    avatar_url: string;
    id_token: string;
}
