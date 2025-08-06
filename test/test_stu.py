# -- Imports ------------------------------------------------------------------

from netaddr import EUI
from pytest import mark

# -- Tests --------------------------------------------------------------------


@mark.usefixtures("anyio_backend")
class TestSTU:

    async def test_root(self, client, stu_prefix) -> None:
        """Test endpoint ``/``"""

        response = await client.get(stu_prefix)

        assert response.status_code == 200
        sth_response = response.json()[0]
        assert sth_response["device_number"] == 1
        mac_address = sth_response["mac_address"]
        # Check that MAC address is valid and assert that it is equal to (the
        # string representation) of itself
        assert EUI(mac_address) == mac_address
        assert sth_response["name"] == "STU 1"

    async def test_reset(self, client, stu_prefix) -> None:
        """Test endpoint ``/reset``"""

        response = await client.put(f"{stu_prefix}/reset")

        assert response.status_code == 200
        assert response.json() is None

    async def test_ota_enable(self, client, stu_prefix) -> None:
        """Test endpoint ``/ota/enable``"""

        response = await client.put(f"{stu_prefix}/ota/enable")

        assert response.status_code == 200
        assert response.json() is None

    async def test_ota_disable(self, client, stu_prefix) -> None:
        """Test endpoint ``/ota/disable``"""

        response = await client.put(f"{stu_prefix}/ota/disable")

        assert response.status_code == 200
        assert response.json() is None

    async def test_connected(self, client, stu_prefix) -> None:
        """Test endpoint ``/connected``"""

        response = await client.get(f"{stu_prefix}/connected")
        assert response.status_code == 200
        # STU is not connected to sensor device yet
        assert response.json() is False
