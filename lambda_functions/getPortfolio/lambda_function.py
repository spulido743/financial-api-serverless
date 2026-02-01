"""
Lambda Function: getPortfolio
Descripción: Obtiene lista de todos los símbolos únicos guardados con sus últimos precios
Trigger: API Gateway GET /portfolio
"""

import json
import boto3
from decimal import Decimal
from datetime import datetime
import os

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'FinancialData')
table = dynamodb.Table(table_name)

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Handler principal - Obtiene portfolio completo
    """
    
    print(f"📥 Event recibido: {json.dumps(event, default=str)}")
    
    try:
        print("📊 Obteniendo portfolio completo...")
        
        # Scan de la tabla para obtener todos los registros
        response = table.scan(
            ProjectionExpression='symbol, #ts, price, #dt, volume, change_percent',
            ExpressionAttributeNames={
                '#ts': 'timestamp',
                '#dt': 'date'
            }
        )
        
        items = response['Items']
        
        print(f"📊 {len(items)} registros encontrados en total")
        
        if len(items) == 0:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'No data found',
                    'message': 'No hay símbolos guardados en el portfolio'
                })
            }
        
        # Agrupar por símbolo y obtener el más reciente de cada uno
        symbols_dict = {}
        
        for item in items:
            symbol = item['symbol']
            timestamp = int(item['timestamp'])
            
            # Guardar solo el más reciente de cada símbolo
            if symbol not in symbols_dict or timestamp > symbols_dict[symbol]['timestamp']:
                symbols_dict[symbol] = {
                    'symbol': symbol,
                    'price': float(item['price']),
                    'timestamp': timestamp,
                    'date': item['date'],
                    'last_updated': item['date']
                }
                
                # Agregar campos opcionales si existen
                if 'volume' in item:
                    symbols_dict[symbol]['volume'] = int(item['volume'])
                if 'change_percent' in item:
                    symbols_dict[symbol]['change_percent'] = float(item['change_percent'])
        
        # Convertir a lista ordenada alfabéticamente
        portfolio = sorted(symbols_dict.values(), key=lambda x: x['symbol'])
        
        # Calcular estadísticas del portfolio
        if portfolio:
            prices = [item['price'] for item in portfolio]
            
            stats = {
                'total_symbols': len(portfolio),
                'total_records': len(items),
                'price_stats': {
                    'highest': round(max(prices), 2),
                    'lowest': round(min(prices), 2),
                    'average': round(sum(prices) / len(prices), 2)
                },
                'symbols_list': [item['symbol'] for item in portfolio]
            }
        else:
            stats = {
                'total_symbols': 0,
                'message': 'No hay símbolos en el portfolio'
            }
        
        print(f"✅ Portfolio con {len(portfolio)} símbolos únicos")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'portfolio': portfolio,
                'statistics': stats,
                'generated_at': datetime.now().isoformat(),
                'message': 'Portfolio obtenido exitosamente'
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
