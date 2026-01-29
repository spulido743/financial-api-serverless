# 📡 Financial API - Información Completa

## 🌐 Endpoints Públicos

### Base URL
```
https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod
```

### POST /stock
**URL Completa:**
```
https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod/stock
```

**Request Body:**
```json
{
  "symbol": "AAPL",
  "price": 185.50,
  "volume": 60000000,
  "change": 4.25,
  "change_percent": 2.35
}
```

**Response 200:**
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Precio de AAPL guardado exitosamente\", ...}"
}
```

**Response 400:**
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Missing required field: symbol\"}"
}
```

---

## 🧪 Ejemplo con cURL

```bash
curl -X POST https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod/stock \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "price": 185.50
  }'
```

---

## 📊 Arquitectura

```
Cliente (Postman/Browser/App)
    ↓ HTTPS
API Gateway: https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod
    ↓ Trigger
Lambda: saveStockPrice
    ↓ Write
DynamoDB: FinancialData
```

---

## 💰 Costos

- API Gateway: GRATIS (Free Tier 1M requests/mes)
- Lambda: GRATIS (Free Tier 1M invocaciones/mes)
- DynamoDB: GRATIS (Free Tier permanente)

**Total:** $0.00 USD/mes ✅

---

## 📅 Creado
Thu Jan 29 21:05:57 UTC 2026

## 🔧 Recursos AWS
- API ID: rd99h9lf9h
- Lambda: saveStockPrice
- DynamoDB Table: FinancialData
- Stage: prod
- Region: us-east-1
