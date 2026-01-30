"""
Lambda Function: fetchRealTimePrice
Descripción: Obtiene precio real de una acción desde Alpha Vantage y lo guarda en DynamoDB
Trigger: API Gateway POST /stock/fetch/{symbol}
"""

import json
import boto3
import requests
from decimal import Decimal
from datetime import datetime
import os

# Configuración
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'FinancialData')
table = dynamodb.Table(table_name)

def fetch_stock_data(symbol):
    """
    Obtener datos de Alpha Vantage
    
    Args:
        symbol: Símbolo de la acción (ej: AAPL)
    
    Returns:
        dict con datos de la acción o None si hay error
    """
    
    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError("ALPHA_VANTAGE_API_KEY no configurada")
    
    print(f"🌐 Consultando Alpha Vantage para {symbol}...")
    
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"📡 Respuesta de Alpha Vantage: {json.dumps(data)[:200]}...")
        
        # Verificar si hay datos
        if "Global Quote" not in data:
            if "Note" in data:
                # Rate limit alcanzado
                return {
                    'error': 'rate_limit',
                    'message': 'Rate limit de Alpha Vantage alcanzado. Espera 1 minuto.'
                }
            elif "Error Message" in data:
                return {
                    'error': 'invalid_symbol',
                    'message': f'Símbolo inválido: {symbol}'
                }
            else:
                return {
                    'error': 'no_data',
                    'message': 'No se recibieron datos de Alpha Vantage'
                }
        
        quote = data["Global Quote"]
        
        # Extraer datos relevantes
        stock_data = {
            'symbol': quote.get("01. symbol", symbol),
            'price': float(quote.get("05. price", 0)),
            'volume': int(quote.get("06. volume", 0)),
            'latest_trading_day': quote.get("07. latest trading day", ""),
            'previous_close': float(quote.get("08. previous close", 0)),
            'change': float(quote.get("09. change", 0)),
            'change_percent': quote.get("10. change percent", "0%").replace("%", "")
        }
        
        print(f"✅ Datos obtenidos: ${stock_data['price']}")
        
        return stock_data
        
    except requests.exceptions.Timeout:
        return {
            'error': 'timeout',
            'message': 'Timeout al consultar Alpha Vantage'
        }
    except requests.exceptions.RequestException as e:
        return {
            'error': 'network_error',
            'message': f'Error de red: {str(e)}'
        }
    except Exception as e:
        return {
            'error': 'unknown',
            'message': f'Error inesperado: {str(e)}'
        }

def save_to_dynamodb(stock_data):
    """
    Guardar datos en DynamoDB
    
    Args:
        stock_data: dict con datos de la acción
    
    Returns:
        True si se guardó exitosamente
    """
    
    try:
        timestamp = int(datetime.now().timestamp())
        current_date = datetime.now().isoformat()
        
        item = {
            'symbol': stock_data['symbol'],
            'timestamp': timestamp,
            'price': Decimal(str(stock_data['price'])),
            'date': current_date,
            'volume': stock_data['volume'],
            'change': Decimal(str(stock_data['change'])),
            'change_percent': Decimal(str(stock_data['change_percent'])),
            'source': 'alpha_vantage',
            'latest_trading_day': stock_data['latest_trading_day']
        }
        
        print(f"💾 Guardando en DynamoDB: {stock_data['symbol']} = ${stock_data['price']}")
        
        response = table.put_item(Item=item)
        
        print(f"✅ Guardado exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar en DynamoDB: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    Handler principal de la función Lambda
    """
    
    print(f"📥 Event recibido: {json.dumps(event, default=str)}")
    
    try:
        # Obtener símbolo del path parameter
        if 'pathParameters' not in event or not event['pathParameters']:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing path parameter',
                    'message': 'Debe proporcionar el símbolo en la URL: /stock/fetch/{symbol}'
                })
            }
        
        symbol = event['pathParameters'].get('symbol', '').upper()
        
        if not symbol:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid symbol',
                    'message': 'El símbolo no puede estar vacío'
                })
            }
        
        print(f"🎯 Procesando símbolo: {symbol}")
        
        # Obtener datos de Alpha Vantage
        stock_data = fetch_stock_data(symbol)
        
        # Verificar si hubo error
        if isinstance(stock_data, dict) and 'error' in stock_data:
            status_code = 429 if stock_data['error'] == 'rate_limit' else 400
            return {
                'statusCode': status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': stock_data['error'],
                    'message': stock_data['message'],
                    'symbol': symbol
                })
            }
        
        # Guardar en DynamoDB
        save_to_dynamodb(stock_data)
        
        # Respuesta exitosa
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Precio de {symbol} actualizado desde Alpha Vantage',
                'symbol': stock_data['symbol'],
                'price': stock_data['price'],
                'change': stock_data['change'],
                'change_percent': f"{stock_data['change_percent']}%",
                'volume': stock_data['volume'],
                'latest_trading_day': stock_data['latest_trading_day'],
                'timestamp': int(datetime.now().timestamp()),
                'source': 'alpha_vantage'
            })
        }
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
