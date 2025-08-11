# -- Imports ------------------------------------------------------------------

from pytest import mark

# -- Tests --------------------------------------------------------------------


@mark.usefixtures("anyio_backend")
class TestGeneral:

    async def test_root(self, state_prefix, client) -> None:
        """Test endpoint ``/``"""

        response = await client.get(str(state_prefix))

        assert response.status_code == 200
        body = response.json()
        assert body["can_ready"] is True
