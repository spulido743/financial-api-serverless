# Lambda Function: calculateIndicators

## Descripción
Calcula indicadores técnicos financieros para análisis de acciones.

## Trigger
API Gateway: `GET /analyze/{symbol}`

## Indicadores Calculados

### Medias Móviles
- **SMA-5**: Simple Moving Average (5 días)
- **SMA-10**: Simple Moving Average (10 días)
- **SMA-20**: Simple Moving Average (20 días)
- **EMA-12**: Exponential Moving Average (12 días)
- **EMA-26**: Exponential Moving Average (26 días)

### Volatilidad
- Desviación estándar como % del precio promedio

### Soporte y Resistencia
- Nivel máximo (resistencia)
- Nivel mínimo (soporte)

### Bollinger Bands
- Banda superior (SMA + 2σ)
- Banda media (SMA)
- Banda inferior (SMA - 2σ)

### Análisis de Precio
- Precio actual vs promedio
- Cambio absoluto y porcentual

### Recomendación
- BUY / SELL / HOLD
- Razón de la recomendación
- Nivel de confianza

## Response Example
```json
{
  "symbol": "AAPL",
  "indicators": {
    "current_price": 185.50,
    "sma_20": 183.25,
    "ema_12": 184.80,
    "volatility": 2.34,
    "bollinger_bands": {
      "upper": 188.50,
      "middle": 183.25,
      "lower": 178.00
    },
    "recommendation": {
      "action": "BUY",
      "reason": "Indicadores mayormente alcistas",
      "confidence": "medium"
    }
  }
}
```

## Requirements
- Mínimo 5 registros históricos
- Datos de los últimos 30 días
