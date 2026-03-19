#!/bin/bash

# London Bicycles ELT Pipeline Setup Script
# Sets up Dagster, dbt, and Great Expectations
# Version: 2.0 (Dagster-based orchestration)

set -e

echo "================================================"
echo "London Bicycles ELT Pipeline Setup"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate conda environment
echo -e "${BLUE}Activating conda environment: dagster...${NC}"
source activate dagster || conda activate dagster

# Navigate to project directory
PROJECT_DIR="/mnt/40121FB8121FB1C0/Shared Files/My Documents (Ubuntu)/repo/su-ntu-ctp/module2_assignment_project/london_bicycles"
DBT_DIR="${PROJECT_DIR}/london_bicycles_dbt"

cd "$DBT_DIR"

# Verify installations
echo -e "\n${BLUE}Verifying required packages...${NC}"

# Check dbt
if python -c "import dbt" 2>/dev/null; then
    DBT_VERSION=$(python -c "import dbt; print(dbt.__version__)")
    echo -e "${GREEN}✓${NC} dbt ${DBT_VERSION} installed"
else
    echo -e "${YELLOW}✗${NC} dbt not found - please install with: pip install dbt-core dbt-bigquery"
    exit 1
fi

# Check Dagster
if python -c "import dagster" 2>/dev/null; then
    DAGSTER_VERSION=$(python -c "import dagster; print(dagster.__version__)")
    echo -e "${GREEN}✓${NC} Dagster ${DAGSTER_VERSION} installed"
else
    echo -e "${YELLOW}✗${NC} Dagster not found - please install with: pip install dagster dagster-webserver"
    exit 1
fi

# Check Great Expectations
if python -c "import great_expectations" 2>/dev/null; then
    GX_VERSION=$(python -c "import great_expectations; print(great_expectations.__version__)")
    echo -e "${GREEN}✓${NC} Great Expectations ${GX_VERSION} installed"
else
    echo -e "${YELLOW}✗${NC} Great Expectations not found - please install with: pip install great-expectations"
    exit 1
fi

# Verify dbt configuration
echo -e "\n${BLUE}Testing dbt configuration...${NC}"
if dbt debug --profiles-dir . > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} dbt configuration verified (BigQuery connection OK)"
else
    echo -e "${YELLOW}⚠${NC}  dbt configuration may need adjustment - run 'dbt debug' for details"
fi

# Load seed data (optional)
read -p "Load/reload seed data (stations.csv, trips.csv)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}Loading seed data...${NC}"
    dbt seed --profiles-dir .
    echo -e "${GREEN}✓${NC} Seed data loaded"
fi

# Generate dbt documentation
echo -e "\n${BLUE}Generating dbt documentation...${NC}"
dbt docs generate --profiles-dir . > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Documentation generated"

# Verify Dagster assets load
echo -e "\n${BLUE}Verifying Dagster setup...${NC}"
if python -c "from dagster_assets import defs; print(f'✓ Loaded: {len(defs.jobs)} jobs, {len(defs.assets)} assets')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Dagster assets and jobs loaded successfully"
else
    echo -e "${YELLOW}✗${NC} Issue loading Dagster assets - check dagster_assets.py"
    exit 1
fi

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}ELT Pipeline Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"

echo -e "\n${BLUE}Getting Started:${NC}"
echo ""
echo -e "  ${YELLOW}1. Launch Dagster UI:${NC}"
echo -e "     \$ dagster dev"
echo -e "     → Opens at http://localhost:3000"
echo ""
echo -e "  ${YELLOW}2. Execute pipelines from UI:${NC}"
echo -e "     → Jobs tab → select 'london_bicycles_full_elt' → Launch Run"
echo ""
echo -e "  ${YELLOW}3. Or run from CLI:${NC}"
echo -e "     \$ dbt run              # Transform data"
echo -e "     \$ dbt test             # Run quality tests"
echo -e "     \$ python great_expectations_validator.py  # Validate"
echo ""
echo -e "  ${YELLOW}4. View documentation:${NC}"
echo -e "     \$ dbt docs serve"
echo -e "     → Opens at http://localhost:8000"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo -e "  - Setup Guide: ../london_bicycles_dbt/DAGSTER_SETUP.md"
echo -e "  - Project Info: ../README.md"
echo ""
