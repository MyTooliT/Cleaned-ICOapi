from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket

from .config import Settings
from .routers import stu_routes, sth_routes, common, websockets

settings = Settings()

app = FastAPI()
app.include_router(prefix='/api/v1', router=stu_routes.router)
app.include_router(prefix='/api/v1', router=sth_routes.router)
app.include_router(prefix='/api/v1', router=common.router)
app.mount('', websockets.router)

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
