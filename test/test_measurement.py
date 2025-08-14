# -- Classes ------------------------------------------------------------------


class TestMeasurement:

    def test_root(self, measurement_prefix, client) -> None:
        """Test endpoint ``/``"""

        measurement_status = measurement_prefix

        response = client.get(measurement_status)
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

    def test_start(self, connect, measurement_prefix, client) -> None:
        """Test endpoint ``/start``"""

        node = connect

        measurement_status = measurement_prefix
        start = f"{measurement_prefix}/start"
        stop = f"{measurement_prefix}/stop"

        adc_config = {
            "prescaler": 2,
            "acquisition_time": 8,
            "oversampling_rate": 64,
            "reference_voltage": 3.3,
        }
        sensor = {
            "channel_number": 1,
            "sensor_id": "acc100g_01",
        }
        disabled = {
            "channel_number": 0,
            "sensor_id": "",
        }

        # ========================
        # = Test Normal Response =
        # ========================

        response = client.post(
            start,
            json={
                "name": node["name"],
                "mac": node["mac_address"],
                "time": 10,
                "first": sensor,
                "second": disabled,
                "third": disabled,
                "ift_requested": False,
                "ift_channel": "",
                "ift_window_width": 0,
                "adc": adc_config,
                "meta": {"version": "", "profile": "", "parameters": {}},
            },
        )
        assert response.status_code == 200

        assert (
            response.json()["message"] == "Measurement started successfully."
        )

        response = client.get(measurement_status)
        assert response.status_code == 200
        body = response.json()
        instructions = body["instructions"]
        assert instructions["adc"] == adc_config
        assert instructions["first"] == sensor

        response = client.post(stop)

        # =======================
        # = Test Error Response =
        # =======================

        response = client.post(start)
        assert response.status_code == 422

    def test_stream(self, measurement, measurement_prefix, client) -> None:
        """Check WebSocket streaming data"""

        measurement

        measurement_status = str(measurement_prefix)

        response = client.get(measurement_status)
        assert response.status_code == 200
        assert response.json()["running"] is True

        ws_url = str(client.base_url).replace("http", "ws")
        stream = f"{ws_url}{measurement_prefix}/stream"

        with client.websocket_connect(stream) as websocket:
            data = websocket.receive_json()
            assert isinstance(data, list)
            assert len(data) >= 1
            message = data[0]
            for key in (
                "timestamp",
                "first",
                "second",
                "third",
                "ift",
                "counter",
                "dataloss",
            ):
                assert key in message
            assert message["timestamp"] >= 0
            assert -100 <= message["first"] <= 100
            assert message["second"] is None
            assert message["third"] is None
            assert 0 <= message["counter"] <= 255
            assert message["ift"] is None
