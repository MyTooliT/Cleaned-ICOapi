from pydantic import BaseModel


class Error(BaseModel):
    name: str
    message: str
    