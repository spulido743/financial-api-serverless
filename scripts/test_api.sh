#!/bin/bash

API_URL=$(cat .api-url.txt 2>/dev/null)

if [ -z "$API_URL" ]; then
    echo "❌ No se encontró la URL de la API"
    echo "Ejecuta primero el paso 17"
    exit 1
fi

ENDPOINT="${API_URL}/stock"

echo "🧪 Testing Financial API"
echo "========================"
echo "Endpoint: $ENDPOINT"
echo ""

# Test 1: AAPL
echo "📊 Test 1: Guardar AAPL"
curl -X POST $ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{
        "symbol": "AAPL",
        "price": 185.50,
        "volume": 60000000,
        "change": 4.25
    }' \
    -w "\nStatus: %{http_code}\n" \
    | python3 -m json.tool
echo ""

# Test 2: GOOGL
echo "📊 Test 2: Guardar GOOGL"
curl -X POST $ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{
        "symbol": "GOOGL",
        "price": 148.20
    }' \
    -w "\nStatus: %{http_code}\n" \
    | python3 -m json.tool
echo ""

# Test 3: Error - Missing symbol
echo "❌ Test 3: Error - Sin symbol"
curl -X POST $ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{
        "price": 100.00
    }' \
    -w "\nStatus: %{http_code}\n" \
    | python3 -m json.tool
echo ""

# Test 4: Error - Missing price
echo "❌ Test 4: Error - Sin price"
curl -X POST $ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{
        "symbol": "TSLA"
    }' \
    -w "\nStatus: %{http_code}\n" \
    | python3 -m json.tool
echo ""

# Verificar DynamoDB
echo "📊 Verificando datos en DynamoDB..."
aws dynamodb scan --table-name FinancialData --query 'Count'

echo ""
echo "✅ Tests completados"
