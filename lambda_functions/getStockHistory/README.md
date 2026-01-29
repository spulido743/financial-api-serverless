# Lambda Function: getStockHistory

## Descripción
Obtiene el histórico de precios de una acción.

## Trigger
API Gateway: `GET /stock/{symbol}/history`

## Path Parameters
- `symbol` (required): Símbolo de la acción

## Query Parameters
- `days` (optional): Número de días de histórico (default: 30, max: 365)
- `limit` (optional): Máximo de registros (default: 100, max: 500)

## Ejemplo Request
```
GET /stock/AAPL/history?days=7&limit=50
```

## Response Success (200)
```json
{
  "symbol": "AAPL",
  "period": {
    "days": 7,
    "from": "2026-01-22T...",
    "to": "2026-01-29T..."
  },
  "statistics": {
    "count": 5,
    "max": 185.50,
    "min": 180.50,
    "avg": 183.25,
    "latest": 185.50,
    "oldest": 180.50
  },
  "data": [
    {
      "timestamp": 1769720353,
      "date": "2026-01-29T...",
      "price": 185.50,
      "volume": 60000000
    },
    ...
  ]
}
```
