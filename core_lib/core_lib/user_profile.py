from dataclasses import dataclass


@dataclass
class UserProfile:
    given_name: str
    family_name: str
    email: str
    avatar_url: str
    is_approved: bool
