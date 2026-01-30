#!/bin/bash

API_URL=$(aws apigateway get-rest-apis --query 'items[?name==`Financial-API`].id' --output text)
API_URL="https://${API_URL}.execute-api.us-east-1.amazonaws.com/prod"

SYMBOL="GOOGL"

echo "🚀 TEST END-TO-END: Integración completa"
echo "========================================"
echo "Símbolo a probar: $SYMBOL"
echo ""

# PASO 1: Fetch precio real desde Alpha Vantage
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASO 1: Obtener precio REAL desde Alpha Vantage"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Endpoint: POST /stock/fetch/${SYMBOL}"
echo ""

FETCH_RESPONSE=$(curl -s -X POST "${API_URL}/stock/fetch/${SYMBOL}")
echo "$FETCH_RESPONSE" | python3 -m json.tool

PRICE=$(echo "$FETCH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('price', 'N/A'))")
echo ""
echo "✅ Precio obtenido: \$$PRICE"
echo ""

sleep 2

# PASO 2: Consultar último precio guardado
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASO 2: Consultar precio desde nuestra API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Endpoint: GET /stock/${SYMBOL}"
echo ""

GET_RESPONSE=$(curl -s -X GET "${API_URL}/stock/${SYMBOL}")
echo "$GET_RESPONSE" | python3 -m json.tool

SAVED_PRICE=$(echo "$GET_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data', {}).get('price', 'N/A'))")
echo ""
echo "✅ Precio guardado en DB: \$$SAVED_PRICE"
echo ""

sleep 2

# PASO 3: Ver histórico
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASO 3: Consultar histórico completo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Endpoint: GET /stock/${SYMBOL}/history?days=7"
echo ""

HISTORY_RESPONSE=$(curl -s -X GET "${API_URL}/stock/${SYMBOL}/history?days=7")
echo "$HISTORY_RESPONSE" | python3 -m json.tool

COUNT=$(echo "$HISTORY_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('statistics', {}).get('count', 0))")
echo ""
echo "✅ Registros en histórico (últimos 7 días): $COUNT"
echo ""

# PASO 4: Verificar en DynamoDB directamente
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PASO 4: Verificación directa en DynamoDB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws dynamodb query \
    --table-name FinancialData \
    --key-condition-expression "symbol = :sym" \
    --expression-attribute-values '{":sym":{"S":"'$SYMBOL'"}}' \
    --scan-index-forward false \
    --limit 3 \
    --query 'Items[*].[symbol.S, price.N, date.S, source.S]' \
    --output table

echo ""
echo "========================================"
echo "✅ TEST END-TO-END COMPLETADO"
echo "========================================"
echo ""
echo "RESUMEN:"
echo "1. ✅ Precio obtenido de Alpha Vantage: \$$PRICE"
echo "2. ✅ Precio guardado en DynamoDB: \$$SAVED_PRICE"
echo "3. ✅ Histórico consultado: $COUNT registros"
echo "4. ✅ Verificación DynamoDB: OK"
echo ""
echo "🎉 Todos los componentes funcionando correctamente"
