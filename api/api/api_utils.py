from pydantic.main import BaseModel


class ErrorMessage(BaseModel):
    detail: str


class EmptyResult(BaseModel):
    result: bool


def ok_result() -> EmptyResult:
    return EmptyResult(result=True)
