# Dagster ELT Pipeline Setup Guide

## Overview
The London Bicycles ELT pipeline orchestration with **Dagster**. This allows managing and monitoring the complete ELT pipeline orchestrated with Extract → Load → Transform → Validate workflow through the Dagster UI.

## Pipeline Components

```
Meltano Extract-Load  →  dbt Transformation  →  Great Expectations Validation
```

The orchestration is defined in `dagster_assets.py` with the following ops (operations):

1. **run_meltano_extract_load()** - Extracts from BigQuery, loads to london_bicycles_raw
2. **run_dbt_transform()** - Runs dbt models and tests
3. **run_great_expectations_validation()** - Validates data quality

## Setup Instructions

### 1. Verify Environment
Make sure your Dagster environment is active:

```bash
conda activate dagster
cd london_bicycles_dbt
```

### 2. Install Required Packages (if not already installed)

```bash
pip install dagster dagster-webserver
```

### 3. Launch Dagster UI

```bash
dagster dev
```

This will:
- Start Dagster daemon
- Launch the Dagster UI at **http://localhost:3000**
- Auto-reload when files change

## Using Dagster UI

### Run the ELT Pipeline

1. Navigate to **http://localhost:3000**
2. Find the job: **london_bicycles_full_elt**
3. Click "Launch Run" to execute
4. Monitor progress in real-time:
   - Extract-Load phase (Meltano)
   - dbt Transformation phase
   - Data validation phase

### View Assets

The Dagster UI displays all 7 data assets:
- **Staging Layer**: stg_trips, stg_stations
- **Mart Layer**: dim_stations, fct_trips
- **KPI Layer**: seasonal_trips, station_trip_volume, quarterly_area_analysis

### Check Logs

For each operation, view detailed logs:
- Meltano tap-bigquery output
- dbt run/test results
- Great Expectations validation results

## meltano.yml Configuration

Updated to use Dagster orchestrator:

```yaml
orchestrators:
  - name: dagster
    variant: dagster
    pip_url: dagster~=1.8.0 dagster-webserver~=1.8.0
```

## Command Line Alternative

If prefer CLI instead of UI:

```bash
# Run the ELT job
dagster job execute -f dagster_assets.py -j london_bicycles_full_elt

# View available jobs
dagster job list -f dagster_assets.py

# View available assets
dagster asset list -f dagster_assets.py
```

## Pipeline Execution Flow

```
┌─────────────────────────────────────────┐
│ run_meltano_extract_load()              │
│ - Execute: meltano run extract-load     │
│ - Source: 'GCP Project ID'/london_bikes │
│ - Target: google-bicycles_raw           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ run_dbt_transform()                     │
│ - Execute: dbt run + dbt test           │
│ - 8 models (2 views + 6 tables)         │
│ - 30+ data quality tests                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ run_great_expectations_validation()     │
│ - Execute: python validator script      │
│ - 4 validation suites (22 checks)       │
│ - All layers (staging, marts, KPIs)     │
└─────────────────────────────────────────┘
```

## Troubleshooting

### Error: "module 'dagster' not found"
**Solution**: Install Dagster in your environment
```bash
pip install dagster dagster-webserver
```

### Error: "Cannot find dagster_assets.py"
**Solution**: Make sure you're in the `london_bicycles_dbt` directory
```bash
cd london_bicycles_dbt
dagster dev
```

### Error: "meltano command not found"
**Solution**: Ensure meltano is installed and accessible
```bash
meltano --version
```

### Port 3000 Already in Use
**Solution**: Specify a different port
```bash
dagster dev --port 3001
```

## Schedule Daily Runs

To run the pipeline on a schedule (daily at 2 AM UTC):

1. Deploy Dagster with a persistent database
2. Use `dagster-daemon` for scheduling
3. Or integrate with external schedulers (Airflow, cron, etc.)

For development, use the UI to manually trigger runs.

## Integration Points

- **BigQuery**: Connection via OAuth (gcloud auth)
- **dbt**: Configured in profiles.yml
- **Meltano**: Job definitions in meltano.yml
- **Great Expectations**: Python validator script

## Next Steps

1. Start Dagster: `dagster dev`
2. Navigate to http://localhost:3000
3. Click "Launch Run" on london_bicycles_full_elt job
4. Monitor pipeline execution
5. View asset lineage and data quality metrics
6. Deploy to production with persistent database

---

**Documentation**: See PROJECT_README.md for complete ELT architecture details
