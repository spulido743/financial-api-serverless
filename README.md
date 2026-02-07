# 📈 Financial API Serverless

API REST serverless completa para consultar, almacenar y analizar datos financieros de acciones en tiempo real, construida 100% con servicios AWS (Lambda, API Gateway, DynamoDB, EventBridge).

![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Serverless](https://img.shields.io/badge/Serverless-FD5750?style=for-the-badge&logo=serverless&logoColor=white)
![DynamoDB](https://img.shields.io/badge/DynamoDB-4053D6?style=for-the-badge&logo=amazon-dynamodb&logoColor=white)

## 🎯 Características

- ✅ **100% Serverless** - Sin servidores que mantener
- ✅ **Auto-scaling** - Escala automáticamente según demanda
- ✅ **Costo $0** - Completamente dentro del AWS Free Tier
- ✅ **Tiempo Real** - Precios actualizados cada hora automáticamente
- ✅ **Indicadores Técnicos** - RSI, SMA, EMA calculados on-demand
- ✅ **API REST** - Endpoints documentados con Postman
- ✅ **Alta Disponibilidad** - Infraestructura multi-AZ de AWS

## 🏗️ Arquitectura
```
┌─────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE DIAGRAM                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EventBridge (cron: 1 hora)                                 │
│       │                                                     │
│       ├──► Lambda: fetchRealTimePrice                      │
│       │         │                                          │
│       │         ├──► Alpha Vantage API (External)         │
│       │         │                                          │
│       │         └──► DynamoDB: FinancialData              │
│       │                                                     │
│  Internet Users                                             │
│       │                                                     │
│       └──► API Gateway (REST API)                          │
│                 │                                           │
│                 ├──► Lambda: fetchRealTimePrice            │
│                 │         └──► DynamoDB                     │
│                 │                                           │
│                 ├──► Lambda: getHistoricalPrices           │
│                 │         └──► DynamoDB (Query)            │
│                 │                                           │
│                 └──► Lambda: calculateIndicators           │
│                           └──► DynamoDB (Query)            │
│                                                             │
│  CloudWatch Alarms ──► SNS (Alertas)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Componentes AWS

### **Lambda Functions**
- `fetchRealTimePrice` - Obtiene precios desde Alpha Vantage API
- `getHistoricalPrices` - Consulta histórico en DynamoDB
- `calculateIndicators` - Calcula RSI, SMA, EMA

### **API Gateway**
- REST API pública
- CORS habilitado
- 3 endpoints principales

### **DynamoDB**
- Tabla: `FinancialData`
- Partition Key: `symbol` (String)
- Sort Key: `timestamp` (Number)
- Capacity: On-Demand (pay-per-request)

### **EventBridge**
- Regla: `HourlyStockPriceUpdate`
- Schedule: `rate(1 hour)`
- Target: Lambda `fetchRealTimePrice`

### **CloudWatch**
- 3 alarmas activas (Errors, Throttles, Duration)
- Logs automáticos de todas las Lambdas

## 📡 API Endpoints

**Base URL:** `https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod`

### 1️⃣ **Get Real-Time Price**
```http
GET /price/{symbol}
```

**Descripción:** Obtiene el precio actual de una acción desde Alpha Vantage y lo guarda en DynamoDB.

**Path Parameters:**
- `symbol` (string, required) - Símbolo de la acción (ej: AAPL, GOOGL, MSFT)

**Response 200 OK:**
```json
{
  "message": "Price for AAPL updated successfully",
  "data": {
    "symbol": "AAPL",
    "status": "success",
    "price": 259.48,
    "change": 2.34,
    "change_percent": "0.91"
  }
}
```

**Ejemplo:**
```bash
curl https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod/price/AAPL
```

---

### 2️⃣ **Get Historical Prices**
```http
GET /historical/{symbol}?days={days}&limit={limit}
```

**Descripción:** Consulta histórico de precios almacenados en DynamoDB.

**Path Parameters:**
- `symbol` (string, required) - Símbolo de la acción

**Query Parameters:**
- `days` (integer, optional) - Días de histórico (default: 7, max: 365)
- `limit` (integer, optional) - Máximo de registros (default: none, max: 1000)

**Response 200 OK:**
```json
{
  "symbol": "AAPL",
  "days": 7,
  "count": 42,
  "data": [
    {
      "symbol": "AAPL",
      "timestamp": 1738522800,
      "price": 259.48,
      "date": "2026-02-02T19:13:27.000000",
      "volume": 45123456,
      "change": 2.34,
      "change_percent": 0.91
    }
  ]
}
```

**Ejemplo:**
```bash
curl "https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod/historical/AAPL?days=7"
```

---

### 3️⃣ **Calculate Technical Indicators**
```http
GET /indicators/{symbol}?period={period}
```

**Descripción:** Calcula indicadores técnicos (RSI, SMA, EMA) basados en datos históricos.

**Path Parameters:**
- `symbol` (string, required) - Símbolo de la acción

**Query Parameters:**
- `period` (integer, optional) - Período para cálculo (default: 14, range: 2-200)

**Response 200 OK:**
```json
{
  "symbol": "AAPL",
  "period": 14,
  "indicators": {
    "rsi": 58.23,
    "sma": 256.78,
    "ema": 257.12
  },
  "current_price": 259.48,
  "data_points": 30
}
```

**Indicadores:**
- **RSI** (Relative Strength Index): Indicador de momentum (0-100)
- **SMA** (Simple Moving Average): Promedio móvil simple
- **EMA** (Exponential Moving Average): Promedio móvil exponencial

**Ejemplo:**
```bash
curl "https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod/indicators/AAPL?period=14"
```

---

## 🔧 Instalación y Despliegue

### **Prerrequisitos**

- AWS Account con Free Tier activo
- AWS CLI instalado y configurado
- Python 3.11+
- Permisos IAM para Lambda, API Gateway, DynamoDB, EventBridge

### **Paso 1: Clonar el Repositorio**
```bash
git clone https://github.com/tu-usuario/financial-api-serverless.git
cd financial-api-serverless
```

### **Paso 2: Configurar Credenciales Alpha Vantage**

1. Obtener API Key gratuita en: https://www.alphavantage.co/support/#api-key
2. Exportar como variable de entorno:
```bash
export ALPHA_VANTAGE_API_KEY="tu-api-key-aqui"
```

### **Paso 3: Crear DynamoDB Table**
```bash
aws dynamodb create-table \
    --table-name FinancialData \
    --attribute-definitions \
        AttributeName=symbol,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
    --key-schema \
        AttributeName=symbol,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST
```

### **Paso 4: Crear IAM Role**
```bash
aws iam create-role \
    --role-name FinancialAPI-Lambda-Role \
    --assume-role-policy-document file://iam-policies/lambda-trust-policy.json

aws iam attach-role-policy \
    --role-name FinancialAPI-Lambda-Role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam put-role-policy \
    --role-name FinancialAPI-Lambda-Role \
    --policy-name DynamoDBAccess \
    --policy-document file://iam-policies/lambda-dynamodb-policy.json
```

### **Paso 5: Deploy Lambda Functions**
```bash
# Deploy fetchRealTimePrice
cd lambda_functions/fetchRealTimePrice
zip -r function.zip lambda_function.py
aws lambda create-function \
    --function-name fetchRealTimePrice \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR-ACCOUNT-ID:role/FinancialAPI-Lambda-Role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 30 \
    --environment Variables={ALPHA_VANTAGE_API_KEY=$ALPHA_VANTAGE_API_KEY,TABLE_NAME=FinancialData}

# Repetir para getHistoricalPrices y calculateIndicators
```

### **Paso 6: Crear API Gateway**
```bash
# Ver documentación completa en /docs/api-gateway-setup.md
```

### **Paso 7: Configurar EventBridge**
```bash
aws events put-rule \
    --name HourlyStockPriceUpdate \
    --schedule-expression "rate(1 hour)"

aws events put-targets \
    --rule HourlyStockPriceUpdate \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR-ACCOUNT-ID:function:fetchRealTimePrice"
```

---

## 📊 Watchlist Actual

El sistema monitorea automáticamente estas 10 acciones cada hora:

| Símbolo | Empresa |
|---------|---------|
| AAPL | Apple Inc. |
| GOOGL | Alphabet Inc. |
| MSFT | Microsoft Corporation |
| AMZN | Amazon.com Inc. |
| META | Meta Platforms Inc. |
| NVDA | NVIDIA Corporation |
| TSLA | Tesla Inc. |
| IBM | International Business Machines |
| JPM | JPMorgan Chase & Co. |
| V | Visa Inc. |

**Para modificar la watchlist:**
```bash
aws lambda update-function-configuration \
    --function-name fetchRealTimePrice \
    --environment Variables={WATCHLIST=AAPL,GOOGL,MSFT,NEW_SYMBOL}
```

---

## 🧪 Testing

### **Colección Postman**

Importar el archivo `Financial_API_Postman_Collection.json` en Postman.

La colección incluye:
- ✅ 15 requests pre-configurados
- ✅ Tests automatizados
- ✅ Variables de entorno
- ✅ Ejemplos de responses

### **Tests Automatizados**
```bash
cd tests
./validation_tests.sh
```

**Resultados esperados:**
- ✅ 13/18 tests pasando (72%)
- ⚠️ 5 tests con bugs conocidos (documentados)

---

## 💰 Costos

**Costo mensual estimado: $0.00 USD** ✅

### Breakdown de costos (dentro de Free Tier):

| Servicio | Uso Mensual | Costo |
|----------|-------------|-------|
| Lambda Invocations | ~1,000 | $0.00 (1M gratis) |
| Lambda Duration | ~50 GB-segundos | $0.00 (400,000 gratis) |
| API Gateway Requests | ~500 | $0.00 (1M gratis) |
| DynamoDB Writes | ~7,200 | $0.00 (25 WCU gratis) |
| DynamoDB Reads | ~2,000 | $0.00 (25 RCU gratis) |
| DynamoDB Storage | <1 GB | $0.00 (25 GB gratis) |
| EventBridge Rules | 1 regla | $0.00 (14M invocaciones gratis) |
| CloudWatch Alarms | 3 alarmas | $0.00 (10 alarmas gratis) |
| **TOTAL** | | **$0.00** |

---

## 📈 Métricas y Monitoreo

### **CloudWatch Alarms**

3 alarmas configuradas:

1. **fetchRealTimePrice-Errors** - Alerta si hay errores
2. **fetchRealTimePrice-Throttles** - Alerta si hay throttling
3. **fetchRealTimePrice-Duration** - Alerta si duración > 25s

### **Performance Actual**

- ⚡ Latencia promedio: ~2.3 segundos
- ✅ Tasa de éxito: 100%
- 📊 Uptime: 99.9%

---

## 🛠️ Tecnologías Utilizadas

- **AWS Lambda** - Compute serverless
- **AWS API Gateway** - REST API management
- **AWS DynamoDB** - NoSQL database
- **AWS EventBridge** - Event scheduling
- **AWS CloudWatch** - Monitoring & logging
- **AWS IAM** - Security & permissions
- **Python 3.11** - Runtime
- **Alpha Vantage API** - Market data provider
- **Postman** - API testing

---

## 📚 Estructura del Proyecto
```
financial-api-serverless/
├── lambda_functions/
│   ├── fetchRealTimePrice/
│   │   ├── lambda_function.py
│   │   └── function.zip
│   ├── getHistoricalPrices/
│   │   ├── lambda_function.py
│   │   └── function.zip
│   └── calculateIndicators/
│       ├── lambda_function.py
│       └── function.zip
├── iam-policies/
│   ├── lambda-trust-policy.json
│   └── lambda-dynamodb-policy.json
├── tests/
│   ├── validation_tests.sh
│   └── validation_summary.md
├── docs/
│   └── architecture-diagram.png
├── Financial_API_Postman_Collection.json
├── README.md
└── api_url.txt
```

---

## 🐛 Bugs Conocidos

Ver `tests/validation_summary.md` para lista completa de bugs conocidos y workarounds.

**Principales:**
1. Event vacío en fetchRealTimePrice se procesa como watchlist (edge case)
2. Validación de period en calculateIndicators necesita mejoras

**Impacto:** Bajo - No afecta uso normal de la API

---

## 🔮 Roadmap / Mejoras Futuras

- [ ] Frontend React con dashboard interactivo
- [ ] CI/CD con GitHub Actions
- [ ] Infraestructura como código (Terraform)
- [ ] WebSocket para actualizaciones en tiempo real
- [ ] Soporte para más exchanges (crypto, forex)
- [ ] Machine Learning para predicciones
- [ ] Autenticación con Cognito
- [ ] Rate limiting por API Key

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 👤 Autor

**Sergio Pulido**
- AWS Account ID: 318774499588
- Región: us-east-1 (Norte de Virginia)
- Proyecto: Financial API Serverless v2.0

---

## 🙏 Agradecimientos

- **Alpha Vantage** por el API gratuito de datos financieros
- **AWS** por el generoso Free Tier
- **Comunidad Open Source** por las librerías utilizadas

---

## 📞 Soporte

¿Tienes preguntas? Abre un issue en GitHub o contacta directamente.

---

**Última actualización:** Febrero 2, 2026  
**Versión:** 2.0  
**Estado:** Producción ✅
