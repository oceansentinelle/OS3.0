#!/usr/bin/env python3
"""
Station measurement endpoints for Ocean Sentinel.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()

db_pool = None


class StationParameter(BaseModel):
    """Dashboard-compatible latest value for one parameter."""

    name: str
    value: float
    unit: str
    status: Optional[str] = None
    source: Optional[str] = None
    timestamp: datetime
    quality_score: Optional[float] = None
    is_critical: bool = False


class StationLatestMeasurement(BaseModel):
    """Latest validated measurement snapshot for one station."""

    time: datetime = Field(..., description="Timestamp of the latest validated sample")
    timestamp: datetime = Field(..., description="Alias of time for dashboard compatibility")
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
    parameters: List[StationParameter] = Field(default_factory=list, description="Dashboard parameters")


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
                    WITH variable_map AS (
                        SELECT *
                        FROM (
                            VALUES
                                ('temperature_water', ARRAY['TEMP', 'temperature_water', 'temperature']::text[], 'TEMP'),
                                ('salinity', ARRAY['PSAL', 'salinity']::text[], 'PSAL'),
                                ('conductivity', ARRAY['conductivity']::text[], NULL),
                                ('pressure_water', ARRAY['pressure_water', 'pressure']::text[], NULL),
                                ('depth', ARRAY['depth']::text[], NULL),
                                ('dissolved_oxygen', ARRAY['DOX2', 'dissolved_oxygen', 'oxygen']::text[], 'DOX2'),
                                ('ph', ARRAY['PH_TOTAL', 'ph']::text[], 'PH_TOTAL'),
                                ('turbidity', ARRAY['turbidity']::text[], NULL),
                                ('chlorophyll_a', ARRAY['chlorophyll_a', 'chlorophyll', 'CHLA']::text[], NULL)
                        ) AS mapped(field_name, variables, parameter_name)
                    ),
                    latest_per_variable AS (
                        SELECT
                            mapped.field_name,
                            mapped.parameter_name,
                            vm.timestamp_utc,
                            vm.station_id,
                            vm.value,
                            vm.unit,
                            vm.quality_score,
                            vm.validation_status,
                            vm.data_status,
                            vm.data_source,
                            ROW_NUMBER() OVER (
                                PARTITION BY mapped.field_name
                                ORDER BY vm.timestamp_utc DESC, vm.processed_at DESC
                            ) AS row_number
                        FROM public.validated_measurements vm
                        JOIN variable_map mapped
                          ON vm.variable = ANY(mapped.variables)
                        WHERE vm.station_id = %s
                    ),
                    latest_values AS (
                        SELECT *
                        FROM latest_per_variable
                        WHERE row_number = 1
                    )
                    SELECT
                        MAX(timestamp_utc) AS time,
                        %s AS station_id,
                        MAX(value) FILTER (WHERE field_name = 'temperature_water') AS temperature_water,
                        MAX(value) FILTER (WHERE field_name = 'salinity') AS salinity,
                        MAX(value) FILTER (WHERE field_name = 'conductivity') AS conductivity,
                        MAX(value) FILTER (WHERE field_name = 'pressure_water') AS pressure_water,
                        MAX(value) FILTER (WHERE field_name = 'depth') AS depth,
                        MAX(value) FILTER (WHERE field_name = 'dissolved_oxygen') AS dissolved_oxygen,
                        MAX(value) FILTER (WHERE field_name = 'ph') AS ph,
                        MAX(value) FILTER (WHERE field_name = 'turbidity') AS turbidity,
                        MAX(value) FILTER (WHERE field_name = 'chlorophyll_a') AS chlorophyll_a,
                        AVG(quality_score) AS quality_score,
                        MAX(validation_status) AS validation_status,
                        MAX(data_status) AS data_status,
                        MAX(data_source) AS data_source,
                        COALESCE(
                            jsonb_agg(
                                jsonb_build_object(
                                    'name', parameter_name,
                                    'value', value,
                                    'unit', unit,
                                    'status', validation_status,
                                    'source', data_source,
                                    'timestamp', timestamp_utc,
                                    'quality_score', quality_score,
                                    'is_critical',
                                        CASE
                                            WHEN parameter_name = 'DOX2' AND value < 150 THEN TRUE
                                            WHEN parameter_name = 'PH_TOTAL' AND value < 7.80 THEN TRUE
                                            WHEN parameter_name = 'TEMP' AND value > 25 THEN TRUE
                                            ELSE FALSE
                                        END
                                )
                                ORDER BY parameter_name
                            ) FILTER (WHERE parameter_name IS NOT NULL),
                            '[]'::jsonb
                        ) AS parameters
                    FROM latest_values;
                    """,
                    (station_id, station_id),
                )

                result = cursor.fetchone()
                if result and result.get("time") is not None:
                    response = dict(result)
                    response.setdefault("timestamp", response["time"])
                    response.setdefault("parameters", [])
                    return StationLatestMeasurement(**response)

                raise HTTPException(
                    status_code=404,
                    detail=f"No validated data found for station {station_id}",
                )
        finally:
            db_pool.putconn(conn)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching latest station measurement: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")
