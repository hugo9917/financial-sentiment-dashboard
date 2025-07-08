#!/usr/bin/env python3
"""
Script de prueba para verificar las implementaciones del proyecto
"""

import requests
import json
import time
import sys
from datetime import datetime
import os

# Configuración
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"


def print_status(message, status="INFO"):
    """Imprimir mensaje con formato"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "SUCCESS":
        print(f"✅ [{timestamp}] {message}")
    elif status == "ERROR":
        print(f"❌ [{timestamp}] {message}")
    elif status == "WARNING":
        print(f"⚠️  [{timestamp}] {message}")
    else:
        print(f"ℹ️  [{timestamp}] {message}")


def test_backend_health():
    """Probar health check del backend"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_status(f"Backend health check: {data['status']}", "SUCCESS")
            return True
        else:
            print_status(
                f"Backend health check failed: {response.status_code}", "ERROR"
            )
            return False
    except Exception as e:
        print_status(f"Backend health check error: {str(e)}", "ERROR")
        return False


def test_authentication():
    """Probar sistema de autenticación"""
    try:
        # Probar login
        login_data = {
            "username": "admin",
            "password": os.getenv("ADMIN_PASSWORD", "admin123"),
        }

        response = requests.post(f"{BASE_URL}/auth/login", data=login_data, timeout=10)

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_status("Login exitoso", "SUCCESS")

            # Probar endpoint protegido
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                print_status(f"Usuario autenticado: {user_data['username']}", "SUCCESS")
                return True
            else:
                print_status("Error al obtener datos del usuario", "ERROR")
                return False
        else:
            print_status(f"Login falló: {response.status_code}", "ERROR")
            return False

    except Exception as e:
        print_status(f"Error en autenticación: {str(e)}", "ERROR")
        return False


def test_api_endpoints():
    """Probar endpoints de la API"""
    endpoints = [
        "/api/sentiment/summary",
        "/api/news/latest",
        "/api/dashboard/stats",
        "/api/stocks/prices",
    ]

    success_count = 0

    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_status(f"✅ {endpoint}: OK", "SUCCESS")
                success_count += 1
            else:
                print_status(f"❌ {endpoint}: {response.status_code}", "ERROR")
        except Exception as e:
            print_status(f"❌ {endpoint}: {str(e)}", "ERROR")

    return success_count == len(endpoints)


def test_database_connection():
    """Probar conexión a la base de datos"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            db_status = data.get("database", "unknown")
            if db_status == "connected":
                print_status("Base de datos conectada", "SUCCESS")
                return True
            else:
                print_status(f"Base de datos: {db_status}", "WARNING")
                return False
        else:
            print_status("No se pudo verificar la base de datos", "ERROR")
            return False
    except Exception as e:
        print_status(f"Error al verificar base de datos: {str(e)}", "ERROR")
        return False


def test_frontend_access():
    """Probar acceso al frontend"""
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print_status("Frontend accesible", "SUCCESS")
            return True
        else:
            print_status(f"Frontend no accesible: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Error al acceder al frontend: {str(e)}", "ERROR")
        return False


def run_all_tests():
    """Ejecutar todas las pruebas"""
    print_status("🚀 Iniciando pruebas del proyecto...")
    print("=" * 50)

    tests = [
        ("Backend Health Check", test_backend_health),
        ("Database Connection", test_database_connection),
        ("Authentication System", test_authentication),
        ("API Endpoints", test_api_endpoints),
        ("Frontend Access", test_frontend_access),
    ]

    results = []

    for test_name, test_func in tests:
        print_status(f"Probando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Error en {test_name}: {str(e)}", "ERROR")
            results.append((test_name, False))
        print()

    # Resumen
    print("=" * 50)
    print_status("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print()
    print_status(
        f"Resultado: {passed}/{total} pruebas pasaron",
        "SUCCESS" if passed == total else "WARNING",
    )

    if passed == total:
        print_status(
            "🎉 ¡Todas las pruebas pasaron! El proyecto está funcionando correctamente.",
            "SUCCESS",
        )
    else:
        print_status(
            "⚠️  Algunas pruebas fallaron. Revisa los errores arriba.", "WARNING"
        )

    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("Pruebas interrumpidas por el usuario", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error general: {str(e)}", "ERROR")
        sys.exit(1)
