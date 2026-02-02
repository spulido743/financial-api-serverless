"""
Lambda Function: fetchRealTimePrice (ENHANCED FOR EVENTBRIDGE)
Descripción: Obtiene precios reales desde Alpha Vantage
Puede procesar múltiples símbolos cuando es invocada por EventBridge
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

# Lista de símbolos a monitorear (WATCHLIST)
# Lee desde variable de entorno o usa default
watchlist_env = os.environ.get('WATCHLIST', '')
if watchlist_env:
    DEFAULT_WATCHLIST = [s.strip() for s in watchlist_env.split(',')]
else:
    DEFAULT_WATCHLIST = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META',
        'NVDA', 'TSLA', 'IBM', 'JPM', 'V'
    ]

print(f"📋 Watchlist configurada: {DEFAULT_WATCHLIST}")

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'FinancialData')
table = dynamodb.Table(table_name)

def fetch_stock_data(symbol):
    """Obtener datos de Alpha Vantage"""
    
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
        
        if "Global Quote" not in data:
            if "Note" in data:
                return {'error': 'rate_limit', 'message': 'Rate limit alcanzado'}
            elif "Error Message" in data:
                return {'error': 'invalid_symbol', 'message': f'Símbolo inválido: {symbol}'}
            else:
                return {'error': 'no_data', 'message': 'Sin datos'}
        
        quote = data["Global Quote"]
        
        stock_data = {
            'symbol': quote.get("01. symbol", symbol),
            'price': float(quote.get("05. price", 0)),
            'volume': int(quote.get("06. volume", 0)),
            'latest_trading_day': quote.get("07. latest trading day", ""),
            'previous_close': float(quote.get("08. previous close", 0)),
            'change': float(quote.get("09. change", 0)),
            'change_percent': quote.get("10. change percent", "0%").replace("%", "")
        }
        
        print(f"✅ {symbol}: ${stock_data['price']}")
        return stock_data
        
    except Exception as e:
        print(f"❌ Error obteniendo {symbol}: {str(e)}")
        return {'error': 'exception', 'message': str(e)}

def save_to_dynamodb(stock_data):
    """Guardar en DynamoDB"""
    
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
        
        table.put_item(Item=item)
        return True
        
    except Exception as e:
        print(f"❌ Error guardando {stock_data['symbol']}: {str(e)}")
        return False

def lambda_handler(event, context):
    """Handler principal - Soporta API Gateway y EventBridge"""
    
    print(f"📥 Event recibido: {json.dumps(event, default=str)}")
    
    # Determinar el origen del evento
    is_from_eventbridge = 'source' in event and event['source'] == 'aws.events'
    is_from_api_gateway = 'pathParameters' in event
    
    symbols_to_process = []
    
    if is_from_eventbridge:
        # EventBridge: procesar watchlist completa
        print("🤖 Invocación desde EventBridge - Procesando watchlist")
        symbols_to_process = DEFAULT_WATCHLIST
        
    elif is_from_api_gateway:
        # API Gateway: procesar un símbolo específico
        symbol = event['pathParameters'].get('symbol', '').upper()
        if not symbol:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invalid symbol'})
            }
        symbols_to_process = [symbol]
        
    else:
        # Invocación directa con símbolos personalizados
        symbols_to_process = event.get('symbols', DEFAULT_WATCHLIST)
    
    print(f"📊 Procesando {len(symbols_to_process)} símbolos: {symbols_to_process}")
    
    results = {
        'processed': 0,
        'successful': 0,
        'failed': 0,
        'rate_limited': 0,
        'details': []
    }
    
    for symbol in symbols_to_process:
        stock_data = fetch_stock_data(symbol)
        
        if isinstance(stock_data, dict) and 'error' in stock_data:
            results['failed'] += 1
            if stock_data['error'] == 'rate_limit':
                results['rate_limited'] += 1
            results['details'].append({
                'symbol': symbol,
                'status': 'error',
                'message': stock_data['message']
            })
        else:
            if save_to_dynamodb(stock_data):
                results['successful'] += 1
                results['details'].append({
                    'symbol': symbol,
                    'status': 'success',
                    'price': stock_data['price']
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'symbol': symbol,
                    'status': 'error',
                    'message': 'Error saving to DynamoDB'
                })
        
        results['processed'] += 1
    
    print(f"✅ Procesamiento completo: {results['successful']}/{results['processed']} exitosos")
    
    # Respuesta según origen
    if is_from_api_gateway:
        # API Gateway espera formato específico
        if results['successful'] > 0:
            detail = results['details'][0]
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'message': f"Precio de {detail['symbol']} actualizado",
                    'symbol': detail['symbol'],
                    'price': detail.get('price'),
                    'source': 'alpha_vantage'
                })
            }
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': results['details'][0]['message']})
            }
    else:
        # EventBridge o invocación directa
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
