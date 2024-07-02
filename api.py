from fastapi import FastAPI, status
from config import Settings

settings = Settings()

app = FastAPI()

@app.get("/ping", status_code=status.HTTP_200_OK)
def ping():
    return "OK"

if __name__ == "__main__":
    import asyncio
    import uvicorn

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    event_loop.run_until_complete(uvicorn.run(app, host=settings.HOST, port=settings.PORT)) # type: ignore[func-returns-value]
