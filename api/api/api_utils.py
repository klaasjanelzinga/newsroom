from pydantic.main import BaseModel


class ErrorMessage(BaseModel):
    detail: str


class EmptyResult(BaseModel):
    result: bool


def ok() -> EmptyResult:
    return EmptyResult(result=True)
