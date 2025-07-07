"""
Script de prueba para verificar el funcionamiento del Rate Limiting
"""

import requests
import time
import json
from typing import Dict, List

class RateLimitTester:
    """Clase para probar el rate limiting de la API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """
        Probar un endpoint específico
        
        Args:
            endpoint: Endpoint a probar
            method: Método HTTP
            data: Datos para POST/PUT
        
        Returns:
            Respuesta de la API
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, data=data)
            else:
                raise ValueError(f"Método no soportado: {method}")
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
        except Exception as e:
            return {
                "status_code": 0,
                "error": str(e),
                "body": None
            }
    
    def test_rate_limiting(self, endpoint: str, max_requests: int = 10, delay: float = 0.1) -> List[Dict]:
        """
        Probar rate limiting en un endpoint específico
        
        Args:
            endpoint: Endpoint a probar
            max_requests: Número máximo de requests a hacer
            delay: Delay entre requests en segundos
        
        Returns:
            Lista de respuestas
        """
        print(f"🧪 Probando rate limiting en: {endpoint}")
        print(f"📊 Haciendo {max_requests} requests con delay de {delay}s")
        
        responses = []
        
        for i in range(max_requests):
            print(f"  Request {i+1}/{max_requests}...")
            response = self.test_endpoint(endpoint)
            responses.append(response)
            
            # Mostrar resultado
            if response["status_code"] == 200:
                print(f"    ✅ 200 OK")
            elif response["status_code"] == 429:
                print(f"    ⚠️  429 Rate Limited")
            else:
                print(f"    ❌ {response['status_code']} Error")
            
            time.sleep(delay)
        
        return responses
    
    def test_login_rate_limiting(self) -> List[Dict]:
        """Probar rate limiting en el endpoint de login"""
        print("\n🔐 Probando Rate Limiting en Login")
        print("=" * 50)
        
        responses = []
        
        # Hacer 10 intentos de login (debería limitar después de 5)
        for i in range(10):
            print(f"  Intento de login {i+1}/10...")
            
            data = {
                "username": "test_user",
                "password": "wrong_password"
            }
            
            response = self.test_endpoint("/auth/login", method="POST", data=data)
            responses.append(response)
            
            if response["status_code"] == 200:
                print(f"    ✅ 200 OK (login exitoso)")
            elif response["status_code"] == 401:
                print(f"    ❌ 401 Unauthorized (credenciales incorrectas)")
            elif response["status_code"] == 429:
                print(f"    ⚠️  429 Rate Limited (demasiados intentos)")
            else:
                print(f"    ❓ {response['status_code']} Otro error")
            
            time.sleep(0.1)  # Pequeño delay entre intentos
        
        return responses
    
    def test_data_endpoints(self) -> Dict[str, List[Dict]]:
        """Probar rate limiting en endpoints de datos"""
        print("\n📊 Probando Rate Limiting en Endpoints de Datos")
        print("=" * 50)
        
        endpoints = [
            "/api/sentiment/summary",
            "/api/sentiment/timeline", 
            "/api/stocks/prices",
            "/api/news/latest",
            "/api/correlation/analysis"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            print(f"\n🔍 Probando: {endpoint}")
            responses = self.test_rate_limiting(endpoint, max_requests=15, delay=0.05)
            results[endpoint] = responses
            
            # Analizar resultados
            success_count = sum(1 for r in responses if r["status_code"] == 200)
            rate_limited_count = sum(1 for r in responses if r["status_code"] == 429)
            
            print(f"  📈 Resultados: {success_count} exitosos, {rate_limited_count} rate limited")
        
        return results
    
    def test_rate_limit_status(self) -> Dict:
        """Probar el endpoint de estado de rate limiting"""
        print("\n📊 Probando Endpoint de Estado de Rate Limiting")
        print("=" * 50)
        
        response = self.test_endpoint("/rate-limit/status")
        
        if response["status_code"] == 200:
            print("  ✅ Endpoint de estado funcionando")
            print(f"  📋 Información: {json.dumps(response['body'], indent=2)}")
        else:
            print(f"  ❌ Error: {response['status_code']}")
        
        return response
    
    def run_full_test(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS DE RATE LIMITING")
        print("=" * 60)
        
        # Probar estado de rate limiting
        self.test_rate_limit_status()
        
        # Probar login rate limiting
        login_results = self.test_login_rate_limiting()
        
        # Probar endpoints de datos
        data_results = self.test_data_endpoints()
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE PRUEBAS")
        print("=" * 60)
        
        # Analizar resultados de login
        login_rate_limited = sum(1 for r in login_results if r["status_code"] == 429)
        print(f"🔐 Login Rate Limiting: {login_rate_limited} requests bloqueadas de 10")
        
        # Analizar resultados de datos
        total_data_requests = 0
        total_data_rate_limited = 0
        
        for endpoint, responses in data_results.items():
            rate_limited = sum(1 for r in responses if r["status_code"] == 429)
            total_data_requests += len(responses)
            total_data_rate_limited += rate_limited
            print(f"📊 {endpoint}: {rate_limited} rate limited de {len(responses)} requests")
        
        print(f"\n📈 Total: {total_data_rate_limited} rate limited de {total_data_requests} requests")
        
        if total_data_rate_limited > 0:
            print("✅ Rate limiting funcionando correctamente!")
        else:
            print("⚠️  No se detectó rate limiting - verificar configuración")

if __name__ == "__main__":
    # Crear tester
    tester = RateLimitTester()
    
    # Ejecutar pruebas
    tester.run_full_test() 