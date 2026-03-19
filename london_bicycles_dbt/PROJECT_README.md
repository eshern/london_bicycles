# London Bicycles Integrated ELT Pipeline with dbt, Meltano & Great Expectations

A comprehensive data pipeline for transforming and analyzing London Bicycles rental data from Google BigQuery using modern data engineering practices (ELT).

## Project Overview

This project implements a complete **Extract-Load-Transform (ELT)** architecture:
- **Extract & Load (Meltano)**: Leveraging `tap-bigquery` for extraction and `target-bigquery` for loading
- **Transform (dbt)**: Layered data modeling with staging, intermediate, and mart layers
- **Validate (Great Expectations)**: Data quality checks and assertions on all data layers

### Architecture

```
Raw BigQuery Data
     ↓ (Meltano - Extract/Load)
london_bicycles_raw (Landing Zone)
     ↓ (dbt - Transform)
Staging Layer (Views) → Intermediate Models
     ↓
Marts Layer (Tables) → Business-Ready Analytics
     ↓ (Great Expectations - Validate)
Data Quality Reports
```

## Configuration

### GCP Project Setup
- **Project ID**: `pydrive-colab-2`
- **Dataset**: `london_bicycles`
- **Location**: `EU`
- **Authentication**: OAuth (gcloud auth application-default login)

### Environment
- **Conda Environment**: `dagster`
- **Tools Installed**: 
  - dbt 1.9.6
  - Meltano (for EL)
  - Great Expectations (for data validation)

## Project Structure

```
london_bicycles/
├── meltano.yml                          # Meltano ELT pipeline configuration
├── great_expectations_config.json       # Great Expectations setup
├── great_expectations_validator.py      # Python validation script
├── setup_elt_pipeline.sh                # Setup script for all tools
│
└── london_bicycles_dbt/
    ├── models/
    │   ├── sources.yml                  # Source definitions
    │   ├── staging/                     # Staging - cleaned, standardized data (views)
    │   │   ├── stg_stations.sql
    │   │   ├── stg_trips.sql
    │   │   └── staging.yml
    │   └── marts/                       # Mart - business-ready tables
    │       ├── dim_stations.sql         # Station dimensions
    │       ├── fct_trips.sql            # Trip facts
    │       ├── trips_by_hour.sql        # Hourly aggregates
    │       ├── seasonal_trips.sql       # Monthly/seasonal analysis (NEW)
    │       ├── station_trip_volume.sql  # High-volume station analysis (NEW)
    │       ├── quarterly_area_analysis.sql # Quarterly geographic analysis (NEW)
    │       ├── marts.yml
    │       └── kpi_marts.yml           # New KPI documentation
    │
    ├── seeds/
    │   ├── stations.csv                 # 15 sample stations
    │   └── trips.csv                    # 20 sample trips
    │
    ├── dbt_project.yml                  # dbt configuration
    ├── profiles.yml                     # BigQuery connection config
    └── macros/
        └── run_great_expectations.sql   # dbt hook for GX integration

tests/                                   # Generated dbt tests
analyses/                                # Analysis queries
```

## Data Models

### Staging Layer (2 Views)
Intermediate transformations from raw sources

#### `stg_stations`
- Cleans and standardizes station reference data
- Fields: station_id, station_name, latitude, longitude

#### `stg_trips`  
- Transforms trip transactions with calculated fields
- Added fields: duration_minutes, trip_date, start_hour, day_of_week
- Handles timestamp conversions for BigQuery

### Mart Layer (6 Tables)

#### **Dimension Tables**
**dim_stations**
- Station master data with 15 sample locations
- Geographic classification (Central/Outer London)
- Latitude/longitude coordinates

#### **Fact Tables**
**fct_trips**
- Detailed trip records (20 sample trips)
- Enriched with station names mapped from dimension
- Trip duration categorization (short/medium/long/very_long)

#### **Aggregate & KPI Tables** (NEW)

**trips_by_hour**
- Hour-level trip metrics (7 rows)
- Metrics: trip counts, avg/min/max duration, unique bikes/users

**seasonal_trips** ⭐ **NEW**
- Monthly analysis of trip patterns
- Metrics: total trips, unique bikes, subscriber/casual split
- Useful for: Seasonal trend analysis, yearly planning

**station_trip_volume** ⭐ **NEW**
- High-volume station ranking and analysis
- Metrics: trip counts, bikes used, subscriber percentage, volume rank
- Identifies busiest stations by geographic area
- Useful for: Station optimization, resource allocation

**quarterly_area_analysis** ⭐ **NEW**
- Quarterly trends by geographic area and user type
- Metrics: trip counts, duration stats, unique bikes, stations visited
- Compares Central vs. Outer London usage patterns
- Useful for: Regional strategy, capacity planning

### Staging Models (Views)

#### `stg_stations`
- Cleans and standardizes station reference data
- Renames columns for consistency (e.g., `name` → `station_name`)
- No aggregations, direct transformations from source

#### `stg_trips`
- Transforms trip transactions with added calculations:
  - Converts duration from seconds to minutes
  - Extracts temporal components (date, hour, day of week)
  - Handles timestamp conversions for BigQuery

### Mart Models (Tables)

#### `dim_stations` (Dimension)
- Station master data with geographic information
- Includes geographic area classification (Central/Outer London)
- 15 sample stations covering various London locations

#### `fct_trips` (Fact)
- Detailed trip records with enriched attributes
- Joins with dimension tables for station names
- Includes trip duration categorization (short/medium/long/very_long)
- 20 sample trips for testing

#### `trips_by_hour` (Aggregate)
- Hour-level trip metrics for analysis
- Aggregations: count, avg/min/max duration, unique bikes/users
- Useful for time-series analysis and trend identification

## Data Quality Tests

The project includes comprehensive dbt tests:
- **Uniqueness tests** on primary keys (station_id, trip_id)
- **Not null tests** on required columns
- **Referential integrity** through model relationships

### Running Tests
```bash
$ dbt test
```

### Test Results
All 31 model tests pass successfully, validating data quality and schema assumptions.

## Commands

### Initialize dbt (already done)
```bash
$ dbt init london_bicycles_dbt
```

### Verify Configuration and Connection
```bash
$ dbt debug
# Expected: "All checks passed!" with successful connection test
```

### Load Seed Data
```bash
$ dbt seed
# Loads CSV files into BigQuery as tables
```

### Execute Models (builds staging and mart tables)
```bash
$ dbt run
# Expected: All 5 models created successfully
```

### Run Data Quality Tests
```bash
$ dbt test
# Expected: 31 tests pass
```

### Generate Documentation
```bash
$ dbt docs generate
$ dbt docs serve  # localhost:8000
```

## Sample Outputs

After running `dbt run`, you'll have:

**Staging Tables** (in `london_bicycles_staging` schema):
- `stg_stations` - 15 stations with cleaned attributes
- `stg_trips` - 20 trips with calculated duration_minutes and date components

**Production Tables** (in `london_bicycles` schema):
- `dim_stations` - Station dimension with area classification
- `fct_trips` - Enriched trip facts with station names and categories
- `trips_by_hour` - 7 hourly aggregates with trip metrics

## Business Analysis Use Cases

### 1. Peak Hour Analysis
Query `trips_by_hour` to identify busy periods:
```sql
SELECT trip_date, start_hour, num_trips
FROM london_bicycles_marts.trips_by_hour
ORDER BY num_trips DESC
```

### 2. Station Coverage
Analyze trips by geographic area:
```sql
SELECT station_area, COUNT(*) as trip_count
FROM london_bicycles_marts.fct_trips
GROUP BY station_area
```

### 3. Trip Duration Insights
```sql
SELECT trip_duration_category, 
       COUNT(*) as count,
       AVG(duration_minutes) as avg_duration
FROM london_bicycles_marts.fct_trips
GROUP BY trip_duration_category
```

## Extending the Project

### Add New Models
1. Create `.sql` file in `models/staging/` or `models/marts/`
2. Use `{{ ref('source_model') }}` to reference other models
3. Add configuration in corresponding `.yml` file
4. Run `dbt run` to build

### Modify Configuration
- Update `profiles.yml` for BigQuery connection settings
- Update `dbt_project.yml` for project-wide settings
- Modify schema generation in model configs with `{{ config(...) }}`

### Working with Real Public Data
To use the actual Google BigQuery public dataset:
1. Ensure your GCP project has access to `bigquery-public-data.london_bicycles`
2. Update staging models to reference `{{ source('bigquery_public_data', 'table_name') }}`
3. Handle cross-location queries if needed (EU location → US public data)

## Troubleshooting

### Connection Issues
```bash
$ gcloud auth application-default login
$ dbt debug  # Verify authentication
```

### Model Failures
- Check SQL syntax in individual model files
- Verify source tables exist in BigQuery
- Review error messages and BigQuery query links

### Test Failures
- Review test SQL: `target/compiled/{project}/tests/`
- Adjust test logic or data to meet quality standards

## Performance Optimization

The current setup uses:
- **Views** for staging models (no storage cost)
- **Tables** for marts (enables efficient querying)
- **Single-threaded execution** (adjust in profiles.yml `threads`)

For larger datasets, consider:
- Increasing thread count in profiles.yml
- Adding incremental models for fact tables
- Using clustering/partitioning on BigQuery tables

## References

- [dbt Documentation](https://docs.getdbt.com/)
- [BigQuery dbt Adapter](https://docs.getdbt.com/reference/warehouse-setups/bigquery-setup)
- [Google Cloud BigQuery Python](https://docs.cloud.google.com/bigquery/docs/reference/libraries#client-libraries-usage-python)
