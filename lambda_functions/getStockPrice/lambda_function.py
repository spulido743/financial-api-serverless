"""
Lambda Function: getStockPrice
Descripción: Obtiene el último precio registrado de una acción
Trigger: API Gateway GET /stock/{symbol}
"""

import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import os

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'FinancialData')
table = dynamodb.Table(table_name)

def decimal_to_float(obj):
    """Convertir Decimal a float para JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Handler principal de la función Lambda
    
    Args:
        event: Evento de entrada con pathParameters
        context: Contexto de ejecución de Lambda
    
    Returns:
        Response con statusCode y body
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
                    'message': 'Debe proporcionar el símbolo en la URL: /stock/{symbol}'
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
        
        print(f"🔍 Consultando último precio de: {symbol}")
        
        # Query DynamoDB para obtener el último registro del símbolo
        response = table.query(
            KeyConditionExpression=Key('symbol').eq(symbol),
            ScanIndexForward=False,  # Ordenar descendente (más reciente primero)
            Limit=1  # Solo el más reciente
        )
        
        print(f"📊 DynamoDB Response: {response['ResponseMetadata']['HTTPStatusCode']}")
        print(f"📊 Items encontrados: {response['Count']}")
        
        # Verificar si se encontró el símbolo
        if response['Count'] == 0:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Symbol not found',
                    'message': f'No se encontraron datos para el símbolo {symbol}'
                })
            }
        
        # Obtener el item más reciente
        item = response['Items'][0]
        
        # Preparar respuesta
        stock_data = {
            'symbol': item['symbol'],
            'price': float(item['price']),
            'timestamp': int(item['timestamp']),
            'date': item['date']
        }
        
        # Agregar campos opcionales si existen
        if 'volume' in item:
            stock_data['volume'] = int(item['volume'])
        if 'change' in item:
            stock_data['change'] = float(item['change'])
        if 'change_percent' in item:
            stock_data['change_percent'] = float(item['change_percent'])
        
        print(f"✅ Precio encontrado: ${stock_data['price']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'symbol': symbol,
                'data': stock_data,
                'message': f'Último precio de {symbol} obtenido exitosamente'
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