#!/bin/bash

API_URL=$(aws apigateway get-rest-apis --query 'items[?name==`Financial-API`].id' --output text)
API_URL="https://${API_URL}.execute-api.us-east-1.amazonaws.com/prod"

SYMBOLS=("AAPL" "MSFT" "GOOGL" "AMZN" "META")

echo "🧪 TEST: Obtener precios de múltiples acciones"
echo "=============================================="
echo ""

for SYMBOL in "${SYMBOLS[@]}"; do
    echo "📊 Obteniendo $SYMBOL..."
    
    RESPONSE=$(curl -s -X POST "${API_URL}/stock/fetch/${SYMBOL}")
    PRICE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('price', 'ERROR'))" 2>/dev/null || echo "ERROR")
    
    if [ "$PRICE" != "ERROR" ]; then
        echo "   ✅ $SYMBOL: \$$PRICE"
    else
        echo "   ❌ $SYMBOL: Error o rate limit"
    fi
    
    # Esperar 13 segundos entre llamadas (5 calls/min = 12 seg entre cada una)
    if [ "$SYMBOL" != "${SYMBOLS[-1]}" ]; then
        echo "   ⏳ Esperando 13 segundos (rate limit)..."
        sleep 13
    fi
    echo ""
done

echo "=============================================="
echo "✅ Test completado"
echo ""
echo "📊 Ver todos los datos en DynamoDB:"
aws dynamodb scan --table-name FinancialData --query 'Count'
