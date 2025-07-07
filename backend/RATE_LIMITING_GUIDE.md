# 🔒 Guía de Rate Limiting

## 📋 Descripción General

El sistema de Rate Limiting implementado protege la API contra abuso y ataques, limitando el número de requests que un cliente puede hacer en un período de tiempo específico.

## 🏗️ Arquitectura

### Componentes Principales

1. **slowapi**: Biblioteca principal para rate limiting
2. **rate_limiting_config.py**: Configuración centralizada de límites
3. **rate_limiting_middleware.py**: Middleware personalizado con funcionalidades avanzadas
4. **main.py**: Integración con FastAPI

## ⚙️ Configuración

### Límites por Tipo de Endpoint

```python
RATE_LIMITS = {
    # Autenticación - Muy restrictivo
    "auth": {
        "login": "5/minute",           # 5 intentos por minuto
        "register": "3/minute",        # 3 registros por minuto
        "password_reset": "2/minute",  # 2 resets por minuto
    },
    
    # Endpoints de datos - Moderadamente restrictivo
    "data": {
        "sentiment_summary": "60/minute",      # 60 requests por minuto
        "sentiment_timeline": "60/minute",     # 60 requests por minuto
        "stock_prices": "60/minute",           # 60 requests por minuto
        "latest_news": "60/minute",            # 60 requests por minuto
    },
    
    # Endpoints computacionalmente intensivos - Más restrictivo
    "analytics": {
        "correlation_analysis": "30/minute",   # 30 requests por minuto
        "dashboard_stats": "30/minute",        # 30 requests por minuto
    },
    
    # Endpoints de sistema - Moderado
    "system": {
        "health_check": "120/minute",          # 120 requests por minuto
        "metrics": "30/minute",                # 30 requests por minuto
    },
}
```

### Límites por Usuario

```python
AUTHENTICATED_USER_LIMITS = {
    "premium": "1000/minute",     # Usuarios premium
    "standard": "100/minute",      # Usuarios estándar
    "free": "50/minute",           # Usuarios gratuitos
}
```

## 🛡️ Funcionalidades de Seguridad

### Whitelist de IPs
Las siguientes IPs están exentas de rate limiting:
- `127.0.0.1` (localhost)
- `::1` (IPv6 localhost)
- `10.0.0.0/8` (red privada)
- `172.16.0.0/12` (red privada)
- `192.168.0.0/16` (red privada)

### Blacklist de IPs
Sistema para bloquear IPs maliciosas (configurable).

### Bloqueo Temporal
Las IPs que exceden los límites pueden ser bloqueadas temporalmente.

## 📊 Endpoints de Monitoreo

### `/rate-limit/status`
Obtiene información de rate limiting para la IP actual:

```json
{
    "ip": "192.168.1.100",
    "rate_limit_info": {
        "ip": "192.168.1.100",
        "requests_last_minute": 15,
        "is_whitelisted": false,
        "is_blacklisted": false,
        "is_temporarily_blocked": false,
        "block_until": null
    },
    "timestamp": "2024-01-15T10:30:00"
}
```

### Headers de Respuesta
Todos los endpoints incluyen headers de rate limiting:

```
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705312200
```

## 🧪 Pruebas

### Script de Prueba
Ejecutar el script de prueba:

```bash
cd backend
python test_rate_limiting.py
```

### Pruebas Manuales
1. **Login Rate Limiting**: Hacer 6+ intentos de login en 1 minuto
2. **Data Endpoints**: Hacer 61+ requests a `/api/sentiment/summary` en 1 minuto
3. **Analytics Endpoints**: Hacer 31+ requests a `/api/correlation/analysis` en 1 minuto

## 🔧 Configuración Avanzada

### Modificar Límites
Editar `rate_limiting_config.py`:

```python
# Cambiar límite de login
RATE_LIMITS["auth"]["login"] = "3/minute"  # Más restrictivo

# Agregar nueva IP a whitelist
WHITELIST_IPS.append("203.0.113.0/24")
```

### Agregar Rate Limiting a Nuevos Endpoints
En `main.py`:

```python
@app.get("/api/new-endpoint")
@limiter.limit("30/minute")
async def new_endpoint(request: Request):
    # Tu código aquí
    pass
```

## 🚨 Respuestas de Error

### Rate Limit Exceeded (429)
```json
{
    "error": "Rate limit exceeded",
    "message": "Too many requests. Please try again later.",
    "retry_after": 60
}
```

## 📈 Métricas y Monitoreo

### Logs
El sistema registra automáticamente:
- Requests bloqueadas por rate limiting
- IPs temporalmente bloqueadas
- Intentos de acceso desde IPs blacklisteadas

### Métricas Disponibles
- Número de requests por IP
- Requests bloqueadas por rate limiting
- IPs temporalmente bloqueadas
- Uso de whitelist/blacklist

## 🔄 Mantenimiento

### Limpieza Automática
- Los historiales de requests se limpian automáticamente
- Los bloqueos temporales expiran automáticamente
- Las métricas se resetean periódicamente

### Monitoreo Recomendado
1. Revisar logs de rate limiting diariamente
2. Monitorear métricas de requests bloqueadas
3. Ajustar límites según el uso real
4. Actualizar whitelist/blacklist según sea necesario

## 🚀 Despliegue

### Variables de Entorno
```bash
# Configurar Redis para rate limiting (opcional)
REDIS_URL=redis://localhost:6379

# Configurar límites personalizados
RATE_LIMIT_LOGIN=5/minute
RATE_LIMIT_DATA=60/minute
RATE_LIMIT_ANALYTICS=30/minute
```

### Docker
El rate limiting funciona sin Redis en desarrollo, pero para producción se recomienda configurar Redis para persistencia.

## 📚 Referencias

- [slowapi Documentation](https://github.com/laurentS/slowapi)
- [FastAPI Rate Limiting](https://fastapi.tiangolo.com/tutorial/security/)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques) 