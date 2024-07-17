from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from ..types.types import STHDevice

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    responses={404: {"description": "Not found"}},
)

mock_data: list[STHDevice] = [
    STHDevice(id=1, name='STH 1', mac='AA:BB:CC:DD:EE:FF', rssi=0 ,regex_str='^[\x20-\x7E]{1,29}[^\\s]$'),
    STHDevice(id=2, name='Messerkopf', mac='AA:00:CC:DD:EE:FF', rssi=0 ,regex_str='^[\x20-\x7E]{1,29}[^\\s]$'),
    STHDevice(id=2, name='Mini Mill', mac='DD:00:CC:DD:EE:FF', rssi=0 ,regex_str='^[\x20-\x7E]{1,29}[^\\s]$'),
]


@router.get('/', response_model=list[STHDevice])
async def index() -> list[STHDevice]:
    return mock_data
