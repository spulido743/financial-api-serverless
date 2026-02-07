"""
Lambda Function: fetchRealTimePrice (PRODUCTION v2.0)
Descripción: Obtiene precios reales desde Alpha Vantage
Features: Batch processing, error handling robusto, validaciones
"""

import json
import boto3
import requests
from decimal import Decimal, InvalidOperation
from datetime import datetime
import os
import traceback

# ==================== CONFIGURACIÓN ====================
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
TABLE_NAME = os.environ.get('TABLE_NAME', 'FinancialData')

# Watchlist configurable
watchlist_env = os.environ.get('WATCHLIST', '')
if watchlist_env:
    DEFAULT_WATCHLIST = [s.strip().upper() for s in watchlist_env.split(',')]
else:
    DEFAULT_WATCHLIST = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 
                        'NVDA', 'TSLA', 'IBM', 'JPM', 'V']

# Cliente DynamoDB
try:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
except Exception as e:
    print(f"❌ Error inicializando DynamoDB: {str(e)}")
    table = None

# ==================== VALIDACIONES ====================

def validate_symbol(symbol):
    """Validar formato de símbolo de acción"""
    if not symbol:
        return False, "Symbol is required"
    
    if not isinstance(symbol, str):
        return False, "Symbol must be a string"
    
    symbol = symbol.strip().upper()
    
    if len(symbol) < 1 or len(symbol) > 5:
        return False, "Symbol must be 1-5 characters"
    
    if not symbol.isalpha():
        return False, "Symbol must contain only letters"
    
    return True, symbol

def validate_api_key():
    """Validar que API key esté configurada"""
    if not ALPHA_VANTAGE_API_KEY:
        return False, "ALPHA_VANTAGE_API_KEY not configured"
    
    if len(ALPHA_VANTAGE_API_KEY) < 10:
        return False, "Invalid ALPHA_VANTAGE_API_KEY format"
    
    return True, ALPHA_VANTAGE_API_KEY

def validate_price_data(data):
    """Validar que los datos de precio sean válidos"""
    required_fields = ['symbol', 'price', 'volume', 'change']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validar tipos de datos
    try:
        price = float(data['price'])
        if price <= 0:
            return False, "Price must be positive"
        
        volume = int(data['volume'])
        if volume < 0:
            return False, "Volume cannot be negative"
        
    except (ValueError, TypeError) as e:
        return False, f"Invalid data type: {str(e)}"
    
    return True, data

# ==================== API FUNCTIONS ====================

def fetch_stock_data(symbol):
    """
    Obtener datos de Alpha Vantage con error handling robusto
    
    Returns:
        dict: Stock data si exitoso
        dict: Error dict si falla {'error': str, 'message': str, 'http_code': int}
    """
    
    # Validar API key
    is_valid, result = validate_api_key()
    if not is_valid:
        return {
            'error': 'configuration_error',
            'message': result,
            'http_code': 500
        }
    
    # Validar símbolo
    is_valid, validated_symbol = validate_symbol(symbol)
    if not is_valid:
        return {
            'error': 'validation_error',
            'message': validated_symbol,
            'http_code': 400
        }
    
    print(f"🌐 Fetching data for {validated_symbol}...")
    
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": validated_symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(
            ALPHA_VANTAGE_URL, 
            params=params, 
            timeout=10
        )
        response.raise_for_status()
        
    except requests.exceptions.Timeout:
        return {
            'error': 'timeout',
            'message': f'Request timeout for {validated_symbol}',
            'http_code': 504
        }
    except requests.exceptions.ConnectionError:
        return {
            'error': 'connection_error',
            'message': 'Failed to connect to Alpha Vantage API',
            'http_code': 503
        }
    except requests.exceptions.HTTPError as e:
        return {
            'error': 'http_error',
            'message': f'HTTP error: {e.response.status_code}',
            'http_code': e.response.status_code
        }
    except Exception as e:
        return {
            'error': 'request_error',
            'message': f'Request failed: {str(e)}',
            'http_code': 500
        }
    
    # Parse response
    try:
        data = response.json()
    except json.JSONDecodeError:
        return {
            'error': 'parse_error',
            'message': 'Invalid JSON response from API',
            'http_code': 502
        }
    
    # Validar respuesta de API
    if "Global Quote" not in data:
        if "Note" in data:
            return {
                'error': 'rate_limit',
                'message': 'Alpha Vantage API rate limit reached (5 calls/min)',
                'http_code': 429
            }
        elif "Error Message" in data:
            return {
                'error': 'invalid_symbol',
                'message': f'Invalid or unknown symbol: {validated_symbol}',
                'http_code': 404
            }
        else:
            return {
                'error': 'no_data',
                'message': f'No data available for {validated_symbol}',
                'http_code': 404
            }
    
    quote = data["Global Quote"]
    
    # Construir stock data
    try:
        stock_data = {
            'symbol': quote.get("01. symbol", validated_symbol),
            'price': float(quote.get("05. price", 0)),
            'volume': int(quote.get("06. volume", 0)),
            'latest_trading_day': quote.get("07. latest trading day", ""),
            'previous_close': float(quote.get("08. previous close", 0)),
            'change': float(quote.get("09. change", 0)),
            'change_percent': quote.get("10. change percent", "0%").replace("%", "")
        }
    except (ValueError, TypeError) as e:
        return {
            'error': 'data_parse_error',
            'message': f'Failed to parse API response: {str(e)}',
            'http_code': 502
        }
    
    # Validar datos extraídos
    is_valid, result = validate_price_data(stock_data)
    if not is_valid:
        return {
            'error': 'invalid_data',
            'message': result,
            'http_code': 502
        }
    
    print(f"✅ {validated_symbol}: ${stock_data['price']}")
    return stock_data

# ==================== DATABASE FUNCTIONS ====================

def save_to_dynamodb(stock_data):
    """
    Guardar datos en DynamoDB con error handling
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    
    if table is None:
        return False, "DynamoDB table not initialized"
    
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
        print(f"💾 Saved {stock_data['symbol']} to DynamoDB")
        return True, None
        
    except InvalidOperation as e:
        return False, f"Invalid decimal conversion: {str(e)}"
    except Exception as e:
        return False, f"DynamoDB error: {str(e)}"

# ==================== LAMBDA HANDLER ====================

def create_response(status_code, body, headers=None):
    """Helper para crear respuestas HTTP consistentes"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body) if isinstance(body, dict) else body
    }

def lambda_handler(event, context):
    """
    Handler principal con error handling robusto
    Soporta: API Gateway, EventBridge, invocación directa
    """
    
    print(f"📥 Event received: {json.dumps(event, default=str)}")
    
    try:
        # Detectar origen del evento
        is_from_eventbridge = 'source' in event and event['source'] == 'aws.events'
        is_from_api_gateway = 'pathParameters' in event
        
        symbols_to_process = []
        
        # Determinar símbolos a procesar
        if is_from_eventbridge:
            print("🤖 EventBridge invocation - Processing watchlist")
            symbols_to_process = DEFAULT_WATCHLIST
            
        elif is_from_api_gateway:
            # Validar pathParameters
            if not event.get('pathParameters'):
                return create_response(400, {
                    'error': 'missing_parameter',
                    'message': 'Path parameter {symbol} is required'
                })
            
            symbol = event['pathParameters'].get('symbol', '').strip().upper()
            
            # Validar símbolo
            is_valid, result = validate_symbol(symbol)
            if not is_valid:
                return create_response(400, {
                    'error': 'invalid_symbol',
                    'message': result
                })
            
            symbols_to_process = [result]
            
        else:
            # Invocación directa
            symbols_to_process = event.get('symbols', DEFAULT_WATCHLIST)
        
        print(f"📊 Processing {len(symbols_to_process)} symbols: {symbols_to_process}")
        
        # Procesar símbolos
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'rate_limited': 0,
            'details': []
        }
        
        for symbol in symbols_to_process:
            stock_data = fetch_stock_data(symbol)
            results['processed'] += 1
            
            # Verificar si hay error
            if isinstance(stock_data, dict) and 'error' in stock_data:
                results['failed'] += 1
                
                if stock_data['error'] == 'rate_limit':
                    results['rate_limited'] += 1
                
                results['details'].append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': stock_data['error'],
                    'message': stock_data['message']
                })
                
                # Si es API Gateway y solo 1 símbolo, retornar error inmediatamente
                if is_from_api_gateway:
                    return create_response(
                        stock_data.get('http_code', 500),
                        {
                            'error': stock_data['error'],
                            'message': stock_data['message'],
                            'symbol': symbol
                        }
                    )
                
                continue
            
            # Guardar en DynamoDB
            success, error_msg = save_to_dynamodb(stock_data)
            
            if success:
                results['successful'] += 1
                results['details'].append({
                    'symbol': symbol,
                    'status': 'success',
                    'price': float(stock_data['price']),
                    'change': float(stock_data['change']),
                    'change_percent': stock_data['change_percent']
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'symbol': symbol,
                    'status': 'error',
                    'error': 'database_error',
                    'message': error_msg
                })
        
        print(f"✅ Processing complete: {results['successful']}/{results['processed']} successful")
        
        # Respuesta según origen
        if is_from_api_gateway:
            # API Gateway - retornar datos del símbolo
            if results['successful'] > 0:
                detail = results['details'][0]
                return create_response(200, {
                    'message': f"Price for {detail['symbol']} updated successfully",
                    'data': detail
                })
            else:
                # Ya se manejó arriba, pero por si acaso
                return create_response(500, {
                    'error': 'processing_failed',
                    'message': 'Failed to process symbol'
                })
        else:
            # EventBridge o invocación directa - retornar resumen
            return {
                'statusCode': 200,
                'body': json.dumps(results)
            }
    
    except Exception as e:
        # Catch-all para errores inesperados
        error_trace = traceback.format_exc()
        print(f"❌ Unexpected error: {error_trace}")
        
        if is_from_api_gateway:
            return create_response(500, {
                'error': 'internal_server_error',
                'message': 'An unexpected error occurred',
                'details': str(e) if context else None
            })
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'internal_server_error',
                    'message': str(e),
                    'trace': error_trace
                })
            }
