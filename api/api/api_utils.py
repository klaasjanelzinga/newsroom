from pydantic.main import BaseModel


class ErrorMessage(BaseModel):
    detail: str
