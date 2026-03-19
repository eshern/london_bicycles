"""
Dagster assets and jobs for London Bicycles ELT pipeline
Integrates Meltano tap-target-dbt jobs with Dagster orchestration
Run with: dagster dev
"""

import os
import subprocess
from dagster import (
    asset,
    job,
    op,
    get_dagster_logger,
    Definitions,
    graph,
    in_process_executor,
    config,
    define_asset_job,
)


@op
def run_meltano_extract_load() -> str:
    """
    Run Meltano extract-load job: tap-bigquery target-bigquery
    Extracts data from BigQuery and loads to london_bicycles_raw dataset
    """
    logger = get_dagster_logger()
    logger.info("Starting Meltano extract-load job...")
    
    try:
        result = subprocess.run(
            ["meltano", "run", "extract-load"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✓ Meltano extract-load completed successfully\n{result.stdout}")
        return "extract_load_completed"
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Meltano extract-load failed: {e.stderr}")
        raise


@op
def run_dbt_transform(extract_load_status: str) -> str:
    """
    Run dbt transformation: dbt run + dbt test
    Transforms raw data into staging and mart models
    Depends on: run_meltano_extract_load
    """
    logger = get_dagster_logger()
    logger.info("Starting dbt transformation...")
    
    try:
        result = subprocess.run(
            ["meltano", "run", "dbt-bigquery:run", "dbt-bigquery:test"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✓ dbt transformation completed successfully\n{result.stdout}")
        return "transform_completed"
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ dbt transformation failed: {e.stderr}")
        raise


@op
def run_great_expectations_validation(transform_status: str) -> str:
    """
    Run Great Expectations data quality validations
    Validates all staging and mart layer tables
    Depends on: run_dbt_transform
    """
    logger = get_dagster_logger()
    logger.info("Starting Great Expectations validations...")
    
    try:
        result = subprocess.run(
            ["python", "great_expectations_validator.py"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✓ Great Expectations validations completed\n{result.stdout}")
        return "validation_completed"
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Great Expectations validations failed: {e.stderr}")
        raise


@graph
def london_bicycles_elt_pipeline():
    """
    Complete ELT pipeline orchestration with Dagster:
    1. Extract & Load (Meltano): BigQuery → london_bicycles_raw
    2. Transform (dbt): Raw → Staging → Marts
    3. Validate (Great Expectations): Data quality checks
    """
    extract_load_status = run_meltano_extract_load()
    transform_status = run_dbt_transform(extract_load_status)
    validation_status = run_great_expectations_validation(transform_status)
    return validation_status


# Create job from graph with in-process executor for local development
london_bicycles_elt_job = london_bicycles_elt_pipeline.to_job(
    name="london_bicycles_full_elt",
    description="Complete ELT pipeline: Extract, Load, Transform, Validate",
    executor_def=in_process_executor,
)


@asset
def london_bicycles_staging_trips():
    """
    Asset: Staging trips data
    Source: london_bicycles_staging.stg_trips
    Updated: During dbt transformation step
    """
    return "london_bicycles_staging.stg_trips"


@asset
def london_bicycles_staging_stations():
    """
    Asset: Staging stations data
    Source: london_bicycles_staging.stg_stations
    Updated: During dbt transformation step
    """
    return "london_bicycles_staging.stg_stations"


@asset
def london_bicycles_fact_trips():
    """
    Asset: Fact trips table (mart layer)
    Source: london_bicycles_marts.fct_trips
    Contains: Trip facts with enriched station information
    """
    return "london_bicycles_marts.fct_trips"


@asset
def london_bicycles_dim_stations():
    """
    Asset: Dimension stations table (mart layer)
    Source: london_bicycles_marts.dim_stations
    Contains: Station master dimension
    """
    return "london_bicycles_marts.dim_stations"


@asset
def london_bicycles_kpi_seasonal():
    """
    Asset: KPI - Seasonal trips analysis (mart layer)
    Source: london_bicycles_marts.seasonal_trips
    Contains: Monthly trip trends, subscriber/casual breakdown
    """
    return "london_bicycles_marts.seasonal_trips"


@asset
def london_bicycles_kpi_station_volume():
    """
    Asset: KPI - Station trip volume ranking (mart layer)
    Source: london_bicycles_marts.station_trip_volume
    Contains: High-volume station metrics and rankings
    """
    return "london_bicycles_marts.station_trip_volume"


@asset
def london_bicycles_kpi_quarterly_area():
    """
    Asset: KPI - Quarterly geographic analysis (mart layer)
    Source: london_bicycles_marts.quarterly_area_analysis
    Contains: Regional trends by user type and quarter
    """
    return "london_bicycles_marts.quarterly_area_analysis"


# Define asset jobs with in_process_executor to prevent SQLite locking
# These jobs are used when materializing assets from the Dagster UI
staging_asset_job = define_asset_job(
    "staging_assets_job",
    selection=["london_bicycles_staging_trips", "london_bicycles_staging_stations"],
    executor_def=in_process_executor,
    description="Materialize staging layer assets",
)

marts_asset_job = define_asset_job(
    "marts_assets_job",
    selection=[
        "london_bicycles_fact_trips",
        "london_bicycles_dim_stations",
        "london_bicycles_kpi_seasonal",
        "london_bicycles_kpi_station_volume",
        "london_bicycles_kpi_quarterly_area",
    ],
    executor_def=in_process_executor,
    description="Materialize mart layer assets",
)

all_assets_job = define_asset_job(
    "all_assets_job",
    executor_def=in_process_executor,
    description="Materialize all assets",
)


defs = Definitions(
    jobs=[
        london_bicycles_elt_job,
        staging_asset_job,
        marts_asset_job,
        all_assets_job,
    ],
    assets=[
        london_bicycles_staging_trips,
        london_bicycles_staging_stations,
        london_bicycles_fact_trips,
        london_bicycles_dim_stations,
        london_bicycles_kpi_seasonal,
        london_bicycles_kpi_station_volume,
        london_bicycles_kpi_quarterly_area,
    ],
)
