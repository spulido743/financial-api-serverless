// Configuración del Frontend
const CONFIG = {
    API_BASE_URL: 'https://rd99h9lf9h.execute-api.us-east-1.amazonaws.com/prod',
    ENDPOINTS: {
        FETCH_PRICE: '/stock/fetch',  // POST /stock/fetch/{symbol}
        GET_STOCK: '/stock',           // GET /stock/{symbol}
        HISTORY: '/stock',             // GET /stock/{symbol}/history
        ANALYZE: '/analyze'            // GET /analyze/{symbol}
    },
    ENVIRONMENT: 'production',
    VERSION: '2.0'
};

console.log('🚀 Config loaded:', CONFIG);
