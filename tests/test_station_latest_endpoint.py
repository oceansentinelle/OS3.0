from datetime import datetime, timezone

from fastapi.testclient import TestClient

from api.main import app
from api.routes import station_endpoint


class FakeCursor:
    def __init__(self, responses):
        self.responses = list(responses)
        self.queries = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def fetchone(self):
        return self.responses.pop(0)


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor

    def cursor(self, cursor_factory=None):
        return self.cursor_instance


class FakePool:
    def __init__(self, responses):
        self.cursor = FakeCursor(responses)
        self.connection = FakeConnection(self.cursor)
        self.returned = False

    def getconn(self):
        return self.connection

    def putconn(self, conn):
        self.returned = True


def make_client(responses):
    pool = FakePool(responses)
    station_endpoint.set_db_pool(pool)
    return TestClient(app), pool


def test_station_latest_returns_existing_station_data():
    timestamp = datetime(2026, 4, 26, 12, 0, tzinfo=timezone.utc)
    client, pool = make_client(
        [
            {
                "time": timestamp,
                "station_id": "BARAG",
                "temperature_water": 15.2,
                "salinity": 35.1,
                "conductivity": None,
                "pressure_water": None,
                "depth": None,
                "dissolved_oxygen": 250.0,
                "ph": 8.1,
                "turbidity": None,
                "chlorophyll_a": None,
                "quality_score": 0.98,
                "validation_status": "valid",
                "data_status": "measured",
                "data_source": "COAST-HF",
            }
        ]
    )

    response = client.get("/api/v1/station/BARAG/latest")

    assert response.status_code == 200
    assert pool.returned is True
    assert "public.validated_measurements" in pool.cursor.queries[0][0]
    assert response.json()["station_id"] == "BARAG"
    assert response.json()["temperature_water"] == 15.2


def test_station_latest_returns_404_for_absent_station():
    client, _ = make_client([None, {"station_known": False}])

    response = client.get("/api/v1/station/UNKNOWN/latest")

    assert response.status_code == 404
    assert response.json() == {"detail": "Station UNKNOWN not found"}


def test_station_latest_returns_404_when_station_has_no_validated_data():
    client, _ = make_client([None, {"station_known": True}])

    response = client.get("/api/v1/station/BARAG/latest")

    assert response.status_code == 404
    assert response.json() == {"detail": "No validated data found for station BARAG"}


def test_station_latest_json_schema_contains_expected_fields():
    schema = app.openapi()["paths"]["/api/v1/station/{station_id}/latest"]["get"]

    assert schema["responses"]["200"]["description"] == "Successful Response"
    assert schema["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "StationLatestMeasurement"
    )
