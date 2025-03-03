from fastapi import APIRouter, status
from fastapi.params import Depends

from models.globals import MeasurementState, NetworkSingleton, get_measurement_state
from models.models import APIStateModel
from scripts.file_handling import get_disk_space_in_gb

router = APIRouter()


@router.get("/ping", status_code=status.HTTP_200_OK)
def ping(measurement_state: MeasurementState = Depends(get_measurement_state())) -> APIStateModel:
    return APIStateModel(
        can_ready=NetworkSingleton.has_instance(),
        disk_capacity=get_disk_space_in_gb(),
        measurement_status=measurement_state.get_status()
    )


@router.put("/reset-can", status_code=status.HTTP_200_OK)
async def reset_can():
    await NetworkSingleton.close_instance()
    await NetworkSingleton.create_instance_if_none()
