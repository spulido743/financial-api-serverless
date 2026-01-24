# 🚀 API REST Serverless - Análisis Financiero

[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20DynamoDB%20%7C%20API%20Gateway-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-En%20Desarrollo-yellow)](https://github.com)

## 📊 Descripción
API serverless en AWS para análisis financiero en tiempo real. Proyecto de aprendizaje AWS Solutions Architect Associate.

## 🏗️ Arquitectura
```
Usuario → API Gateway → Lambda → DynamoDB
                          ↓
                     CloudWatch
```

## 🛠️ Stack
- AWS Lambda (Python 3.11)
- DynamoDB
- API Gateway
- CloudWatch
- EventBridge
- Alpha Vantage API

## 📁 Estructura
```
financial-api-serverless/
├── lambda_functions/       # Código Lambda
├── docs/                   # Documentación
├── tests/                  # Pruebas
├── iam-policies/          # Políticas IAM
└── scripts/               # Scripts de deploy
```

## 📅 Roadmap
- [x] ✅ Configuración AWS (Semana 1-2)
- [ ] 🔄 DynamoDB (Semana 3)
- [ ] 🔄 Primera Lambda (Semana 4)
- [ ] 🔄 API Gateway (Semana 5-6)
- [ ] 🔄 APIs externas (Semana 7-8)
- [ ] 🔄 Análisis financiero (Semana 9-10)
- [ ] 🔄 Automatización (Semana 11-12)

## 🚀 Quick Start

### Prerequisitos
```bash
# Verificar AWS CLI
aws --version

# Verificar Python
python3 --version
```

### Probar API externa
```bash
# Editar tests/test_alpha_vantage.py con tu API Key
python3 tests/test_alpha_vantage.py
```

## 💰 Costos
Con Free Tier: **$0 - $2/mes**

## 👤 Autor
**Sergio Pulido**  
Estudiante de Administración Financiera e Ingeniería de Sistemas  
IST @ NTT Data

## 📚 Referencias
- [Curso AWS SAA-C03](https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/)
- [AWS Lambda Docs](https://docs.aws.amazon.com/lambda/)
- [Alpha Vantage API](https://www.alphavantage.co/documentation/)

---
**Estado:** 🟡 Fase 1 - Preparación (70% completo)  
**Última actualización:** Enero 2026
