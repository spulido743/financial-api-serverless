#!/bin/bash

echo "🧪 Testing Lambda Function: saveStockPrice"
echo "=========================================="
echo ""

FUNCTION_NAME="saveStockPrice"
TEST_DIR="test_events"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

run_test() {
    local test_file=$1
    local test_name=$2
    local expected_status=$3
    
    echo -e "${YELLOW}▶ Test: ${test_name}${NC}"
    
    aws lambda invoke \
        --function-name $FUNCTION_NAME \
        --payload file://${TEST_DIR}/${test_file} \
        --cli-binary-format raw-in-base64-out \
        response.json \
        --query 'StatusCode' \
        --output text > /dev/null 2>&1
    
    status_code=$(cat response.json | python3 -c "import sys, json; print(json.load(sys.stdin).get('statusCode', 'N/A'))")
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} - Status: $status_code"
    else
        echo -e "${RED}❌ FAIL${NC} - Expected: $expected_status, Got: $status_code"
    fi
    
    echo "   Response: $(cat response.json)"
    echo ""
}

# Ejecutar tests
run_test "test-aapl.json" "AAPL - Valid input" "200"
run_test "test-googl.json" "GOOGL - Valid input" "200"
run_test "test-msft.json" "MSFT - Valid input" "200"
run_test "test-error-missing-price.json" "Missing price field" "400"

echo "=========================================="
echo "✅ Tests completados"
echo ""
echo "📊 Datos en DynamoDB:"
aws dynamodb scan --table-name FinancialData --query 'Items[*].[symbol.S, price.N]' --output table

# Cleanup
rm -f response.json
