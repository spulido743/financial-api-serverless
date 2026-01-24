
# 🏗️ Arquitectura del Sistema

## Diagrama de Componentes
```
┌──────────────────────────────────────────────────────────────┐
│                         USUARIO/APP                           │
│                    (Postman, Frontend, CLI)                   │
└────────────────────────────┬─────────────────────────────────┘
                             │ HTTPS
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                      API GATEWAY (REST)                       │
│  ┌────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ POST       │ GET          │ GET          │ GET          │ │
│  │ /stock     │ /stock/{id}  │ /history     │ /analyze     │ │
│  └────────────┴──────────────┴──────────────┴──────────────┘ │
└────────────────────────────┬─────────────────────────────────┘
                             │ Trigger
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                      LAMBDA FUNCTIONS                         │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │ saveStock     │  │ getStock      │  │ fetchRealTime    │ │
│  │ Price         │  │ Price         │  │ Price            │ │
│  └───────────────┘  └───────────────┘  └──────────────────┘ │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │ calculate     │  │ getStock      │  │ getPortfolio     │ │
│  │ Indicators    │  │ History       │  │                  │ │
│  └───────────────┘  └───────────────┘  └──────────────────┘ │
└────────┬──────────────────────┬────────────────┬────────────┘
         │ Query/Write          │ Fetch          │ Logs
         ▼                      ▼                ▼
┌─────────────────┐   ┌──────────────────┐   ┌────────────────┐
│   DYNAMODB      │   │  ALPHA VANTAGE   │   │  CLOUDWATCH    │
│                 │   │      API         │   │                │
│ FinancialData   │   │  (External)      │   │  Logs/Metrics  │
│                 │   │                  │   │                │
│ PK: symbol      │   │  Real-time       │   │  Monitoring    │
│ SK: timestamp   │   │  Stock Prices    │   │  Alarms        │
└─────────────────┘   └──────────────────┘   └────────────────┘
         ▲
         │ Schedule
         │
┌────────┴─────────┐
│   EVENTBRIDGE    │
│                  │
│  Cron: 0 * * * * │
│  (Every hour)    │
└──────────────────┘
```

## Flujo de Datos

### 1. Guardar Precio Manual
```
Usuario → POST /stock → Lambda saveStockPrice → DynamoDB
```

### 2. Consultar Precio
```
Usuario → GET /stock/{symbol} → Lambda getStockPrice → DynamoDB → Usuario
```

### 3. Actualización Automática
```
EventBridge (cada hora) → Lambda fetchRealTimePrice → Alpha Vantage API
                                    ↓
                               DynamoDB
```

### 4. Análisis Técnico
```
Usuario → GET /analyze/{symbol} → Lambda calculateIndicators
                                         ↓
                                  Query DynamoDB (últimos 20-30 días)
                                         ↓
                                  Calcular SMA, RSI, MACD
                                         ↓
                                  Return analysis → Usuario
```

## Componentes

### Frontend/Cliente
- **Postman**: Pruebas de API
- **cURL**: Scripts automatizados
- **(Futuro)** React Dashboard

### API Layer
- **API Gateway**: Punto de entrada único, manejo de CORS, rate limiting

### Compute
- **Lambda Functions**: Serverless, auto-escalable, pago por uso

### Storage
- **DynamoDB**: NoSQL, baja latencia, schema flexible

### External Services
- **Alpha Vantage**: Datos financieros en tiempo real
- **Yahoo Finance** (futuro): Datos históricos complementarios

### Observability
- **CloudWatch Logs**: Logs centralizados
- **CloudWatch Metrics**: Métricas de rendimiento
- **CloudWatch Alarms**: Alertas automáticas

### Automation
- **EventBridge**: Ejecución programada (cron jobs)

## Seguridad

- IAM Roles para Lambda
- API Gateway sin autenticación (Fase 1)
- Secrets Manager para API Keys (futuro)
- VPC para DynamoDB (futuro)

## Escalabilidad

- Lambda: Auto-scaling automático
- DynamoDB: On-demand capacity
- API Gateway: Sin límite en Free Tier

## Costos Estimados

Con Free Tier:
- Lambda: 1M requests/mes gratis
- DynamoDB: 25GB storage gratis
- API Gateway: 1M requests/mes gratis

**Total: $0-2/mes**
EOF

# Commit del diseño
git add docs/ARCHITECTURE.md
git commit -m "📐 Add architecture documentation"
git push origin main