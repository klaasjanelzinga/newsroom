from fastapi import APIRouter, Response
from pydantic.dataclasses import dataclass
from starlette import status

user_router = APIRouter()


@dataclass
class User:
    given_name: str
    family_name: str
    email: str
    avatar_url: str


@user_router.post("/user/signup", response_model=User)
async def signup(token: str, user: User, response: Response) -> User:
    response.status_code = status.HTTP_201_CREATED
    return User(email="test@test.com", avatar_url="http://test.com", given_name="test", family_name="test")
