from pydantic import BaseModel


class Error(BaseModel):
    name: str
    message: str


class NoResponseError(Error):
    def __init__(self):
        super().__init__(
            name="NoResponseError",
            message="CAN Network did not respond."
        )


class ConnectionTimeoutError(Error):
    def __init__(self):
        super().__init__(
            name="ConnectionTimeoutError",
            message="STH was not reachable."
        )