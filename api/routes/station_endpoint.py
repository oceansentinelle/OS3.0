#!/usr/bin/env python3
"""
Station measurement endpoints for Ocean Sentinel.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

db_pool = None


class StationLatestMeasurement(BaseModel):
    """Latest validated measurement snapshot for one station."""

    time: datetime = Field(..., description="Timestamp of the latest validated sample")
    station_id: str = Field(..., description="Station identifier")
    temperature_water: Optional[float] = Field(None, description="Water temperature")
    salinity: Optional[float] = Field(None, description="Practical salinity")
    conductivity: Optional[float] = Field(None, description="Conductivity")
    pressure_water: Optional[float] = Field(None, description="Water pressure")
    depth: Optional[float] = Field(None, description="Depth")
    dissolved_oxygen: Optional[float] = Field(None, description="Dissolved oxygen")
    ph: Optional[float] = Field(None, description="pH")
    turbidity: Optional[float] = Field(None, description="Turbidity")
    chlorophyll_a: Optional[float] = Field(None, description="Chlorophyll-a")
    quality_score: Optional[float] = Field(None, description="Average quality score")
    validation_status: Optional[str] = Field(None, description="Validation status")
    data_status: Optional[str] = Field(None, description="Data status")
    data_source: Optional[str] = Field(None, description="Data source")


def set_db_pool(pool):
    """Inject the application database pool."""
    global db_pool
    db_pool = pool


@router.get(
    "/station/{station_id}/latest",
    response_model=StationLatestMeasurement,
    tags=["Measurements"],
)
async def get_station_latest(station_id: str):
    """
    Return the latest validated measurement snapshot for a station.
    """
    if db_pool is None:
        raise HTTPException(status_code=503, detail="Database pool unavailable")

    try:
        conn = db_pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    WITH latest_timestamp AS (
                        SELECT timestamp_utc
                        FROM public.validated_measurements
                        WHERE station_id = %s
                        ORDER BY timestamp_utc DESC
                        LIMIT 1
                    )
                    SELECT
                        vm.timestamp_utc AS time,
                        vm.station_id,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable IN ('temperature_water', 'temperature', 'TEMP')
                        ) AS temperature_water,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable IN ('salinity', 'PSAL')
                        ) AS salinity,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable = 'conductivity'
                        ) AS conductivity,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable IN ('pressure_water', 'pressure')
                        ) AS pressure_water,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable = 'depth'
                        ) AS depth,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable IN ('dissolved_oxygen', 'oxygen', 'DOX2')
                        ) AS dissolved_oxygen,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable IN ('ph', 'PH_TOTAL')
                        ) AS ph,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable = 'turbidity'
                        ) AS turbidity,
                        MAX(vm.value) FILTER (
                            WHERE vm.variable IN ('chlorophyll_a', 'chlorophyll', 'CHLA')
                        ) AS chlorophyll_a,
                        AVG(vm.quality_score) AS quality_score,
                        MAX(vm.validation_status) AS validation_status,
                        MAX(vm.data_status) AS data_status,
                        MAX(vm.data_source) AS data_source
                    FROM public.validated_measurements vm
                    JOIN latest_timestamp lt
                      ON lt.timestamp_utc = vm.timestamp_utc
                    WHERE vm.station_id = %s
                    GROUP BY vm.timestamp_utc, vm.station_id
                    LIMIT 1;
                    """,
                    (station_id, station_id),
                )

                result = cursor.fetchone()
                if result:
                    return StationLatestMeasurement(**dict(result))

                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1 FROM public.raw_measurements WHERE station_id = %s
                        UNION ALL
                        SELECT 1 FROM public.data_quality_reports WHERE station_id = %s
                        UNION ALL
                        SELECT 1 FROM public.forecast_predictions WHERE station_id = %s
                        UNION ALL
                        SELECT 1 FROM public.alerts WHERE station_id = %s
                    ) AS station_known;
                    """,
                    (station_id, station_id, station_id, station_id),
                )
                station_row = cursor.fetchone()
                station_known = bool(station_row and station_row.get("station_known"))
                detail = (
                    f"No validated data found for station {station_id}"
                    if station_known
                    else f"Station {station_id} not found"
                )
                raise HTTPException(status_code=404, detail=detail)
        finally:
            db_pool.putconn(conn)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching latest station measurement: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")
