# -- Imports ------------------------------------------------------------------

from netaddr import EUI
from pytest import mark

# -- Globals ------------------------------------------------------------------

sth_prefix = "/api/v1/sth"

# -- Tests --------------------------------------------------------------------


@mark.anyio
async def test_root(client) -> None:
    """Test endpoint ``/``"""

    response = await client.get(sth_prefix)

    assert response.status_code == 200
    sensor_devices = response.json()
    # We assume that at least one sensor device is available
    assert len(sensor_devices) >= 1

    sensor_device = sensor_devices[0]
    assert sensor_device["device_number"] == 0
    mac_address = sensor_device["mac_address"]
    # Check that MAC address is valid and assert that it is equal to (the
    # string representation) of itself
    assert EUI(mac_address) == mac_address
    assert len(sensor_device["name"]) <= 8
    assert 0 >= sensor_device["rssi"] >= -80
