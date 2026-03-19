import great_expectations as ge
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.core.batch_definition import BatchDefinition
from google.cloud import bigquery
import pandas as pd
import json

class LondonBicyclesGreatExpectations:
    """
    Great Expectations validation framework for London Bicycles data
    """
    
    def __init__(self, project_id="pydrive-colab-2", dataset="london_bicycles"):
        self.project_id = project_id
        self.dataset = dataset
        self.client = bigquery.Client(project=project_id)
    
    def validate_staging_trips(self):
        """Validate staging trips data quality using pandas operations"""
        try:
            query = f"""
                SELECT * FROM `{self.project_id}.{self.dataset}_staging.stg_trips` LIMIT 1000
            """
            df = self.client.query(query).result().to_dataframe()
            
            validation_results = {
                "table": "stg_trips",
                "status": "passed",
                "checks": []
            }
            
            # Trip ID uniqueness
            unique_check = len(df['trip_id'].unique()) == len(df['trip_id'])
            validation_results["checks"].append({
                "name": "trip_id uniqueness",
                "passed": unique_check
            })
            
            # Duration constraints (0 to 86400 seconds)
            duration_check = (df['duration'].min() >= 0) and (df['duration'].max() <= 86400)
            validation_results["checks"].append({
                "name": "duration range (0-86400)",
                "passed": duration_check
            })
            
            # Duration minutes should be positive
            duration_min_check = df['duration_minutes'].min() >= 0
            validation_results["checks"].append({
                "name": "duration_minutes >= 0",
                "passed": duration_min_check
            })
            
            # Not null constraints
            nn_trip_id = df['trip_id'].notna().all()
            nn_start_station = df['start_station_id'].notna().all()
            nn_end_station = df['end_station_id'].notna().all()
            nn_trip_date = df['trip_date'].notna().all()
            nn_duration = df['duration_minutes'].notna().all()
            
            validation_results["checks"].append({
                "name": "trip_id not null",
                "passed": nn_trip_id
            })
            validation_results["checks"].append({
                "name": "start_station_id not null",
                "passed": nn_start_station
            })
            validation_results["checks"].append({
                "name": "end_station_id not null",
                "passed": nn_end_station
            })
            validation_results["checks"].append({
                "name": "trip_date not null",
                "passed": nn_trip_date
            })
            validation_results["checks"].append({
                "name": "duration_minutes not null",
                "passed": nn_duration
            })
            
            # Overall status
            validation_results["status"] = "passed" if all(c["passed"] for c in validation_results["checks"]) else "failed"
            
            return validation_results
        except Exception as e:
            return {
                "table": "stg_trips",
                "status": "failed",
                "error": str(e)
            }
    
    def validate_staging_stations(self):
        """Validate staging stations data quality using pandas operations"""
        try:
            query = f"""
                SELECT * FROM `{self.project_id}.{self.dataset}_staging.stg_stations`
            """
            df = self.client.query(query).result().to_dataframe()
            
            validation_results = {
                "table": "stg_stations",
                "status": "passed",
                "checks": []
            }
            
            # Station ID uniqueness
            unique_check = len(df['station_id'].unique()) == len(df['station_id'])
            validation_results["checks"].append({
                "name": "station_id uniqueness",
                "passed": unique_check
            })
            
            # Not null constraints
            nn_station_id = df['station_id'].notna().all()
            nn_station_name = df['station_name'].notna().all()
            nn_latitude = df['latitude'].notna().all()
            nn_longitude = df['longitude'].notna().all()
            
            validation_results["checks"].append({
                "name": "station_id not null",
                "passed": nn_station_id
            })
            validation_results["checks"].append({
                "name": "station_name not null",
                "passed": nn_station_name
            })
            validation_results["checks"].append({
                "name": "latitude not null",
                "passed": nn_latitude
            })
            validation_results["checks"].append({
                "name": "longitude not null",
                "passed": nn_longitude
            })
            
            # Geographic bounds for London
            lat_check = (df['latitude'].min() >= 51.3) and (df['latitude'].max() <= 51.7)
            lon_check = (df['longitude'].min() >= -0.3) and (df['longitude'].max() <= 0.1)
            
            validation_results["checks"].append({
                "name": "latitude bounds (51.3-51.7)",
                "passed": lat_check
            })
            validation_results["checks"].append({
                "name": "longitude bounds (-0.3-0.1)",
                "passed": lon_check
            })
            
            # Overall status
            validation_results["status"] = "passed" if all(c["passed"] for c in validation_results["checks"]) else "failed"
            
            return validation_results
        except Exception as e:
            return {
                "table": "stg_stations",
                "status": "failed",
                "error": str(e)
            }
    
    def validate_mart_fct_trips(self):
        """Validate fact trips mart using pandas operations"""
        try:
            query = f"""
                SELECT * FROM `{self.project_id}.{self.dataset}_marts.fct_trips` LIMIT 1000
            """
            df = self.client.query(query).result().to_dataframe()
            
            validation_results = {
                "table": "fct_trips",
                "status": "passed",
                "checks": []
            }
            
            # Trip ID uniqueness and not null
            unique_check = len(df['trip_id'].unique()) == len(df['trip_id'])
            nn_check = df['trip_id'].notna().all()
            
            validation_results["checks"].append({
                "name": "trip_id uniqueness",
                "passed": unique_check
            })
            validation_results["checks"].append({
                "name": "trip_id not null",
                "passed": nn_check
            })
            
            # Duration should be positive
            duration_check = df['duration_minutes'].min() >= 0
            validation_results["checks"].append({
                "name": "duration_minutes >= 0",
                "passed": duration_check
            })
            
            # Trip duration category values
            valid_categories = {"short", "medium", "long", "very_long"}
            category_check = set(df['trip_duration_category'].unique()).issubset(valid_categories)
            validation_results["checks"].append({
                "name": "trip_duration_category in valid set",
                "passed": category_check
            })
            
            # Overall status
            validation_results["status"] = "passed" if all(c["passed"] for c in validation_results["checks"]) else "failed"
            
            return validation_results
        except Exception as e:
            return {
                "table": "fct_trips",
                "status": "failed",
                "error": str(e)
            }
    
    def validate_mart_dim_stations(self):
        """Validate stations dimension mart using pandas operations"""
        try:
            query = f"""
                SELECT * FROM `{self.project_id}.{self.dataset}_marts.dim_stations`
            """
            df = self.client.query(query).result().to_dataframe()
            
            validation_results = {
                "table": "dim_stations",
                "status": "passed",
                "checks": []
            }
            
            # Station ID uniqueness
            unique_check = len(df['station_id'].unique()) == len(df['station_id'])
            nn_check = df['station_id'].notna().all()
            
            validation_results["checks"].append({
                "name": "station_id uniqueness",
                "passed": unique_check
            })
            validation_results["checks"].append({
                "name": "station_id not null",
                "passed": nn_check
            })
            
            # Area classification
            valid_areas = {"Central", "Outer"}
            area_check = set(df['station_area'].unique()).issubset(valid_areas)
            validation_results["checks"].append({
                "name": "station_area in valid set",
                "passed": area_check
            })
            
            # Overall status
            validation_results["status"] = "passed" if all(c["passed"] for c in validation_results["checks"]) else "failed"
            
            return validation_results
        except Exception as e:
            return {
                "table": "dim_stations",
                "status": "failed",
                "error": str(e)
            }
    
    def run_all_validations(self):
        """Run all data quality validations"""
        results = {}
        
        print("Running Data Quality Validations...")
        print("-" * 60)
        
        # Validate Staging Trips
        stg_trips_results = self.validate_staging_trips()
        if stg_trips_results["status"] == "passed":
            print("✓ Staging Trips validation passed")
            passed_checks = sum(1 for c in stg_trips_results.get("checks", []) if c.get("passed"))
            total_checks = len(stg_trips_results.get("checks", []))
            print(f"  Checks: {passed_checks}/{total_checks}")
        else:
            if "error" in stg_trips_results:
                print(f"✗ Staging Trips validation failed: {stg_trips_results['error']}")
            else:
                print("✗ Staging Trips validation failed")
                for check in stg_trips_results.get("checks", []):
                    if not check.get("passed"):
                        print(f"  - {check['name']}: FAILED")
        results['stg_trips'] = stg_trips_results
        
        # Validate Staging Stations
        stg_stations_results = self.validate_staging_stations()
        if stg_stations_results["status"] == "passed":
            print("✓ Staging Stations validation passed")
            passed_checks = sum(1 for c in stg_stations_results.get("checks", []) if c.get("passed"))
            total_checks = len(stg_stations_results.get("checks", []))
            print(f"  Checks: {passed_checks}/{total_checks}")
        else:
            if "error" in stg_stations_results:
                print(f"✗ Staging Stations validation failed: {stg_stations_results['error']}")
            else:
                print("✗ Staging Stations validation failed")
                for check in stg_stations_results.get("checks", []):
                    if not check.get("passed"):
                        print(f"  - {check['name']}: FAILED")
        results['stg_stations'] = stg_stations_results
        
        # Validate Fact Trips
        fct_trips_results = self.validate_mart_fct_trips()
        if fct_trips_results["status"] == "passed":
            print("✓ Fact Trips mart validation passed")
            passed_checks = sum(1 for c in fct_trips_results.get("checks", []) if c.get("passed"))
            total_checks = len(fct_trips_results.get("checks", []))
            print(f"  Checks: {passed_checks}/{total_checks}")
        else:
            if "error" in fct_trips_results:
                print(f"✗ Fact Trips mart validation failed: {fct_trips_results['error']}")
            else:
                print("✗ Fact Trips mart validation failed")
                for check in fct_trips_results.get("checks", []):
                    if not check.get("passed"):
                        print(f"  - {check['name']}: FAILED")
        results['fct_trips'] = fct_trips_results
        
        # Validate Dimension Stations
        dim_stations_results = self.validate_mart_dim_stations()
        if dim_stations_results["status"] == "passed":
            print("✓ Dimension Stations mart validation passed")
            passed_checks = sum(1 for c in dim_stations_results.get("checks", []) if c.get("passed"))
            total_checks = len(dim_stations_results.get("checks", []))
            print(f"  Checks: {passed_checks}/{total_checks}")
        else:
            if "error" in dim_stations_results:
                print(f"✗ Dimension Stations mart validation failed: {dim_stations_results['error']}")
            else:
                print("✗ Dimension Stations mart validation failed")
                for check in dim_stations_results.get("checks", []):
                    if not check.get("passed"):
                        print(f"  - {check['name']}: FAILED")
        results['dim_stations'] = dim_stations_results
        
        print("-" * 60)
        
        # Summary
        total_suites = 4
        passed_suites = sum(1 for r in results.values() if r.get("status") == "passed")
        print(f"Summary: {passed_suites}/{total_suites} validation suites passed")
        print("Validations complete!")
        
        return results

# Entry point for running validations
if __name__ == "__main__":
    validator = LondonBicyclesGreatExpectations()
    validator.run_all_validations()
