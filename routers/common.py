import json
import logging

from fastapi import APIRouter, status
from fastapi.params import Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from models.globals import GeneralMessenger, MeasurementState, NetworkSingleton, get_measurement_state, \
    get_messenger, get_trident_client
from models.models import SystemStateModel
from models.trident import StorageClient
from scripts.file_handling import get_disk_space_in_gb

router = APIRouter(
    tags=["General"]
)

logger = logging.getLogger(__name__)

@router.get("/state", status_code=status.HTTP_200_OK)
def state(measurement_state: MeasurementState = Depends(get_measurement_state), storage: StorageClient = Depends(get_trident_client)) -> SystemStateModel:
    return SystemStateModel(
        can_ready=NetworkSingleton.has_instance(),
        disk_capacity=get_disk_space_in_gb(),
        measurement_status=measurement_state.get_status(),
        cloud_status=storage.is_authenticated()
    )


@router.put("/reset-can", status_code=status.HTTP_200_OK)
async def reset_can():
    await NetworkSingleton.close_instance()
    await NetworkSingleton.create_instance_if_none()


@router.websocket("/state")
async def state_websocket(
        websocket: WebSocket,
        messenger: GeneralMessenger = Depends(get_messenger),
        measurement_state: MeasurementState = Depends(get_measurement_state),
        storage: StorageClient = Depends(get_trident_client)
):
    await websocket.accept()
    messenger.add_messenger(websocket)
    logger.info(f"Client accepted for state websocket.")

    try:
        # Initial send of data on connect
        await websocket.send_json(SystemStateModel(
            can_ready=NetworkSingleton.has_instance(),
            disk_capacity=get_disk_space_in_gb(),
            measurement_status=measurement_state.get_status(),
            cloud_status=storage.is_authenticated()
        ).model_dump())
        while True:
            command = await websocket.receive_text()
            if command == "get_state":
                await websocket.send_json(SystemStateModel(
                    can_ready=NetworkSingleton.has_instance(),
                    disk_capacity=get_disk_space_in_gb(),
                    measurement_status=measurement_state.get_status(),
                    cloud_status=storage.is_authenticated()
                ).model_dump())
                logger.info("Sent state information data to client upon request.")
    except WebSocketDisconnect:
        try:
            messenger.remove_messenger(websocket)
            logger.info(f"Client disconnected from measurement stream - now {len(measurement_state.clients)} clients")
        except ValueError:
            logger.debug(f"Client was already disconnected - still {len(measurement_state.clients)} clients")