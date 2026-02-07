# Frontend - Financial API Dashboard

Frontend básico pero funcional para interactuar con la API serverless de datos financieros.

## 🚀 Cómo usar

1. Abre `index.html` en tu navegador (no requiere servidor local para pruebas básicas)
2. La interfaz te permite:
   - Guardar precios manualmente
   - Consultar último precio
   - Ver histórico
   - Analizar técnicamente
   - Ver portfolio completo
   - Actualizar precios desde Alpha Vantage

## 📁 Estructura de archivos

```
frontend/
├── index.html    # Página principal
├── styles.css    # Estilos responsive
├── script.js     # Lógica de interacción con API
└── README.md     # Este archivo
```

## 🔧 Configuración

- **API URL**: Hardcodeada en `script.js` como `https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod`
- **CORS**: Ya configurado en las respuestas de las Lambdas (`Access-Control-Allow-Origin: *`)

## 📱 Características

- **Responsive**: Funciona en móviles y desktop
- **Real-time feedback**: Indicadores de carga y errores
- **Formateo de datos**: Monedas, fechas, JSON legible
- **Validación**: Campos requeridos y tipos de datos
- **Manejo de errores**: Muestra mensajes amigables

## 🧪 Pruebas rápidas

1. **Guardar precio**:
   - Símbolo: `AAPL`
   - Precio: `185.50`
   - Click en "Guardar"

2. **Consultar precio**:
   - Símbolo: `AAPL`
   - Click en "Consultar"

3. **Ver portfolio**:
   - Click en "Ver Portfolio Completo"

## ⚠️ Notas

- El frontend es **estático** (no hay backend propio)
- Las llamadas son directas a API Gateway (CORS habilitado)
- Para producción, considera:
  - Servir desde S3 + CloudFront
  - Autenticación (API Keys/Cognito)
  - Rate limiting en el frontend

## 🐛 Troubleshooting

- **CORS errors**: Asegúrate que las Lambdas incluyan el header `Access-Control-Allow-Origin: *`
- **404 errors**: Verifica que la API URL sea correcta y los recursos estén desplegados
- **Timeouts**: Algunas operaciones (análisis técnico) pueden tardar si hay muchos datos
