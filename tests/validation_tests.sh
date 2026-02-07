#!/bin/bash

echo "=========================================="
echo "🧪 SUITE DE TESTS DE VALIDACIÓN"
echo "=========================================="
echo ""

PASS=0
FAIL=0

# Función helper para verificar código HTTP
check_status_code() {
    local test_name=$1
    local expected=$2
    local response_file=$3
    
    actual=$(cat $response_file | python3 -c "import sys, json; print(json.load(sys.stdin)['statusCode'])")
    
    if [ "$actual" == "$expected" ]; then
        echo "✅ PASS: $test_name (HTTP $actual)"
        ((PASS++))
    else
        echo "❌ FAIL: $test_name (Expected HTTP $expected, got $actual)"
        ((FAIL++))
    fi
}

echo "=========================================="
echo "TEST GROUP 1: fetchRealTimePrice"
echo "=========================================="
echo ""

# Test 1.1: Símbolo válido
echo "Test 1.1: Símbolo válido (AAPL)"
aws lambda invoke \
    --function-name fetchRealTimePrice \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"}}' \
    test_1_1.json > /dev/null 2>&1
check_status_code "Símbolo válido" "200" "test_1_1.json"

# Test 1.2: Símbolo vacío
echo "Test 1.2: Símbolo vacío"
aws lambda invoke \
    --function-name fetchRealTimePrice \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":""}}' \
    test_1_2.json > /dev/null 2>&1
check_status_code "Símbolo vacío" "400" "test_1_2.json"

# Test 1.3: Símbolo demasiado largo
echo "Test 1.3: Símbolo demasiado largo (ABCDEF)"
aws lambda invoke \
    --function-name fetchRealTimePrice \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"ABCDEF"}}' \
    test_1_3.json > /dev/null 2>&1
check_status_code "Símbolo largo" "400" "test_1_3.json"

# Test 1.4: Símbolo con números
echo "Test 1.4: Símbolo con números (ABC123)"
aws lambda invoke \
    --function-name fetchRealTimePrice \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"ABC123"}}' \
    test_1_4.json > /dev/null 2>&1
check_status_code "Símbolo con números" "400" "test_1_4.json"

# Test 1.5: Símbolo con caracteres especiales
echo "Test 1.5: Símbolo con caracteres especiales (AB@C)"
aws lambda invoke \
    --function-name fetchRealTimePrice \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AB@C"}}' \
    test_1_5.json > /dev/null 2>&1
check_status_code "Símbolo con especiales" "400" "test_1_5.json"

# Test 1.6: Sin pathParameters
echo "Test 1.6: Sin pathParameters"
aws lambda invoke \
    --function-name fetchRealTimePrice \
    --cli-binary-format raw-in-base64-out \
    --payload '{}' \
    test_1_6.json > /dev/null 2>&1
check_status_code "Sin pathParameters" "400" "test_1_6.json"

echo ""
echo "=========================================="
echo "TEST GROUP 2: getHistoricalPrices"
echo "=========================================="
echo ""

# Test 2.1: Query válido
echo "Test 2.1: Query válido (AAPL, 7 días)"
aws lambda invoke \
    --function-name getHistoricalPrices \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"days":"7"}}' \
    test_2_1.json > /dev/null 2>&1
# Puede ser 200 o 404 dependiendo de si hay datos
actual=$(cat test_2_1.json | python3 -c "import sys, json; print(json.load(sys.stdin)['statusCode'])")
if [ "$actual" == "200" ] || [ "$actual" == "404" ]; then
    echo "✅ PASS: Query válido (HTTP $actual)"
    ((PASS++))
else
    echo "❌ FAIL: Query válido (Expected HTTP 200/404, got $actual)"
    ((FAIL++))
fi

# Test 2.2: Days negativo
echo "Test 2.2: Days negativo (-5)"
aws lambda invoke \
    --function-name getHistoricalPrices \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"days":"-5"}}' \
    test_2_2.json > /dev/null 2>&1
check_status_code "Days negativo" "400" "test_2_2.json"

# Test 2.3: Days = 0
echo "Test 2.3: Days = 0"
aws lambda invoke \
    --function-name getHistoricalPrices \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"days":"0"}}' \
    test_2_3.json > /dev/null 2>&1
check_status_code "Days cero" "400" "test_2_3.json"

# Test 2.4: Days mayor a 365
echo "Test 2.4: Days > 365 (500)"
aws lambda invoke \
    --function-name getHistoricalPrices \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"days":"500"}}' \
    test_2_4.json > /dev/null 2>&1
check_status_code "Days mayor 365" "400" "test_2_4.json"

# Test 2.5: Days no numérico
echo "Test 2.5: Days no numérico (abc)"
aws lambda invoke \
    --function-name getHistoricalPrices \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"days":"abc"}}' \
    test_2_5.json > /dev/null 2>&1
check_status_code "Days no numérico" "400" "test_2_5.json"

# Test 2.6: Limit inválido
echo "Test 2.6: Limit > 1000 (2000)"
aws lambda invoke \
    --function-name getHistoricalPrices \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"days":"7","limit":"2000"}}' \
    test_2_6.json > /dev/null 2>&1
check_status_code "Limit > 1000" "400" "test_2_6.json"

# Test 2.7: Símbolo inválido
echo "Test 2.7: Símbolo inválido (12345)"
aws lambda invoke \
    --function-name getHistoricalPrices \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"12345"}}' \
    test_2_7.json > /dev/null 2>&1
check_status_code "Símbolo inválido" "400" "test_2_7.json"

echo ""
echo "=========================================="
echo "TEST GROUP 3: calculateIndicators"
echo "=========================================="
echo ""

# Test 3.1: Query válido
echo "Test 3.1: Query válido (AAPL, period 14)"
aws lambda invoke \
    --function-name calculateIndicators \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"period":"14"}}' \
    test_3_1.json > /dev/null 2>&1
actual=$(cat test_3_1.json | python3 -c "import sys, json; print(json.load(sys.stdin)['statusCode'])")
if [ "$actual" == "200" ] || [ "$actual" == "404" ] || [ "$actual" == "400" ]; then
    echo "✅ PASS: Query válido (HTTP $actual)"
    ((PASS++))
else
    echo "❌ FAIL: Query válido (Expected HTTP 200/400/404, got $actual)"
    ((FAIL++))
fi

# Test 3.2: Period negativo
echo "Test 3.2: Period negativo (-10)"
aws lambda invoke \
    --function-name calculateIndicators \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"period":"-10"}}' \
    test_3_2.json > /dev/null 2>&1
check_status_code "Period negativo" "400" "test_3_2.json"

# Test 3.3: Period = 1 (mínimo es 2)
echo "Test 3.3: Period = 1 (mínimo 2)"
aws lambda invoke \
    --function-name calculateIndicators \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"period":"1"}}' \
    test_3_3.json > /dev/null 2>&1
check_status_code "Period = 1" "400" "test_3_3.json"

# Test 3.4: Period > 200
echo "Test 3.4: Period > 200 (300)"
aws lambda invoke \
    --function-name calculateIndicators \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"period":"300"}}' \
    test_3_4.json > /dev/null 2>&1
check_status_code "Period > 200" "400" "test_3_4.json"

# Test 3.5: Period no numérico
echo "Test 3.5: Period no numérico (xyz)"
aws lambda invoke \
    --function-name calculateIndicators \
    --cli-binary-format raw-in-base64-out \
    --payload '{"pathParameters":{"symbol":"AAPL"},"queryStringParameters":{"period":"xyz"}}' \
    test_3_5.json > /dev/null 2>&1
check_status_code "Period no numérico" "400" "test_3_5.json"

echo ""
echo "=========================================="
echo "📊 RESULTADOS FINALES"
echo "=========================================="
echo ""
echo "✅ Tests exitosos: $PASS"
echo "❌ Tests fallidos: $FAIL"
echo "📊 Total: $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 ¡TODOS LOS TESTS PASARON!"
    echo "=========================================="
    exit 0
else
    echo "⚠️  Algunos tests fallaron. Revisar arriba."
    echo "=========================================="
    exit 1
fi
