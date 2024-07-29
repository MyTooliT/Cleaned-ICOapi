from fastapi import APIRouter, status, HTTPException
from mytoolit.can.network import NoResponseError
from ..types.types import STHDeviceResponseModel
from ..scripts.sth import get_sth_devices_from_network
from ..scripts.stu import get_stu_status, get_stu_mac

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    responses={404: {"description": "Not found"}},
)


@router.get('/sth', status_code=status.HTTP_200_OK)
async def sth() -> list[STHDeviceResponseModel]:
    devices = await get_sth_devices_from_network()
    return [STHDeviceResponseModel.from_network(device) for device in devices]


@router.get('/stu/alive/{nr}', status_code=status.HTTP_200_OK)
async def stu_alive(nr) -> bool:
    try:
        await get_stu_status(f'STU {nr}')
        return True
    except NoResponseError:
        raise HTTPException(status_code=404, detail=f'STU {nr} not connected')


@router.get('/stu/mac/{nr}', status_code=status.HTTP_200_OK)
async def stu_mac(nr) -> str:
    try:
        mac_eui = await get_stu_mac(f'STU {nr}')
        return mac_eui.format()
    except NoResponseError:
        raise HTTPException(status_code=404, detail=f'STU {nr} not connected')