#!/bin/bash
# Quick verification script for Dagster ELT pipeline setup

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Dagster ELT Pipeline Verification                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python environment
echo "1. Checking Python environment..."
if python --version &>/dev/null; then
    echo "   ✓ Python: $(python --version 2>&1 | cut -d' ' -f2)"
else
    echo "   ✗ Python not found"
    exit 1
fi

# Check Dagster installation
echo ""
echo "2. Checking Dagster installation..."
if python -c "import dagster; print(f'✓ Dagster: {dagster.__version__}')" 2>&1; then
    :
else
    echo "   ✗ Dagster not installed"
    exit 1
fi

# Check required files
echo ""
echo "3. Checking required files..."
required_files=("dagster_assets.py" "dagster.yaml" "workspace.yaml" "great_expectations_validator.py")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file not found"
        exit 1
    fi
done

# Check job configuration
echo ""
echo "4. Checking job configuration..."
if grep -q "in_process_executor" dagster_assets.py; then
    echo "   ✓ In-process executor configured (prevents SQLite locking)"
else
    echo "   ⚠ Warning: In-process executor not found"
fi

# Verify job can be loaded
echo ""
echo "5. Verifying job definitions can be loaded..."
if python -c "
from dagster_assets import london_bicycles_elt_job, defs
print(f'   ✓ Job: {london_bicycles_elt_job.name}')
print(f'   ✓ Definitions contain {len(defs.assets)} assets')
" 2>&1; then
    :
else
    echo "   ✗ Failed to load job definitions"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  All checks passed! ✅                                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Run: dagster dev"
echo "  2. Open: http://localhost:3000"
echo "  3. Find job: london_bicycles_full_elt"
echo "  4. Click 'Launch Run' to execute"
echo ""
