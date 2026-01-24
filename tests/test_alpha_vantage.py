"""
Test de conexión con Alpha Vantage API
Ejecutar: python3 tests/test_alpha_vantage.py
"""

import requests
import json
import sys

# TODO: Reemplazar con tu API Key real de Alpha Vantage
API_KEY = "demo"  # Cambiar después de registrarte
SYMBOL = "IBM"

def test_alpha_vantage_connection():
    """Prueba conexión básica con Alpha Vantage"""
    
    if API_KEY == "demo":
        print("⚠️  Usando API Key 'demo' - registrate en Alpha Vantage para obtener tu clave")
        print("🔗 https://www.alphavantage.co/support/#api-key\n")
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": SYMBOL,
        "apikey": API_KEY
    }
    
    print(f"🔍 Consultando precio de {SYMBOL}...")
    print(f"🌐 URL: {url}")
    print(f"📦 Params: {params}\n")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if "Global Quote" in data:
            quote = data["Global Quote"]
            price = quote.get("05. price", "N/A")
            change = quote.get("09. change", "N/A")
            change_pct = quote.get("10. change percent", "N/A")
            
            print("=" * 50)
            print("✅ CONEXIÓN EXITOSA!")
            print("=" * 50)
            print(f"📊 Símbolo: {SYMBOL}")
            print(f"💰 Precio actual: ${price}")
            print(f"📈 Cambio: {change} ({change_pct})")
            print("=" * 50)
            
            return True
            
        elif "Note" in data:
            print("⚠️  Rate limit alcanzado")
            print(f"📝 Mensaje: {data['Note']}")
            return False
            
        else:
            print("⚠️  Respuesta recibida pero sin datos de precio")
            print(f"📋 Datos recibidos: {json.dumps(data, indent=2)}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout - La API no respondió a tiempo")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
        return False

if __name__ == "__main__":
    success = test_alpha_vantage_connection()
    sys.exit(0 if success else 1)
