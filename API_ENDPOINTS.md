# Ocean Sentinel API Endpoints

Status: NO-GO PRODUCTION maintained. This document lists the endpoints currently exposed by the local FastAPI application only.

## Root and health

- `GET /` - API metadata and endpoint index.
- `GET /health` - legacy API/database health check.
- `GET /api/v1/health` - lightweight service health check.
- `GET /api/v1/pipeline/status` - pipeline status backed by PostgreSQL.

## Measurements

- `GET /api/v1/station/{station_id}/latest` - official latest station measurement endpoint. Reads from `public.validated_measurements` and returns:
  - `200` when at least one validated measurement exists for the station;
  - `404` when no validated measurement exists for the requested station.
- `GET /api/v1/station/{station_id}/history` - historical station measurements endpoint currently backed by the legacy `barag.sensor_data` query.

No `/api/v1/stations` or `/api/v1/alerts/sacs` endpoint is exposed in this API baseline.
