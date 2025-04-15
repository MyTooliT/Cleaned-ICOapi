import logging
import os
import platform
from pathlib import Path
from dotenv import load_dotenv
from typing import List
from fastapi import WebSocket
import asyncio
import sys
import orjson
from colorlog import ColoredFormatter
from logging.handlers import RotatingFileHandler

log_watchers: List[WebSocket] = []
log_queue: asyncio.Queue[str] = asyncio.Queue()

load_dotenv(".env")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_USE_JSON = os.getenv("LOG_USE_JSON", "0") == "1"
LOG_USE_COLOR = os.getenv("LOG_USE_COLOR", "0") == "1"
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 5 * 1024 * 1024))  # 5 MB default
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

def get_default_log_path() -> str:
    app_folder = "icogui"
    file_name = "icogui.log"
    if platform.system() == "Windows":
        base = os.getenv("LOCALAPPDATA", str(Path.home()))
    else:
        base = os.path.join(Path.home(), ".local", "share")
    log_dir = os.path.join(base, app_folder, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, file_name)

LOG_PATH = os.getenv("LOG_PATH", get_default_log_path())

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return orjson.dumps(log_data).decode("utf-8")

class WebSocketLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            message = self.format(record)
            log_queue.put_nowait(message)
        except Exception:
            pass

async def log_broadcaster():
    while True:
        message = await log_queue.get()
        for ws in list(log_watchers):
            try:
                await ws.send_text(message)
            except Exception:
                log_watchers.remove(ws)

def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    if LOG_USE_JSON:
        formatter = JSONFormatter()
    elif LOG_USE_COLOR:
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
        )

    file_handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    ws_handler = WebSocketLogHandler()
    ws_handler.setFormatter(formatter)

    for h in [file_handler, console_handler, ws_handler]:
        root_logger.addHandler(h)

    logging.getLogger("uvicorn").handlers.clear()
    logging.getLogger("uvicorn.error").handlers.clear()
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn").propagate = True
    logging.getLogger("uvicorn.error").propagate = True
    logging.getLogger("uvicorn.access").propagate = True

    logging.getLogger("uvicorn").setLevel(LOG_LEVEL)
    logging.getLogger("uvicorn.error").setLevel(LOG_LEVEL)
    logging.getLogger("uvicorn.access").setLevel(LOG_LEVEL)
