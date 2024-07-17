from pydantic import BaseModel


class Device(BaseModel):
    id: int
    name: str
    mac: str


class STHDevice(Device):
    rssi: float
    regex_str: str


class STUDevice(Device):
    pass

