#!/bin/bash

# London Bicycles ELT Pipeline Setup Script
# Sets up Meltano, dbt, and Great Expectations

set -e

echo "================================================"
echo "London Bicycles ELT Pipeline Setup"
echo "================================================"

# Activate conda environment
echo "Activating conda environment: dagster..."
source activate dagster

# Install Meltano if not already installed
echo -e "\nChecking Meltano installation..."
if ! command -v meltano &> /dev/null; then
    echo "Installing Meltano..."
    pip install meltano
else
    echo "✓ Meltano already installed"
fi

# Initialize Meltano project
echo -e "\nInitializing Meltano project..."
cd /mnt/40121FB8121FB1C0/Shared\ Files/My\ Documents\ \(Ubuntu\)/repo/su-ntu-ctp/module2_assignment_project/london_bicycles

if [ ! -f "meltano.yml" ]; then
    echo "meltano.yml not found in expected location"
fi

# Verify Great Expectations
echo -e "\nChecking Great Expectations installation..."
python -c "import great_expectations; print('✓ Great Expectations version:', great_expectations.__version__)"

# Setup dbt
echo -e "\nSetting up dbt..."
cd london_bicycles_dbt
dbt debug

# Create dbt documentation
echo -e "\nGenerating dbt documentation..."
dbt docs generate

echo -e "\n================================================"
echo "ELT Pipeline Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Configure Meltano extractors:"
echo "   $ meltano invoke tap-bigquery --help"
echo ""
echo "2. Run dbt models:"
echo "   $ dbt run"
echo ""
echo "3. Run data quality tests:"
echo "   $ dbt test"
echo ""
echo "4. Run Great Expectations validations:"
echo "   $ python great_expectations_validator.py"
echo ""
echo "5. Run full ELT pipeline with Meltano:"
echo "   $ meltano run tap-bigquery target-bigquery dbt:run dbt:test"
echo ""
