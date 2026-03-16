#!/bin/bash

# Nova Forge Backend Test Runner
# This script runs all tests and generates a report

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   NOVA FORGE BACKEND TEST RUNNER${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found.${NC}"
    echo "Please run this script from the research_agent directory:"
    echo "  cd research_agent && bash run_tests.sh"
    exit 1
fi

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo -e "${YELLOW}Python Version:${NC} $python_version"

# Check if required packages are installed
echo ""
echo -e "${YELLOW}Checking dependencies...${NC}"

required_packages=("fastapi" "pydantic" "arxiv" "boto3" "dotenv")
missing_packages=()

for package in "${required_packages[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $package"
    else
        echo -e "${RED}✗${NC} $package"
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Missing packages detected. Install with:${NC}"
    echo "  pip install -e ."
    exit 1
fi

echo ""
echo -e "${YELLOW}Running test suite...${NC}"
echo ""

# Run the comprehensive test suite
if [ -f "test_api.py" ]; then
    python test_api.py
    test_exit_code=$?
else
    echo -e "${RED}test_api.py not found${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

if [ $test_exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start backend: python main.py"
    echo "  2. Test endpoint: curl http://localhost:7777/health"
    echo "  3. Start frontend: cd ../chat-app && pnpm dev"
    exit 0
else
    echo -e "${RED}✗ TESTS FAILED${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Please check the error messages above."
    exit 1
fi
