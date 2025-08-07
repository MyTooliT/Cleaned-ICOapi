# -- Imports ------------------------------------------------------------------

from httpx import ASGITransport, AsyncClient
from netaddr import EUI
from pytest import fixture

from icoapi.api import app

# -- Fixtures -----------------------------------------------------------------


@fixture(scope="session")
def anyio_backend():
    return "asyncio"


@fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@fixture
async def connect(client):
    response = await client.get("/api/v1/sth")

    assert response.status_code == 200
    sensor_nodes = response.json()

    # We assume that a sensor device with the name `Test-STH` is available and
    # ready for connection
    node = None
    for sensor_node in sensor_nodes:
        if sensor_node["name"] == "Test-STH":
            node = sensor_node
            break
    assert node is not None
    mac_address = node["mac_address"]
    assert mac_address is not None
    assert EUI(mac_address)  # Check for valid MAC address

    mac_address = sensor_node["mac_address"]
    response = await client.put(
        "/api/v1/sth/connect", json={"mac": mac_address}
    )
    assert response.status_code == 200
    assert response.json() is None

    yield node

    await client.put("/api/v1/sth/disconnect")
