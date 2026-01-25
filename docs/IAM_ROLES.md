# 🔐 IAM Roles y Permisos

## Rol: FinancialAPI-Lambda-Role

**ARN:** `arn:aws:iam::318774499588:role/FinancialAPI-Lambda-Role`

### Políticas Adjuntas

#### 1. AWSLambdaBasicExecutionRole (AWS Managed)
Permite a Lambda escribir logs en CloudWatch.

**Permisos:**
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

#### 2. FinancialAPI-DynamoDB-Policy (Custom)
Permite operaciones CRUD en DynamoDB.

**Permisos:**
- `dynamodb:PutItem`
- `dynamodb:GetItem`
- `dynamodb:Query`
- `dynamodb:Scan`
- `dynamodb:UpdateItem`
- `dynamodb:DeleteItem`

**Recurso:** `arn:aws:dynamodb:us-east-1:*:table/FinancialData`

### Trust Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## Funciones Lambda que usan este rol

- ✅ saveStockPrice
- 🔄 getStockPrice (futuro)
- 🔄 fetchRealTimePrice (futuro)
- 🔄 calculateIndicators (futuro)

## Fecha de Creación
2026-01-24
