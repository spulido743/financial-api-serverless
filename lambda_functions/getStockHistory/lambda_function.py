"""
Lambda Function: getStockHistory
Descripción: Obtiene el histórico de precios de una acción
Trigger: API Gateway GET /stock/{symbol}/history
"""

import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from datetime import datetime, timedelta
import os

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'FinancialData')
table = dynamodb.Table(table_name)

def decimal_to_float(obj):
    """Convertir Decimal a float"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Handler principal
    
    Query Parameters:
        - days: número de días de histórico (default: 30)
        - limit: máximo número de registros (default: 100)
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
                    'message': 'Debe proporcionar el símbolo en la URL'
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
        
        # Obtener query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        days = int(query_params.get('days', 30))
        limit = int(query_params.get('limit', 100))
        
        # Validar límites
        if days > 365:
            days = 365
        if limit > 500:
            limit = 500
        
        print(f"🔍 Consultando histórico de {symbol}: {days} días, límite {limit}")
        
        # Calcular timestamp de inicio (hace N días)
        start_date = datetime.now() - timedelta(days=days)
        start_timestamp = int(start_date.timestamp())
        
        # Query DynamoDB
        response = table.query(
            KeyConditionExpression=Key('symbol').eq(symbol) & Key('timestamp').gte(start_timestamp),
            ScanIndexForward=False,  # Más reciente primero
            Limit=limit
        )
        
        print(f"📊 DynamoDB Response: {response['ResponseMetadata']['HTTPStatusCode']}")
        print(f"📊 Items encontrados: {response['Count']}")
        
        if response['Count'] == 0:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'No data found',
                    'message': f'No se encontraron datos para {symbol} en los últimos {days} días'
                })
            }
        
        # Procesar items
        history = []
        for item in response['Items']:
            record = {
                'timestamp': int(item['timestamp']),
                'date': item['date'],
                'price': float(item['price'])
            }
            
            # Campos opcionales
            if 'volume' in item:
                record['volume'] = int(item['volume'])
            if 'change' in item:
                record['change'] = float(item['change'])
            if 'change_percent' in item:
                record['change_percent'] = float(item['change_percent'])
            
            history.append(record)
        
        # Calcular estadísticas
        prices = [float(item['price']) for item in response['Items']]
        stats = {
            'count': len(prices),
            'max': max(prices),
            'min': min(prices),
            'avg': sum(prices) / len(prices),
            'latest': prices[0],
            'oldest': prices[-1]
        }
        
        print(f"✅ Histórico obtenido: {stats['count']} registros")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'symbol': symbol,
                'period': {
                    'days': days,
                    'from': start_date.isoformat(),
                    'to': datetime.now().isoformat()
                },
                'statistics': stats,
                'data': history,
                'message': f'Histórico de {symbol} obtenido exitosamente'
            }, default=decimal_to_float)
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
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
