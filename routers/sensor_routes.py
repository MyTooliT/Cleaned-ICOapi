from typing import List

from fastapi import APIRouter, HTTPException, status

from models.models import Sensor
from scripts.data_handling import get_sensor_defaults, get_sensors, write_sensor_defaults

router = APIRouter(
    prefix="/sensor",
    tags=["Sensor"]
)

@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=List[Sensor],
    responses={
        200: {
            "content": "application/json",
            "description": "Available sensors for platform."
        },
        500: {
            "content": "application/json",
            "description": "Can't find sensor declaration."
        }
    }
)
def query_sensors():
    return get_sensors()


@router.post('reset')
def reset_sensors_to_default() -> None:
    default_sensors = get_sensor_defaults()
    try:
        write_sensor_defaults(default_sensors)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))