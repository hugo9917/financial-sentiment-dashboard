"""
Configuración de Rate Limiting para la API
Define límites de velocidad para diferentes tipos de endpoints
"""

# Configuración de Rate Limiting por tipo de endpoint
RATE_LIMITS = {
    # Autenticación - Muy restrictivo para prevenir ataques
    "auth": {
        "login": "5/minute",  # 5 intentos de login por minuto
        "register": "3/minute",  # 3 registros por minuto
        "password_reset": "2/minute",  # 2 resets por minuto
    },
    # Endpoints de datos - Moderadamente restrictivo
    "data": {
        "sentiment_summary": "60/minute",  # 60 requests por minuto
        "sentiment_timeline": "60/minute",  # 60 requests por minuto
        "stock_prices": "60/minute",  # 60 requests por minuto
        "latest_news": "60/minute",  # 60 requests por minuto
        "sentiment_by_symbol": "60/minute",  # 60 requests por minuto
        "prices_by_symbol": "60/minute",  # 60 requests por minuto
    },
    # Endpoints computacionalmente intensivos - Más restrictivo
    "analytics": {
        "correlation_analysis": "30/minute",  # 30 requests por minuto
        "dashboard_stats": "30/minute",  # 30 requests por minuto
        "machine_learning": "10/minute",  # 10 requests por minuto (futuro)
    },
    # Endpoints de sistema - Moderado
    "system": {
        "health_check": "120/minute",  # 120 requests por minuto
        "metrics": "30/minute",  # 30 requests por minuto
        "test_db": "10/minute",  # 10 requests por minuto
    },
    # Endpoints públicos - Menos restrictivo
    "public": {
        "root": "300/minute",  # 300 requests por minuto
        "docs": "200/minute",  # 200 requests por minuto
    },
}

# Configuración de excepciones por IP
WHITELIST_IPS = [
    "127.0.0.1",  # Localhost
    "::1",  # IPv6 localhost
    "10.0.0.0/8",  # Red privada
    "172.16.0.0/12",  # Red privada
    "192.168.0.0/16",  # Red privada
]

# Configuración de blacklist por IP (para bloquear IPs maliciosas)
BLACKLIST_IPS = []

# Configuración de rate limiting por usuario autenticado
AUTHENTICATED_USER_LIMITS = {
    "premium": "1000/minute",  # Usuarios premium
    "standard": "100/minute",  # Usuarios estándar
    "free": "50/minute",  # Usuarios gratuitos
}


def get_rate_limit(endpoint_type: str, endpoint_name: str) -> str:
    """
    Obtener el límite de rate limiting para un endpoint específico

    Args:
        endpoint_type: Tipo de endpoint (auth, data, analytics, system, public)
        endpoint_name: Nombre específico del endpoint

    Returns:
        String con el límite (ej: "60/minute")
    """
    try:
        return RATE_LIMITS[endpoint_type][endpoint_name]
    except KeyError:
        # Límite por defecto si no se encuentra la configuración
        return "30/minute"


def is_ip_whitelisted(ip: str) -> bool:
    """
    Verificar si una IP está en la whitelist

    Args:
        ip: Dirección IP a verificar

    Returns:
        True si la IP está en whitelist, False en caso contrario
    """
    return ip in WHITELIST_IPS


def is_ip_blacklisted(ip: str) -> bool:
    """
    Verificar si una IP está en la blacklist

    Args:
        ip: Dirección IP a verificar

    Returns:
        True si la IP está en blacklist, False en caso contrario
    """
    return ip in BLACKLIST_IPS


def get_user_rate_limit(user_role: str = "free") -> str:
    """
    Obtener el límite de rate limiting para un usuario autenticado

    Args:
        user_role: Rol del usuario (premium, standard, free)

    Returns:
        String con el límite para el usuario
    """
    return AUTHENTICATED_USER_LIMITS.get(user_role, "50/minute")
