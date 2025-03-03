import asyncio
import datetime

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from models.models import MeasurementStatus, ControlResponse, MeasurementInstructions
from models.globals import get_network, get_measurement_state, MeasurementState, Network
from scripts.measurement import run_measurement

router = APIRouter()

@router.post("/start", response_model=ControlResponse)
async def start_measurement(
        instructions: MeasurementInstructions,
        network: Network = Depends(get_network),
        measurement_state: MeasurementState = Depends(get_measurement_state)
):
    if measurement_state.running:
        return ControlResponse(message="Measurement is already running.")

    measurement_state.running = True
    measurement_state.name = instructions.name if instructions.name else datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    measurement_state.start_time = datetime.datetime.now().isoformat()
    measurement_state.task = asyncio.create_task(run_measurement(network, instructions, measurement_state))

    return ControlResponse(message="Measurement started successfully.")


@router.post("/stop", response_model=ControlResponse)
async def stop_measurement(measurement_state: MeasurementState = Depends(get_measurement_state)):
    if not measurement_state.running:
        return ControlResponse(message="No active measurement to stop.")

    measurement_state.running = False
    if measurement_state.task:
        measurement_state.task.cancel()
    return ControlResponse(message="Measurement stopped successfully.")


@router.get("", response_model=MeasurementStatus)
async def measurement_status(measurement_state: MeasurementState = Depends(get_measurement_state)):
    return MeasurementStatus(
        running=measurement_state.running,
        name=measurement_state.name if measurement_state.running else None,
        start_time=measurement_state.start_time if measurement_state.running else None
    )


@router.websocket("/stream")
async def websocket_endpoint(
        websocket: WebSocket,
        measurement_state: MeasurementState = Depends(get_measurement_state),
):
    await websocket.accept()
    measurement_state.clients.append(websocket)
    print(f"Client connected! {len(measurement_state.clients)} clients")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        measurement_state.clients.remove(websocket)
        print(f"Client disconnected! {len(measurement_state.clients)} clients")
