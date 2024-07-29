from fastapi import APIRouter
from ..types.types import STHDeviceResponseModel
from ..scripts.sth_devices import get_sth_devices_from_network

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    responses={404: {"description": "Not found"}},
)


@router.get('/')
async def index() -> list[STHDeviceResponseModel]:
    devices = await get_sth_devices_from_network()
    return [STHDeviceResponseModel.from_network(device) for device in devices]
