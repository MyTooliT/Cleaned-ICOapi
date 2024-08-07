from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Body, Request
from fastapi.responses import JSONResponse, Response
from ..models.models import STHDeviceResponseModel, STUDeviceResponseModel
from ..scripts.sth import get_sth_devices_from_network
from ..scripts.stu import get_stu_devices, reset_stu, enable_ota, disable_ota
from ..scripts.errors import NoResponseError

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


@router.options('/stu/reset')
def options():
    return


@router.put(
    '/stu/reset',
    response_model=None | NoResponseError,
    status_code=status.HTTP_502_BAD_GATEWAY,
    responses={
        204: {
            "description": "Device was successfully reset."
        },
        502: {
            "content": "application/json",
            "description": "The CAN Network did not respond. This can either be because the Node is not connected, "
                           "or the Network is unresponsive."
        }
    },
)
async def stu_reset(name: Annotated[str, Body(embed=True)], response: Response) -> None | NoResponseError:
    if await reset_stu(name):
        response.status_code = status.HTTP_204_NO_CONTENT
    else:
        response.status_code = status.HTTP_502_BAD_GATEWAY
        return NoResponseError()


@router.put('/stu/ota/enable')
async def stu_enable_ota(name: Annotated[str, Body(embed=True)], response: Response) -> None | NoResponseError:
    if await enable_ota(name):
        response.status_code = status.HTTP_204_NO_CONTENT
        return None
    else:
        response.status_code = status.HTTP_502_BAD_GATEWAY
        return NoResponseError()


@router.put('/stu/ota/disable')
async def stu_disable_ota(name: Annotated[str, Body(embed=True)], response: Response) -> None | NoResponseError:
    if await disable_ota(name):
        response.status_code = status.HTTP_204_NO_CONTENT
        return None
    else:
        response.status_code = status.HTTP_502_BAD_GATEWAY
        return NoResponseError()