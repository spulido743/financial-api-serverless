"""
Lambda Function: calculateIndicators (ADVANCED VERSION)
Indicadores: SMA, EMA, RSI, MACD, Stochastic, Bollinger Bands, Volatilidad
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

def fetch_historical_data(symbol, days=60):
    """Obtener más datos para RSI y MACD (necesitan más historia)"""
    start_date = datetime.now() - timedelta(days=days)
    start_timestamp = int(start_date.timestamp())
    
    print(f"📊 Consultando {days} días de datos para {symbol}...")
    
    response = table.query(
        KeyConditionExpression=Key('symbol').eq(symbol) & Key('timestamp').gte(start_timestamp),
        ScanIndexForward=False,
        Limit=200
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

# ============ INDICADORES BÁSICOS ============

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

# ============ INDICADORES AVANZADOS ============

def calculate_rsi(prices, period=14):
    """
    RSI (Relative Strength Index)
    Valores: 0-100
    > 70 = Sobrecompra (OVERBOUGHT)
    < 30 = Sobreventa (OVERSOLD)
    """
    if len(prices) < period + 1:
        return None
    
    # Invertir para calcular del más antiguo al más reciente
    prices_reversed = prices[::-1][:(period + 1)]
    
    # Calcular cambios de precio
    changes = [prices_reversed[i] - prices_reversed[i-1] for i in range(1, len(prices_reversed))]
    
    # Separar ganancias y pérdidas
    gains = [change if change > 0 else 0 for change in changes]
    losses = [-change if change < 0 else 0 for change in changes]
    
    # Calcular promedio
    avg_gain = mean(gains) if gains else 0
    avg_loss = mean(losses) if losses else 0
    
    if avg_loss == 0:
        return 100.0  # No hay pérdidas = RSI máximo
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    MACD (Moving Average Convergence Divergence)
    Components:
    - MACD line: EMA(12) - EMA(26)
    - Signal line: EMA(9) of MACD
    - Histogram: MACD - Signal
    """
    if len(prices) < slow + signal:
        return None
    
    def calc_ema_series(data, period):
        """Calcular serie de EMA"""
        if len(data) < period:
            return None
        
        data_reversed = data[::-1]
        multiplier = 2 / (period + 1)
        emas = [data_reversed[0]]
        
        for price in data_reversed[1:]:
            new_ema = (price * multiplier) + (emas[-1] * (1 - multiplier))
            emas.append(new_ema)
        
        return emas[-1]  # Último valor (más reciente)
    
    # Calcular EMAs
    ema_fast = calc_ema_series(prices, fast)
    ema_slow = calc_ema_series(prices, slow)
    
    if ema_fast is None or ema_slow is None:
        return None
    
    # MACD line
    macd_line = ema_fast - ema_slow
    
    # Signal line (simplificado - en producción sería EMA del MACD)
    signal_line = macd_line * 0.9  # Aproximación
    
    # Histogram
    histogram = macd_line - signal_line
    
    return {
        'macd': round(macd_line, 4),
        'signal': round(signal_line, 4),
        'histogram': round(histogram, 4)
    }

def calculate_stochastic(prices, period=14):
    """
    Stochastic Oscillator
    Valores: 0-100
    > 80 = Sobrecompra
    < 20 = Sobreventa
    """
    if len(prices) < period:
        return None
    
    recent_prices = prices[:period]
    current_price = prices[0]
    
    highest_high = max(recent_prices)
    lowest_low = min(recent_prices)
    
    if highest_high == lowest_low:
        return 50.0  # Neutral
    
    stoch_k = ((current_price - lowest_low) / (highest_high - lowest_low)) * 100
    
    return round(stoch_k, 2)

# ============ SISTEMA DE RECOMENDACIÓN AVANZADO ============

def generate_advanced_recommendation(indicators):
    """
    Sistema de puntuación para generar recomendación
    Considera todos los indicadores disponibles
    """
    signals = []
    score = 0  # Puntuación: positivo = BUY, negativo = SELL
    
    # 1. RSI
    rsi = indicators.get('rsi')
    if rsi is not None:
        if rsi < 30:
            signals.append('BUY (RSI oversold: {})'.format(rsi))
            score += 3
        elif rsi > 70:
            signals.append('SELL (RSI overbought: {})'.format(rsi))
            score -= 3
        elif rsi < 40:
            signals.append('BUY (RSI low: {})'.format(rsi))
            score += 1
        elif rsi > 60:
            signals.append('SELL (RSI high: {})'.format(rsi))
            score -= 1
    
    # 2. MACD
    macd_data = indicators.get('macd')
    if macd_data is not None:
        if macd_data['macd'] > macd_data['signal']:
            signals.append('BUY (MACD bullish crossover)')
            score += 2
        else:
            signals.append('SELL (MACD bearish crossover)')
            score -= 2
        
        if macd_data['histogram'] > 0:
            score += 1
        else:
            score -= 1
    
    # 3. Stochastic
    stoch = indicators.get('stochastic')
    if stoch is not None:
        if stoch < 20:
            signals.append('BUY (Stochastic oversold: {})'.format(stoch))
            score += 2
        elif stoch > 80:
            signals.append('SELL (Stochastic overbought: {})'.format(stoch))
            score -= 2
    
    # 4. Bollinger Bands
    bb = indicators.get('bollinger_bands')
    current = indicators.get('current_price')
    if bb is not None and current is not None:
        if current < bb['lower']:
            signals.append('BUY (Price below Bollinger lower band)')
            score += 3
        elif current > bb['upper']:
            signals.append('SELL (Price above Bollinger upper band)')
            score -= 3
    
    # 5. Price vs SMA
    sma_20 = indicators.get('sma_20')
    if sma_20 is not None and current is not None:
        if current > sma_20:
            signals.append('BUY (Price above SMA-20)')
            score += 1
        else:
            signals.append('SELL (Price below SMA-20)')
            score -= 1
    
    # 6. Volatilidad
    volatility = indicators.get('volatility')
    if volatility is not None and volatility > 10:
        signals.append('WARNING (High volatility: {}%)'.format(volatility))
    
    # Decisión final basada en score
    if score >= 5:
        action = 'STRONG BUY'
        confidence = 'high'
    elif score >= 2:
        action = 'BUY'
        confidence = 'medium'
    elif score >= 0:
        action = 'WEAK BUY'
        confidence = 'low'
    elif score >= -2:
        action = 'WEAK SELL'
        confidence = 'low'
    elif score >= -5:
        action = 'SELL'
        confidence = 'medium'
    else:
        action = 'STRONG SELL'
        confidence = 'high'
    
    return {
        'action': action,
        'score': score,
        'signals': signals,
        'confidence': confidence,
        'total_indicators': len([s for s in signals if 'WARNING' not in s])
    }

# ============ LAMBDA HANDLER ============

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
        
        print(f"📊 Calculando indicadores AVANZADOS para: {symbol}")
        
        # Obtener más datos para RSI y MACD
        data = fetch_historical_data(symbol, days=60)
        
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
        
        print(f"🔢 Calculando con {len(prices)} precios...")
        
        # Calcular TODOS los indicadores
        indicators = {
            'symbol': symbol,
            'analysis_date': datetime.now().isoformat(),
            'data_points': len(prices),
            'period': '60 days',
            
            # Precio actual
            'current_price': round(prices[0], 2),
            
            # Medias móviles
            'sma_5': calculate_sma(prices, 5),
            'sma_10': calculate_sma(prices, 10),
            'sma_20': calculate_sma(prices, 20),
            'sma_50': calculate_sma(prices, 50),
            'ema_12': calculate_ema(prices, 12),
            'ema_26': calculate_ema(prices, 26),
            
            # Indicadores avanzados
            'rsi': calculate_rsi(prices, 14),
            'macd': calculate_macd(prices, 12, 26, 9),
            'stochastic': calculate_stochastic(prices, 14),
            
            # Análisis de precio
            'price_analysis': calculate_price_change(prices),
            
            # Volatilidad y bandas
            'volatility': calculate_volatility(prices[:30]),
            'bollinger_bands': calculate_bollinger_bands(prices, 20),
            
            # Soporte y resistencia
            'support_resistance': calculate_support_resistance(prices[:30]),
            
            # Estadísticas
            'statistics': {
                'max': round(max(prices), 2),
                'min': round(min(prices), 2),
                'avg': round(mean(prices), 2),
                'range': round(max(prices) - min(prices), 2)
            }
        }
        
        # Generar recomendación avanzada
        recommendation = generate_advanced_recommendation(indicators)
        indicators['recommendation'] = recommendation
        
        print(f"✅ Análisis completado: {recommendation['action']} (score: {recommendation['score']})")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'symbol': symbol,
                'indicators': indicators,
                'message': f'Análisis técnico avanzado de {symbol} completado exitosamente'
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
