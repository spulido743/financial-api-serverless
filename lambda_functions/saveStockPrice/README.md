# Lambda Function: saveStockPrice

## Descripción
Guarda el precio de una acción en DynamoDB.

## Input Event
```json
{
  "symbol": "AAPL",
  "price": 180.50,
  "volume": 52000000,
  "change": 2.15,
  "change_percent": 1.20
}
```

## Output Success (200)
```json
{
  "message": "Precio de AAPL guardado exitosamente",
  "data": {
    "symbol": "AAPL",
    "price": 180.50,
    "timestamp": 1706097000,
    "date": "2026-01-24T15:30:00Z"
  }
}
```

## Output Error (400)
```json
{
  "error": "Missing required field: symbol",
  "message": "Debe proporcionar el símbolo de la acción"
}
```

## Variables de Entorno
- `TABLE_NAME`: Nombre de la tabla DynamoDB (default: FinancialData)

## Permisos IAM Requeridos
- dynamodb:PutItem en tabla FinancialData
- logs:CreateLogGroup
- logs:CreateLogStream
- logs:PutLogEvents