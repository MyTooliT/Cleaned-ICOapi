# -- Imports ------------------------------------------------------------------

from pytest import mark

# -- Classes ------------------------------------------------------------------


@mark.usefixtures("anyio_backend")
class TestSTU:

    async def test_root(self, measurement_prefix, client) -> None:
        """Test endpoint ``/``"""

        response = await client.get(str(measurement_prefix))
        assert response.status_code == 200

        body = response.json()

        for key in (
            "instructions",
            "name",
            "running",
            "start_time",
            "tool_name",
        ):
            assert key in body

    async def test_start(self, measurement_prefix, client) -> None:
        """Test endpoint ``/start``"""

        # =======================
        # = Test Error Response =
        # =======================

        response = await client.post(str(measurement_prefix / "start"))
        assert response.status_code == 422
