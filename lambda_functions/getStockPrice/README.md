# Lambda Function: getStockPrice

## Descripción
Consulta el último precio registrado de una acción en DynamoDB.

## Trigger
API Gateway: `GET /stock/{symbol}`

## Path Parameters
- `symbol` (required): Símbolo de la acción (ej: AAPL, GOOGL)

## Ejemplo Request
```
GET /stock/AAPL
```

## Response Success (200)
```json
{
  "symbol": "AAPL",
  "data": {
    "symbol": "AAPL",
    "price": 185.50,
    "timestamp": 1769720353,
    "date": "2026-01-29T20:59:13Z",
    "volume": 60000000,
    "change": 4.25,
    "change_percent": 2.35
  },
  "message": "Último precio de AAPL obtenido exitosamente"
}
```

## Response Error (404)
```json
{
  "error": "Symbol not found",
  "message": "No se encontraron datos para el símbolo XYZ"
}
```

## Variables de Entorno
- `TABLE_NAME`: Nombre de la tabla DynamoDB (default: FinancialData)

## Permisos IAM Requeridos
- dynamodb:Query en tabla FinancialData
- logs:CreateLogGroup
- logs:CreateLogStream
- logs:PutLogEvents