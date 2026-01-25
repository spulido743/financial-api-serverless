#!/bin/bash

FUNCTION_NAME="saveStockPrice"
LOG_GROUP="/aws/lambda/${FUNCTION_NAME}"

echo "📊 Monitoreando logs de Lambda: $FUNCTION_NAME"
echo "Presiona Ctrl+C para salir"
echo "=========================================="

# Obtener logs de los últimos 5 minutos
START_TIME=$(($(date +%s) - 300))000  # 5 minutos atrás en ms

aws logs tail $LOG_GROUP --follow --since 5m
