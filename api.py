from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket
from contextlib import asynccontextmanager
from mytoolit.can.network import Network

from .config import Settings
from .routers import stu_routes, sth_routes, common, websockets
from .models.GlobalNetwork import NetworkSingleton

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This function handles startup and shutdown of the API.
    Anything before <yield> will be run on startup; everything after on shutdown.
    See https://fastapi.tiangolo.com/advanced/events/#lifespan
    """
    await NetworkSingleton.create_instance_if_none()
    yield
    await NetworkSingleton.close_instance()

app = FastAPI(lifespan=lifespan)
app.include_router(prefix='/api/v1', router=stu_routes.router)
app.include_router(prefix='/api/v1', router=sth_routes.router)
app.include_router(prefix='/api/v1', router=common.router)
app.include_router(prefix='', router=websockets.router)

origins = [
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.websocket("/live")
async def live_websocket(websocket: WebSocket):
    await websocket.accept()


if __name__ == "__main__":
    import asyncio
    import uvicorn

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    event_loop.run_until_complete(uvicorn.run(app, host=settings.HOST, port=settings.PORT)) # type: ignore[func-returns-value]
