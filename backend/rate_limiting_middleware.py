"""
Middleware personalizado para Rate Limiting
Incluye funcionalidades avanzadas como whitelist, blacklist y límites por usuario
"""

import logging
import time
from typing import Dict

from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from rate_limiting_config import (get_user_rate_limit, is_ip_blacklisted,
                                  is_ip_whitelisted)

logger = logging.getLogger(__name__)


class AdvancedRateLimiter:
    """
    Rate limiter avanzado con funcionalidades adicionales
    """

    def __init__(self, limiter: Limiter):
        self.limiter = limiter
        self.request_history: Dict[str, list] = {}
        self.blocked_ips: Dict[str, float] = {}

    def is_rate_limited(self, request: Request, user_role: str = "free") -> bool:
        """
        Verificar si una request está limitada por rate limiting

        Args:
            request: Request de FastAPI
            user_role: Rol del usuario (para límites personalizados)

        Returns:
            True si la request está limitada, False en caso contrario
        """
        client_ip = get_remote_address(request)

        # Verificar blacklist
        if is_ip_blacklisted(client_ip):
            logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
            return True

        # Verificar si la IP está temporalmente bloqueada
        if client_ip in self.blocked_ips:
            block_until = self.blocked_ips[client_ip]
            if time.time() < block_until:
                logger.warning(
                    f"Blocked request from temporarily blocked IP: {client_ip}"
                )
                return True
            else:
                # Remover del bloqueo temporal
                del self.blocked_ips[client_ip]

        # Verificar whitelist (bypass rate limiting)
        if is_ip_whitelisted(client_ip):
            logger.debug(f"Whitelisted IP bypassing rate limiting: {client_ip}")
            return False

        # Verificar límites por usuario autenticado
        if user_role != "free":
            user_limit = get_user_rate_limit(user_role)
            return self._check_user_limit(client_ip, user_limit)

        return False

    def _check_user_limit(self, client_ip: str, limit: str) -> bool:
        """
        Verificar límite específico para usuarios autenticados

        Args:
            client_ip: IP del cliente
            limit: Límite en formato "X/minute"

        Returns:
            True si excede el límite, False en caso contrario
        """
        try:
            requests_per_minute = int(limit.split("/")[0])
        except (ValueError, IndexError):
            requests_per_minute = 50  # Límite por defecto

        current_time = time.time()
        minute_ago = current_time - 60

        # Limpiar requests antiguos
        if client_ip in self.request_history:
            self.request_history[client_ip] = [
                req_time
                for req_time in self.request_history[client_ip]
                if req_time > minute_ago
            ]
        else:
            self.request_history[client_ip] = []

        # Verificar si excede el límite
        if len(self.request_history[client_ip]) >= requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}: "
                f"{len(self.request_history[client_ip])} requests in last minute"
            )
            return True

        # Agregar request actual
        self.request_history[client_ip].append(current_time)
        return False

    def block_ip_temporarily(self, client_ip: str, minutes: int = 5):
        """
        Bloquear una IP temporalmente

        Args:
            client_ip: IP a bloquear
            minutes: Minutos de bloqueo
        """
        self.blocked_ips[client_ip] = time.time() + (minutes * 60)
        logger.warning(
            f"Temporarily blocked IP {client_ip} for {minutes} minutes"
        )

    def get_rate_limit_info(self, client_ip: str) -> Dict:
        """
        Obtener información de rate limiting para una IP

        Args:
            client_ip: IP del cliente

        Returns:
            Diccionario con información de rate limiting
        """
        current_time = time.time()
        minute_ago = current_time - 60

        if client_ip in self.request_history:
            recent_requests = [
                req_time
                for req_time in self.request_history[client_ip]
                if req_time > minute_ago
            ]
        else:
            recent_requests = []

        is_blocked = (
            client_ip in self.blocked_ips and
            time.time() < self.blocked_ips[client_ip]
        )

        return {
            "ip": client_ip,
            "requests_last_minute": len(recent_requests),
            "is_whitelisted": is_ip_whitelisted(client_ip),
            "is_blacklisted": is_ip_blacklisted(client_ip),
            "is_temporarily_blocked": is_blocked,
            "block_until": (
                self.blocked_ips.get(client_ip, None) if is_blocked else None
            ),
        }


def create_rate_limiting_middleware(limiter: Limiter):
    """
    Crear middleware de rate limiting

    Args:
        limiter: Instancia del limiter de slowapi

    Returns:
        Función middleware
    """
    advanced_limiter = AdvancedRateLimiter(limiter)

    async def rate_limiting_middleware(request: Request, call_next):
        client_ip = get_remote_address(request)

        # Obtener rol del usuario si está autenticado
        user_role = "free"
        try:
            # Intentar obtener el usuario actual
            # current_user = await get_current_active_user(request)
            # user_role = current_user.get("role", "free")
            pass
        except Exception:
            pass  # Usuario no autenticado, usar rol por defecto

        # Verificar rate limiting
        if advanced_limiter.is_rate_limited(request, user_role):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60,
                },
            )

        # Continuar con la request
        response = await call_next(request)

        # Agregar headers de rate limiting
        rate_limit_info = advanced_limiter.get_rate_limit_info(client_ip)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, 60 - rate_limit_info["requests_last_minute"])
        )
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))

        return response

    return rate_limiting_middleware
