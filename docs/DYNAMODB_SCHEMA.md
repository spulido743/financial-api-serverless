
# 📊 DynamoDB Schema - FinancialData

## Table Configuration

**Table Name:** `FinancialData`  
**Region:** `us-east-1`  
**Capacity Mode:** On-demand  
**Encryption:** AWS owned key

## Keys

### Partition Key (PK)
- **Attribute:** `symbol`
- **Type:** String
- **Description:** Símbolo bursátil (ej: AAPL, GOOGL, MSFT)
- **Example:** "AAPL"

### Sort Key (SK)
- **Attribute:** `timestamp`
- **Type:** Number
- **Description:** Unix timestamp (segundos desde 1970)
- **Example:** 1706097000

## Item Schema
```json
{
  "symbol": "AAPL",              // Partition Key (String)
  "timestamp": 1706097000,       // Sort Key (Number)
  "price": 180.50,               // Number
  "date": "2026-01-24T15:30:00Z", // String (ISO 8601)
  "volume": 52000000,            // Number (optional)
  "change": 2.15,                // Number (optional)
  "change_percent": 1.20         // Number (optional)
}
```

## Access Patterns

### 1. Obtener último precio de un símbolo
```
Query:
  PK = "AAPL"
  SK = MAX (último timestamp)
```

### 2. Obtener histórico de un símbolo
```
Query:
  PK = "AAPL"
  SK BETWEEN timestamp_inicio AND timestamp_fin
```

### 3. Todos los símbolos únicos
```
Scan: (solo para admin/debug, no eficiente)
```

## Capacity & Costs

**Read Capacity:** On-demand (auto-scaling)  
**Write Capacity:** On-demand (auto-scaling)

**Free Tier:**
- 25GB storage
- 200M read requests/month
- 25M write requests/month

**Projected usage:**
- Writes: ~1,000/day = 30k/month ✅ Free
- Reads: ~5,000/day = 150k/month ✅ Free
- Storage: ~10MB ✅ Free

## Indexes

**Global Secondary Indexes (GSI):** None (for now)  
**Local Secondary Indexes (LSI):** None

## Backup

**Point-in-time recovery:** Disabled (for now, save costs)  
**Backups:** On-demand manual backups

## Created

**Date:** 2026-01-24  
**By:** sergio  
**Account:** 318774499588
