import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.responses import Response

from models.models import LogResponse
from utils.logging_setup import log_watchers, LOG_PATH

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)

@router.get("", response_model=LogResponse)
def get_logs(limit: int = 500):
    with open(LOG_PATH, "r") as f:
        lines = f.readlines()
    return LogResponse(
        path=LOG_PATH,
        logs="".join(lines[-limit:]),
        max_bytes=int(os.getenv("LOG_MAX_BYTES"), 0),
        backup_count=int(os.getenv("LOG_BACKUP_COUNT"), 0)
    )

@router.get("/download")
def download_logs():
    with open(LOG_PATH, "rb") as f:
        content = f.read()
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=icogui.log"}
    )

@router.websocket("/stream")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    log_watchers.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        log_watchers.remove(websocket)