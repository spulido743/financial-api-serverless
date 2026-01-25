#!/usr/bin/env python3
"""
Script para leer datos de DynamoDB - FinancialData
Uso: python3 scripts/read_dynamodb.py
"""

import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import json

# Configuración
TABLE_NAME = "FinancialData"
REGION = "us-east-1"

# Cliente DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

def decimal_to_float(obj):
    """Convertir Decimal a float para JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def scan_all_items():
    """Obtener todos los items de la tabla"""
    print("🔍 Escaneando toda la tabla...\n")
    
    response = table.scan()
    items = response['Items']
    
    print(f"📊 Total de items encontrados: {len(items)}\n")
    print("=" * 80)
    
    for item in items:
        print(f"\n🏢 Símbolo: {item['symbol']}")
        print(f"   💰 Precio: ${item.get('price', 'N/A')}")
        print(f"   📅 Fecha: {item.get('date', 'N/A')}")
        print(f"   ⏰ Timestamp: {item['timestamp']}")
        if 'volume' in item:
            print(f"   📈 Volumen: {item['volume']:,}")
        if 'change' in item:
            print(f"   📊 Cambio: {item['change']}")
        print("-" * 80)
    
    return items

def query_by_symbol(symbol):
    """Consultar datos de un símbolo específico"""
    print(f"\n🔎 Consultando datos de {symbol}...\n")
    
    response = table.query(
        KeyConditionExpression=Key('symbol').eq(symbol)
    )
    
    items = response['Items']
    
    if not items:
        print(f"❌ No se encontraron datos para {symbol}")
        return []
    
    print(f"✅ {len(items)} registro(s) encontrado(s) para {symbol}\n")
    print("=" * 80)
    
    # Ordenar por timestamp (más reciente primero)
    items_sorted = sorted(items, key=lambda x: x['timestamp'], reverse=True)
    
    for item in items_sorted:
        print(f"💰 Precio: ${item.get('price', 'N/A')}")
        print(f"📅 Fecha: {item.get('date', 'N/A')}")
        print(f"⏰ Timestamp: {item['timestamp']}")
        print("-" * 80)
    
    return items_sorted

def get_latest_price(symbol):
    """Obtener el precio más reciente de un símbolo"""
    print(f"\n💵 Obteniendo último precio de {symbol}...\n")
    
    response = table.query(
        KeyConditionExpression=Key('symbol').eq(symbol),
        ScanIndexForward=False,  # Orden descendente
        Limit=1  # Solo el más reciente
    )
    
    items = response['Items']
    
    if not items:
        print(f"❌ No hay datos para {symbol}")
        return None
    
    latest = items[0]
    price = latest.get('price', 'N/A')
    date = latest.get('date', 'N/A')
    
    print(f"✅ Último precio de {symbol}: ${price}")
    print(f"   📅 Fecha: {date}")
    
    return latest

def get_all_symbols():
    """Obtener lista de símbolos únicos"""
    print("\n📋 Obteniendo lista de símbolos...\n")
    
    response = table.scan(
        ProjectionExpression='symbol'
    )
    
    symbols = set(item['symbol'] for item in response['Items'])
    
    print(f"✅ Símbolos encontrados: {', '.join(sorted(symbols))}")
    print(f"   Total: {len(symbols)} símbolos\n")
    
    return list(symbols)

def export_to_json(filename='evidencias/dynamodb_data.json'):
    """Exportar todos los datos a JSON"""
    print(f"\n💾 Exportando datos a {filename}...\n")
    
    response = table.scan()
    items = response['Items']
    
    # Crear directorio si no existe
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Guardar a JSON
    with open(filename, 'w') as f:
        json.dump(items, f, indent=2, default=decimal_to_float)
    
    print(f"✅ {len(items)} items exportados a {filename}")

def main():
    """Función principal"""
    print("=" * 80)
    print(" 🚀 DynamoDB Reader - FinancialData")
    print("=" * 80)
    
    try:
        # 1. Escanear todos los items
        all_items = scan_all_items()
        
        # 2. Obtener símbolos únicos
        symbols = get_all_symbols()
        
        # 3. Consultar datos de cada símbolo
        for symbol in sorted(symbols):
            get_latest_price(symbol)
        
        # 4. Exportar a JSON
        export_to_json()
        
        print("\n" + "=" * 80)
        print("✅ Script completado exitosamente")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()