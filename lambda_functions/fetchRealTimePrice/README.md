# Lambda Function: fetchRealTimePrice

## Descripción
Obtiene el precio real de una acción desde Alpha Vantage API y lo guarda en DynamoDB.

## Trigger
API Gateway: `POST /stock/fetch/{symbol}`

## External API
- **Service:** Alpha Vantage
- **Endpoint:** GLOBAL_QUOTE
- **Rate Limit:** 5 calls/minute, 500 calls/day (Free Tier)

## Path Parameters
- `symbol` (required): Símbolo de la acción (ej: AAPL, GOOGL)

## Environment Variables
- `ALPHA_VANTAGE_API_KEY` (required): API Key de Alpha Vantage
- `TABLE_NAME`: Nombre de la tabla DynamoDB (default: FinancialData)

## Dependencies
- `requests`: HTTP library (via Lambda Layer)
- `boto3`: AWS SDK (included in Lambda)

## Response Success (200)
```json
{
  "message": "Precio de AAPL actualizado desde Alpha Vantage",
  "symbol": "AAPL",
  "price": 185.50,
  "change": 2.15,
  "change_percent": "1.17%",
  "volume": 58000000,
  "latest_trading_day": "2026-01-29",
  "timestamp": 1769720353,
  "source": "alpha_vantage"
}
```

## Response Error (429) - Rate Limit
```json
{
  "error": "rate_limit",
  "message": "Rate limit de Alpha Vantage alcanzado. Espera 1 minuto.",
  "symbol": "AAPL"
}
```

## Response Error (400) - Invalid Symbol
```json
{
  "error": "invalid_symbol",
  "message": "Símbolo inválido: XYZ123"
}
```

## Notes
- Los datos son del último día de trading
- Puede haber retraso de 15 minutos (datos en tiempo real requieren plan paid)
- Mercado cerrado: devuelve último precio conocido
