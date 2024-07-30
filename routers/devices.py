from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse, Response
from ..models.models import STHDeviceResponseModel, STUDeviceResponseModel
from ..scripts.sth import get_sth_devices_from_network
from ..scripts.stu import get_stu_devices

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    '/sth', status_code=status.HTTP_200_OK)
async def sth() -> list[STHDeviceResponseModel]:
    devices = await get_sth_devices_from_network()
    return [STHDeviceResponseModel.from_network(device) for device in devices]


@router.get(
    '/stu',
    status_code=status.HTTP_200_OK,
    response_model=list[STUDeviceResponseModel],
    responses={
        200: {
            "content": "application/json",
            "description": "Return the STU Devices connected to the system"
        },
        204: {
            "content": "application/json",
            "description": "Indicates no STU Devices connected to the system"
        }
    },
)
async def stu(response: Response) -> list[STUDeviceResponseModel]:
    devices = await get_stu_devices()

    if len(devices) == 0:
        response.status_code = status.HTTP_204_NO_CONTENT

    return devices
