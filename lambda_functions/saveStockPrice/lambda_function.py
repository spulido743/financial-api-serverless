"""
Lambda Function: saveStockPrice
Descripción: Guarda el precio de una acción en DynamoDB
Trigger: API Gateway (futuro) o invocación manual
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

def lambda_handler(event, context):
    """
    Handler principal de la función Lambda
    
    Args:
        event: Evento de entrada (JSON con symbol y price)
        context: Contexto de ejecución de Lambda
    
    Returns:
        Response con statusCode y body
    """
    
    print(f"📥 Event recibido: {json.dumps(event)}")
    
    try:
        # Parsear el body si viene de API Gateway
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Si es invocación directa, usar event directamente
            body = event
        
        # Validar campos requeridos
        if 'symbol' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required field: symbol',
                    'message': 'Debe proporcionar el símbolo de la acción'
                })
            }
        
        if 'price' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required field: price',
                    'message': 'Debe proporcionar el precio de la acción'
                })
            }
        
        # Extraer datos
        symbol = body['symbol'].upper()
        price = Decimal(str(body['price']))
        
        # Timestamp actual
        timestamp = int(datetime.now().timestamp())
        current_date = datetime.now().isoformat()
        
        # Datos opcionales
        volume = body.get('volume', None)
        change = body.get('change', None)
        change_percent = body.get('change_percent', None)
        
        # Construir item para DynamoDB
        item = {
            'symbol': symbol,
            'timestamp': timestamp,
            'price': price,
            'date': current_date
        }
        
        # Agregar campos opcionales si existen
        if volume is not None:
            item['volume'] = int(volume)
        if change is not None:
            item['change'] = Decimal(str(change))
        if change_percent is not None:
            item['change_percent'] = Decimal(str(change_percent))
        
        print(f"💾 Guardando en DynamoDB: {symbol} = ${price}")
        
        # Guardar en DynamoDB
        response = table.put_item(Item=item)
        
        print(f"✅ Item guardado exitosamente")
        print(f"📊 DynamoDB Response: {response['ResponseMetadata']['HTTPStatusCode']}")
        
        # Respuesta exitosa
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Precio de {symbol} guardado exitosamente',
                'data': {
                    'symbol': symbol,
                    'price': float(price),
                    'timestamp': timestamp,
                    'date': current_date
                }
            })
        }
        
    except ValueError as e:
        print(f"❌ Error de validación: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid data type',
                'message': f'El precio debe ser un número válido: {str(e)}'
            })
        }
        
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
