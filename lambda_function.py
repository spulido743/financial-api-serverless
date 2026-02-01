"""
Lambda Function: calculateIndicators
Descripción: Calcula indicadores técnicos financieros
Indicadores: SMA, EMA, Volatilidad, Max/Min, Tendencia
Trigger: API Gateway GET /analyze/{symbol}
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
    """Convertir Decimal a float"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def fetch_historical_data(symbol, days=30):
    """
    Obtener datos históricos de DynamoDB
    
    Args:
        symbol: Símbolo de la acción
        days: Número de días hacia atrás
    
    Returns:
        Lista de precios ordenados (más reciente primero)
    """
    
    start_date = datetime.now() - timedelta(days=days)
    start_timestamp = int(start_date.timestamp())
    
    print(f"📊 Consultando {days} días de datos para {symbol}...")
    
    response = table.query(
        KeyConditionExpression=Key('symbol').eq(symbol) & Key('timestamp').gte(start_timestamp),
        ScanIndexForward=False,  # Más reciente primero
        Limit=100
    )
    
    if response['Count'] == 0:
        return None
    
    # Extraer solo los precios
    prices = [float(item['price']) for item in response['Items']]
    timestamps = [int(item['timestamp']) for item in response['Items']]
    
    print(f"✅ {len(prices)} registros encontrados")
    
    return {
        'prices': prices,
        'timestamps': timestamps,
        'items': response['Items']
    }

def calculate_sma(prices, period):
    """
    Simple Moving Average (Media Móvil Simple)
    
    Args:
        prices: Lista de precios
        period: Período (ej: 20 días)
    
    Returns:
        SMA o None si no hay suficientes datos
    """
    if len(prices) < period:
        return None
    
    sma = mean(prices[:period])
    return round(sma, 2)

def calculate_ema(prices, period):
    """
    Exponential Moving Average (Media Móvil Exponencial)
    
    Args:
        prices: Lista de precios (más reciente primero)
        period: Período
    
    Returns:
        EMA o None
    """
    if len(prices) < period:
        return None
    
    # Invertir para calcular del más antiguo al más reciente
    prices_reversed = prices[::-1][:period]
    
    multiplier = 2 / (period + 1)
    ema = prices_reversed[0]  # Comenzar con el primer precio
    
    for price in prices_reversed[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return round(ema, 2)

def calculate_volatility(prices):
    """
    Volatilidad (desviación estándar)
    
    Args:
        prices: Lista de precios
    
    Returns:
        Volatilidad en porcentaje
    """
    if len(prices) < 2:
        return None
    
    std = stdev(prices)
    avg = mean(prices)
    volatility_pct = (std / avg) * 100
    
    return round(volatility_pct, 2)

def calculate_price_change(prices):
    """
    Cambio de precio (último vs promedio)
    
    Args:
        prices: Lista de precios
    
    Returns:
        Dict con cambios
    """
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
    """
    Bollinger Bands (Bandas de Bollinger)
    
    Args:
        prices: Lista de precios
        period: Período para SMA
        num_std: Número de desviaciones estándar
    
    Returns:
        Dict con upper, middle, lower bands
    """
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
    """
    Niveles de soporte y resistencia básicos
    
    Args:
        prices: Lista de precios
    
    Returns:
        Dict con niveles
    """
    resistance = max(prices)
    support = min(prices)
    
    return {
        'resistance': round(resistance, 2),
        'support': round(support, 2),
        'range': round(resistance - support, 2)
    }

def generate_recommendation(indicators):
    """
    Generar recomendación basada en indicadores
    
    Args:
        indicators: Dict con todos los indicadores
    
    Returns:
        String con recomendación
    """
    signals = []
    
    # Señal 1: Precio vs SMA
    if indicators['price_analysis']['current'] > indicators['sma_20']:
        signals.append('bullish')
    else:
        signals.append('bearish')
    
    # Señal 2: Precio vs Bandas de Bollinger
    if indicators['bollinger_bands']:
        current = indicators['price_analysis']['current']
        if current > indicators['bollinger_bands']['upper']:
            signals.append('overbought')
        elif current < indicators['bollinger_bands']['lower']:
            signals.append('oversold')
    
    # Señal 3: Volatilidad
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
        
        # Obtener datos históricos
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
        
        # Calcular todos los indicadores
        indicators = {
            'symbol': symbol,
            'analysis_date': datetime.now().isoformat(),
            'data_points': len(prices),
            'period': '30 days',
            
            # Indicadores básicos
            'current_price': round(prices[0], 2),
            'sma_5': calculate_sma(prices, 5),
            'sma_10': calculate_sma(prices, 10),
            'sma_20': calculate_sma(prices, 20),
            'ema_12': calculate_ema(prices, 12),
            'ema_26': calculate_ema(prices, 26),
            
            # Análisis de precio
            'price_analysis': calculate_price_change(prices),
            
            # Volatilidad
            'volatility': calculate_volatility(prices),
            
            # Soporte y resistencia
            'support_resistance': calculate_support_resistance(prices),
            
            # Bollinger Bands
            'bollinger_bands': calculate_bollinger_bands(prices, period=20),
            
            # Estadísticas
            'statistics': {
                'max': round(max(prices), 2),
                'min': round(min(prices), 2),
                'avg': round(mean(prices), 2),
                'range': round(max(prices) - min(prices), 2)
            }
        }
        
        # Generar recomendación
        recommendation, reason = generate_recommendation(indicators)
        indicators['recommendation'] = {
            'action': recommendation,
            'reason': reason,
            'confidence': 'medium'  # Podría ser calculado con más lógica
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
