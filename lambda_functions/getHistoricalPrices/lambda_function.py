"""
Lambda Function: getHistoricalPrices (PRODUCTION v2.0)
Descripción: Consulta histórico de precios desde DynamoDB
Features: Error handling robusto, validaciones, paginación
"""

import json
import boto3
from decimal import Decimal
from datetime import datetime, timedelta
import os
import traceback

# ==================== CONFIGURACIÓN ====================
TABLE_NAME = os.environ.get('TABLE_NAME', 'FinancialData')

# Cliente DynamoDB
try:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
except Exception as e:
    print(f"❌ Error initializing DynamoDB: {str(e)}")
    table = None

# ==================== VALIDACIONES ====================

def validate_symbol(symbol):
    """Validar formato de símbolo"""
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

def validate_days(days_str):
    """Validar parámetro days"""
    try:
        days = int(days_str)
        
        if days < 1:
            return False, "Days must be at least 1"
        
        if days > 365:
            return False, "Days cannot exceed 365"
        
        return True, days
        
    except ValueError:
        return False, f"Invalid days parameter: must be an integer"

def validate_limit(limit_str):
    """Validar parámetro limit para paginación"""
    try:
        limit = int(limit_str)
        
        if limit < 1:
            return False, "Limit must be at least 1"
        
        if limit > 1000:
            return False, "Limit cannot exceed 1000"
        
        return True, limit
        
    except ValueError:
        return False, f"Invalid limit parameter: must be an integer"

# ==================== HELPER FUNCTIONS ====================

class DecimalEncoder(json.JSONEncoder):
    """Encoder para convertir Decimal a float en JSON"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def create_response(status_code, body, headers=None):
    """Helper para crear respuestas HTTP consistentes"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, cls=DecimalEncoder)
    }

# ==================== DATABASE FUNCTIONS ====================

def query_historical_data(symbol, days, limit=None):
    """
    Query DynamoDB para datos históricos
    
    Returns:
        tuple: (success: bool, data: list or error_message: str)
    """
    
    if table is None:
        return False, "DynamoDB table not initialized"
    
    try:
        # Calcular timestamps
        end_time = int(datetime.now().timestamp())
        start_time = end_time - (days * 86400)
        
        print(f"🔍 Querying {symbol} from {datetime.fromtimestamp(start_time)} to {datetime.fromtimestamp(end_time)}")
        
        # Query DynamoDB
        query_params = {
            'KeyConditionExpression': 'symbol = :symbol AND #ts BETWEEN :start AND :end',
            'ExpressionAttributeNames': {
                '#ts': 'timestamp'
            },
            'ExpressionAttributeValues': {
                ':symbol': symbol,
                ':start': start_time,
                ':end': end_time
            },
            'ScanIndexForward': False
        }
        
        if limit:
            query_params['Limit'] = limit
        
        response = table.query(**query_params)
        
        items = response.get('Items', [])
        
        print(f"✅ Found {len(items)} records for {symbol}")
        
        return True, items
        
    except Exception as e:
        error_msg = f"DynamoDB query error: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

# ==================== LAMBDA HANDLER ====================

def lambda_handler(event, context):
    """Handler principal con error handling robusto"""
    
    print(f"📥 Event received: {json.dumps(event, default=str)}")
    
    try:
        if 'pathParameters' not in event:
            return create_response(400, {
                'error': 'missing_parameters',
                'message': 'Path parameter {symbol} is required'
            })
        
        symbol = event['pathParameters'].get('symbol', '').strip().upper()
        
        is_valid, result = validate_symbol(symbol)
        if not is_valid:
            return create_response(400, {
                'error': 'invalid_symbol',
                'message': result
            })
        
        symbol = result
        
        query_params = event.get('queryStringParameters') or {}
        
        days_str = query_params.get('days', '7')
        is_valid, days_result = validate_days(days_str)
        if not is_valid:
            return create_response(400, {
                'error': 'invalid_days',
                'message': days_result
            })
        
        days = days_result
        
        limit = None
        if 'limit' in query_params:
            is_valid, limit_result = validate_limit(query_params['limit'])
            if not is_valid:
                return create_response(400, {
                    'error': 'invalid_limit',
                    'message': limit_result
                })
            limit = limit_result
        
        print(f"📊 Fetching {days} days of history for {symbol}" + 
              (f" (limit: {limit})" if limit else ""))
        
        success, result = query_historical_data(symbol, days, limit)
        
        if not success:
            return create_response(500, {
                'error': 'database_error',
                'message': result
            })
        
        if not result:
            return create_response(404, {
                'error': 'no_data',
                'message': f'No historical data found for {symbol} in the last {days} days',
                'symbol': symbol,
                'days': days
            })
        
        response_data = {
            'symbol': symbol,
            'days': days,
            'count': len(result),
            'data': result
        }
        
        if limit:
            response_data['limit'] = limit
        
        return create_response(200, response_data)
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Unexpected error: {error_trace}")
        
        return create_response(500, {
            'error': 'internal_server_error',
            'message': 'An unexpected error occurred',
            'details': str(e)
        })
