from typing import List, Optional, Tuple

from core_lib.application_data import repositories
from core_lib.repositories import SavedNewsItem, User


def save_news_item_from_news_item(news_item_id: str, user: User) -> SavedNewsItem:
    """Saves the news item for the user."""
    news_item = repositories.news_item_repository.fetch_by_id(news_item_id)
    if news_item is None:
        raise Exception("News item not found")
    saved_news_item = SavedNewsItem.parse_obj(news_item.dict(exclude={"saved_news_item_id"}))
    saved_news_item.user_id = user.user_id
    news_item.is_saved = True
    news_item.saved_news_item_id = saved_news_item.saved_news_item_id
    saved_news_item = repositories.saved_news_item_repository.upsert(saved_news_item)
    repositories.news_item_repository.upsert(news_item)
    return saved_news_item


def fetch_saved_news_item_for_user(user: User, cursor: Optional[bytes]) -> Tuple[str, List[SavedNewsItem]]:
    return repositories.saved_news_item_repository.fetch_items(user=user, cursor=cursor, limit=30)


def delete_saved_news_item_with_id(saved_news_item_id: str, user: User) -> None:
    saved_news_item = repositories.saved_news_item_repository.fetch_by_id(saved_news_item_id)
    if saved_news_item is None:
        return  # Was already deleted
    news_item = repositories.news_item_repository.fetch_by_id(saved_news_item.news_item_id)
    if news_item is not None:
        news_item.is_saved = False
        news_item.saved_news_item_id = None
        repositories.news_item_repository.upsert(news_item)
    repositories.saved_news_item_repository.delete_saved_news_item(saved_news_item_id, user)
