"""
Lambda Function: calculateIndicators (FIXED)
Descripción: Calcula indicadores técnicos financieros
"""

import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from datetime import datetime, timedelta
import os
from statistics import mean, stdev

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'FinancialData')
table = dynamodb.Table(table_name)

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def fetch_historical_data(symbol, days=30):
    start_date = datetime.now() - timedelta(days=days)
    start_timestamp = int(start_date.timestamp())
    
    print(f"📊 Consultando {days} días de datos para {symbol}...")
    
    response = table.query(
        KeyConditionExpression=Key('symbol').eq(symbol) & Key('timestamp').gte(start_timestamp),
        ScanIndexForward=False,
        Limit=100
    )
    
    if response['Count'] == 0:
        return None
    
    prices = [float(item['price']) for item in response['Items']]
    timestamps = [int(item['timestamp']) for item in response['Items']]
    
    print(f"✅ {len(prices)} registros encontrados")
    
    return {
        'prices': prices,
        'timestamps': timestamps,
        'items': response['Items']
    }

def calculate_sma(prices, period):
    if len(prices) < period:
        return None
    sma = mean(prices[:period])
    return round(sma, 2)

def calculate_ema(prices, period):
    if len(prices) < period:
        return None
    prices_reversed = prices[::-1][:period]
    multiplier = 2 / (period + 1)
    ema = prices_reversed[0]
    for price in prices_reversed[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    return round(ema, 2)

def calculate_volatility(prices):
    if len(prices) < 2:
        return None
    std = stdev(prices)
    avg = mean(prices)
    volatility_pct = (std / avg) * 100
    return round(volatility_pct, 2)

def calculate_price_change(prices):
    current = prices[0]
    avg = mean(prices)
    change = current - avg
    change_pct = (change / avg) * 100
    return {
        'current': round(current, 2),
        'average': round(avg, 2),
        'change': round(change, 2),
        'change_percent': round(change_pct, 2)
    }

def calculate_bollinger_bands(prices, period=20, num_std=2):
    if len(prices) < period:
        return None
    recent_prices = prices[:period]
    sma = mean(recent_prices)
    std = stdev(recent_prices)
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return {
        'upper': round(upper, 2),
        'middle': round(sma, 2),
        'lower': round(lower, 2)
    }

def calculate_support_resistance(prices):
    resistance = max(prices)
    support = min(prices)
    return {
        'resistance': round(resistance, 2),
        'support': round(support, 2),
        'range': round(resistance - support, 2)
    }

def generate_recommendation(indicators):
    """Generar recomendación con manejo seguro de None"""
    signals = []
    
    # Señal 1: Precio vs SMA (verificar que SMA no sea None)
    if indicators.get('sma_20') is not None and indicators.get('price_analysis'):
        if indicators['price_analysis']['current'] > indicators['sma_20']:
            signals.append('bullish')
        else:
            signals.append('bearish')
    
    # Señal 2: Bollinger Bands (verificar que existan)
    if indicators.get('bollinger_bands') is not None and indicators.get('price_analysis'):
        current = indicators['price_analysis']['current']
        bb = indicators['bollinger_bands']
        if current > bb['upper']:
            signals.append('overbought')
        elif current < bb['lower']:
            signals.append('oversold')
    
    # Señal 3: Volatilidad (verificar que no sea None)
    if indicators.get('volatility') is not None:
        if indicators['volatility'] > 5:
            signals.append('high_volatility')
    
    # Generar recomendación
    bullish_count = signals.count('bullish')
    bearish_count = signals.count('bearish')
    
    if 'oversold' in signals:
        return 'BUY', 'Precio está por debajo de la banda inferior (sobreventa)'
    elif 'overbought' in signals:
        return 'SELL', 'Precio está por encima de la banda superior (sobrecompra)'
    elif bullish_count > bearish_count:
        return 'BUY', 'Indicadores mayormente alcistas'
    elif bearish_count > bullish_count:
        return 'SELL', 'Indicadores mayormente bajistas'
    else:
        return 'HOLD', 'Señales mixtas, mantener posición'

def lambda_handler(event, context):
    print(f"📥 Event recibido: {json.dumps(event, default=str)}")
    
    try:
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
        
        print(f"📊 Calculando indicadores para: {symbol}")
        
        data = fetch_historical_data(symbol, days=30)
        
        if not data or len(data['prices']) < 5:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Insufficient data',
                    'message': f'No hay suficientes datos para analizar {symbol}. Se necesitan al menos 5 registros.'
                })
            }
        
        prices = data['prices']
        
        print(f"🔢 Calculando indicadores con {len(prices)} precios...")
        
        indicators = {
            'symbol': symbol,
            'analysis_date': datetime.now().isoformat(),
            'data_points': len(prices),
            'period': '30 days',
            'current_price': round(prices[0], 2),
            'sma_5': calculate_sma(prices, 5),
            'sma_10': calculate_sma(prices, 10),
            'sma_20': calculate_sma(prices, 20),
            'ema_12': calculate_ema(prices, 12),
            'ema_26': calculate_ema(prices, 26),
            'price_analysis': calculate_price_change(prices),
            'volatility': calculate_volatility(prices),
            'support_resistance': calculate_support_resistance(prices),
            'bollinger_bands': calculate_bollinger_bands(prices, period=20),
            'statistics': {
                'max': round(max(prices), 2),
                'min': round(min(prices), 2),
                'avg': round(mean(prices), 2),
                'range': round(max(prices) - min(prices), 2)
            }
        }
        
        recommendation, reason = generate_recommendation(indicators)
        indicators['recommendation'] = {
            'action': recommendation,
            'reason': reason,
            'confidence': 'medium'
        }
        
        print(f"✅ Análisis completado: {recommendation}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'symbol': symbol,
                'indicators': indicators,
                'message': f'Análisis técnico de {symbol} completado exitosamente'
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
