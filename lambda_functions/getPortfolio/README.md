# Lambda Function: getPortfolio

## Descripción
Obtiene todos los símbolos únicos guardados en DynamoDB con sus últimos precios.

## Trigger
API Gateway: `GET /portfolio`

## Response Example
```json
{
  "portfolio": [
    {
      "symbol": "AAPL",
      "price": 259.48,
      "last_updated": "2026-01-31T16:31:45Z",
      "volume": 92443408,
      "change_percent": 0.46
    },
    {
      "symbol": "GOOGL",
      "price": 148.20,
      "last_updated": "2026-01-30T12:00:00Z"
    }
  ],
  "statistics": {
    "total_symbols": 8,
    "total_records": 45,
    "price_stats": {
      "highest": 615.30,
      "lowest": 142.80,
      "average": 245.50
    },
    "symbols_list": ["AAPL", "GOOGL", "IBM", ...]
  }
}
```

## Features
- Devuelve solo el precio más reciente de cada símbolo
- Ordenado alfabéticamente
- Estadísticas del portfolio completo
- Lista de todos los símbolos disponibles
