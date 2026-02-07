// Configuración
const API_BASE = 'https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod';

// Utilidades
function setResult(elementId, message, type = 'info') {
    const el = document.getElementById(elementId);
    if (!el) {
        console.error(`❌ Elemento no encontrado: ${elementId}`);
        return;
    }
    el.className = `result ${type}`;
    el.textContent = message;
    console.log(`📝 Resultado actualizado en ${elementId}:`, message);
}

function setLoading(elementId, loading = true) {
    const el = document.getElementById(elementId);
    if (!el) {
        console.error(`❌ Elemento no encontrado: ${elementId}`);
        return;
    }
    if (loading) {
        el.innerHTML = '<span class="loading"></span>Procesando...';
        el.className = 'result info';
        console.log(`⏳ Loading activado en ${elementId}`);
    } else {
        el.textContent = '';
        el.className = 'result';
        console.log(`✅ Loading desactivado en ${elementId}`);
    }
}

function formatJSON(obj) {
    return JSON.stringify(obj, null, 2);
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function formatDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleString();
}

// Helper para fetch con manejo de errores
async function apiFetch(url, options = {}) {
    try {
        console.log('🚀 Llamando a API:', url, 'con opciones:', options);
        
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        console.log('📥 Response status:', response.status);
        console.log('📥 Response headers:', response.headers);
        
        const data = await response.json();
        console.log('📥 Response data:', data);
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('❌ API Error:', error);
        throw error;
    }
}

// 1. Guardar precio
document.getElementById('save-price-form').addEventListener('submit', async (e) => {
    console.log('🔘 Formulario guardar precio submit');
    e.preventDefault();
    setLoading('save-result');
    
    const payload = {
        symbol: document.getElementById('symbol-save').value.trim().toUpperCase(),
        price: parseFloat(document.getElementById('price-save').value)
    };
    
    // Campos opcionales
    const volume = document.getElementById('volume-save').value;
    const change = document.getElementById('change-save').value;
    const changePercent = document.getElementById('change-percent-save').value;
    
    if (volume) payload.volume = parseInt(volume);
    if (change) payload.change = parseFloat(change);
    if (changePercent) payload.change_percent = parseFloat(changePercent);
    
    console.log('📤 Payload a enviar:', payload);
    
    try {
        const result = await apiFetch(`${API_BASE}/stock`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        console.log('✅ Precio guardado:', result);
        setResult('save-result', `✅ ${result.message}\n\nDatos guardados:\nSímbolo: ${result.data.symbol}\nPrecio: ${formatCurrency(result.data.price)}\nFecha: ${result.data.date}`, 'success');
        e.target.reset();
    } catch (error) {
        console.error('❌ Error guardando precio:', error);
        setResult('save-result', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading('save-result', false);
    }
});

// 2. Consultar último precio
document.getElementById('get-price-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    setLoading('get-result');
    
    const symbol = document.getElementById('symbol-get').value.trim().toUpperCase();
    
    try {
        const result = await apiFetch(`${API_BASE}/stock/${symbol}`);
        console.log('✅ Precio consultado:', result);
        
        let output = `📊 Último precio de ${result.data.symbol}\n`;
        output += `• Precio: ${formatCurrency(result.data.price)}\n`;
        output += `• Fecha: ${formatDate(result.data.timestamp)}\n`;
        
        if (result.data.volume) output += `• Volumen: ${result.data.volume.toLocaleString()}\n`;
        if (result.data.change) output += `• Cambio: ${formatCurrency(result.data.change)}\n`;
        if (result.data.change_percent) output += `• % Cambio: ${result.data.change_percent}%\n`;
        
        console.log('📝 Output generado para consulta:', output);
        setResult('get-result', output, 'success');
    } catch (error) {
        setResult('get-result', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading('get-result', false);
    }
});

// 3. Histórico
document.getElementById('history-form').addEventListener('submit', async (e) => {
    console.log('🔘 Formulario histórico submit');
    e.preventDefault();
    setLoading('history-result');
    
    const symbol = document.getElementById('symbol-history').value.trim().toUpperCase();
    const days = document.getElementById('days-history').value;
    const limit = document.getElementById('limit-history').value;
    
    console.log('📤 Parámetros histórico:', { symbol, days, limit });
    
    try {
        const result = await apiFetch(`${API_BASE}/stock/${symbol}/history?days=${days}&limit=${limit}`);
        console.log('✅ Histórico recibido:', result);
        
        let output = `📈 Histórico de ${result.symbol} (${result.period.days} días)\n`;
        output += `Registros: ${result.statistics.count}\n`;
        output += `Precio máximo: ${formatCurrency(result.statistics.max)}\n`;
        output += `Precio mínimo: ${formatCurrency(result.statistics.min)}\n`;
        output += `Promedio: ${formatCurrency(result.statistics.avg)}\n\n`;
        
        // Mostrar últimos 5 registros
        output += 'Últimos 5 registros:\n';
        result.data.slice(0, 5).forEach((item, i) => {
            output += `${i+1}. ${formatDate(item.timestamp)} - ${formatCurrency(item.price)}\n`;
        });
        
        console.log('📝 Output generado para histórico:', output);
        setResult('history-result', output, 'success');
    } catch (error) {
        console.error('❌ Error en histórico:', error);
        setResult('history-result', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading('history-result', false);
    }
});

// 4. Análisis técnico
document.getElementById('analyze-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    setLoading('analyze-result');
    
    const symbol = document.getElementById('symbol-analyze').value.trim().toUpperCase();
    
    try {
        const result = await apiFetch(`${API_BASE}/analyze/${symbol}`);
        
        console.log('✅ Análisis completado:', result);
        
        let output = `📊 Análisis técnico de ${result.symbol}\n`;
        output += `Fecha análisis: ${new Date(result.indicators.analysis_date).toLocaleString()}\n`;
        output += `Puntos de datos: ${result.indicators.data_points}\n\n`;
        
        // Indicadores principales
        output += 'Indicadores principales:\n';
        output += `• Precio actual: ${formatCurrency(result.indicators.current_price)}\n`;
        if (result.indicators.sma_20) output += `• SMA 20: ${formatCurrency(result.indicators.sma_20)}\n`;
        if (result.indicators.ema_12) output += `• EMA 12: ${formatCurrency(result.indicators.ema_12)}\n`;
        if (result.indicators.volatility) output += `• Volatilidad: ${result.indicators.volatility}%\n`;
        
        // Bollinger Bands
        if (result.indicators.bollinger_bands) {
            const bb = result.indicators.bollinger_bands;
            output += `\nBollinger Bands:\n`;
            output += `• Superior: ${formatCurrency(bb.upper)}\n`;
            output += `• Media: ${formatCurrency(bb.middle)}\n`;
            output += `• Inferior: ${formatCurrency(bb.lower)}\n`;
        }
        
        // Recomendación
        if (result.indicators.recommendation) {
            const rec = result.indicators.recommendation;
            output += `\n🎯 Recomendación: ${rec.action}\n`;
            output += `• Razón: ${rec.reason}\n`;
            output += `• Confianza: ${rec.confidence}\n`;
        }
        
        console.log('📝 Output generado para análisis:', output);
        setResult('analyze-result', output, 'success');
    } catch (error) {
        setResult('analyze-result', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading('analyze-result', false);
    }
});

// 5. Portfolio
document.getElementById('portfolio-btn').addEventListener('click', async () => {
    console.log('🔘 Botón portfolio clickeado');
    setLoading('portfolio-result');
    
    try {
        const result = await apiFetch(`${API_BASE}/portfolio`);
        console.log('✅ Portfolio data recibida:', result);
        
        let output = `💼 Portfolio completo\n`;
        output += `Símbolos únicos: ${result.statistics.total_symbols}\n`;
        output += `Total registros: ${result.statistics.total_records}\n`;
        output += `Precio más alto: ${formatCurrency(result.statistics.price_stats.highest)}\n`;
        output += `Precio más bajo: ${formatCurrency(result.statistics.price_stats.lowest)}\n`;
        output += `Promedio: ${formatCurrency(result.statistics.price_stats.average)}\n\n`;
        
        output += 'Símbolos en portfolio:\n';
        result.portfolio.forEach(item => {
            output += `• ${item.symbol}: ${formatCurrency(item.price)} (${formatDate(item.timestamp)})\n`;
        });
        
        console.log('📝 Output generado para portfolio:', output);
        setResult('portfolio-result', output, 'success');
    } catch (error) {
        console.error('❌ Error en portfolio:', error);
        setResult('portfolio-result', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading('portfolio-result', false);
    }
});

// 6. Fetch desde Alpha Vantage
document.getElementById('fetch-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    setLoading('fetch-result');
    
    const symbol = document.getElementById('symbol-fetch').value.trim().toUpperCase();
    
    try {
        const result = await apiFetch(`${API_BASE}/stock/fetch/${symbol}`, {
            method: 'POST'
        });
        
        let output = `🌐 Precio actualizado desde Alpha Vantage\n`;
        output += `Símbolo: ${result.symbol}\n`;
        output += `Precio: ${formatCurrency(result.price)}\n`;
        output += `Cambio: ${formatCurrency(result.change)}\n`;
        output += `% Cambio: ${result.change_percent}\n`;
        output += `Volumen: ${result.volume ? result.volume.toLocaleString() : 'N/A'}\n`;
        output += `Último día de trading: ${result.latest_trading_day || 'N/A'}\n`;
        output += `Fuente: ${result.source}\n`;
        
        setResult('fetch-result', output, 'success');
        e.target.reset();
    } catch (error) {
        setResult('fetch-result', `❌ Error: ${error.message}`, 'error');
    } finally {
        setLoading('fetch-result', false);
    }
});

// Inicialización: mostrar URL de API y verificar que todo cargue
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Frontend cargado completamente');
    document.getElementById('api-url').textContent = API_BASE;
    
    // Verificar que todos los elementos existan
    const elements = [
        'save-price-form', 'get-price-form', 'history-form', 
        'analyze-form', 'portfolio-btn', 'fetch-form',
        'save-result', 'get-result', 'history-result', 
        'analyze-result', 'portfolio-result', 'fetch-result'
    ];
    
    elements.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            console.log(`✅ Elemento encontrado: ${id}`);
        } else {
            console.error(`❌ Elemento NO encontrado: ${id}`);
        }
    });
    
    // Probar setResult con un mensaje simple
    console.log('🧪 Probando setResult...');
    setResult('save-result', '✅ Frontend listo para usar', 'success');
    setTimeout(() => {
        setResult('save-result', '');
    }, 2000);
});
