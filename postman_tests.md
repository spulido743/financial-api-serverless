# 🧪 Tests para Postman

## Test 1: Guardar AAPL
```json
POST /stock
{
  "symbol": "AAPL",
  "price": 185.50,
  "volume": 60000000
}
```
**Esperado:** 200 OK

---

## Test 2: Guardar GOOGL
```json
POST /stock
{
  "symbol": "GOOGL",
  "price": 148.20
}
```
**Esperado:** 200 OK

---

## Test 3: Error - Sin symbol
```json
POST /stock
{
  "price": 100.00
}
```
**Esperado:** 400 Bad Request

---

## Test 4: Error - Sin price
```json
POST /stock
{
  "symbol": "TSLA"
}
```
**Esperado:** 400 Bad Request

---

## Test 5: Precio con decimales
```json
POST /stock
{
  "symbol": "MSFT",
  "price": 425.7896
}
```
**Esperado:** 200 OK

