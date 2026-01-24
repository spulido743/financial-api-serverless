# 📖 Documentación de la API

## 🌐 Base URL
```
https://API_ID.execute-api.us-east-1.amazonaws.com/prod
```
*(Se actualizará cuando se despliegue)*

## 🔐 Autenticación
**Fase actual:** API pública (sin autenticación)  
**Futuro:** API Keys o AWS Cognito

---

## 📡 Endpoints

### 1. Guardar Precio de Acción
**POST** `/stock`

Guarda el precio de una acción en DynamoDB.

**Request:**
```json
{
  "symbol": "AAPL",
  "price": 180.50
}
```

**Response 200:**
```json
{
  "message": "Precio de AAPL guardado: $180.50",
  "timestamp": 1706097000
}
```

---

### 2. Consultar Último Precio
**GET** `/stock/{symbol}`

**Response 200:**
```json
{
  "symbol": "AAPL",
  "price": 180.50,
  "date": "2026-01-24T15:30:00Z"
}
```

---

### 3. Análisis Técnico
**GET** `/analyze/{symbol}`

**Response 200:**
```json
{
  "symbol": "AAPL",
  "sma_20": 178.45,
  "rsi": 62.3,
  "recommendation": "BUY"
}
```

---

## 📊 Códigos HTTP
- `200` OK
- `400` Bad Request
- `404` Not Found  
- `500` Internal Server Error

## 🚀 Ejemplos cURL
```bash
# Guardar precio
curl -X POST https://YOUR-API/prod/stock \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","price":180.50}'

# Consultar precio
curl https://YOUR-API/prod/stock/AAPL
```
