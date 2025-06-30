#!/usr/bin/env python3
"""
Script principal para ejecutar las correcciones de prioridad alta del proyecto.
"""

import subprocess
import sys
import os
import time

def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado."""
    print(f"\n🔧 {description}")
    print(f"Comando: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Salida: {result.stdout}")
        if result.stderr:
            print(f"Errores: {result.stderr}")
        print(f"Código de salida: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return False

def main():
    """Ejecutar las correcciones de prioridad alta."""
    print("🚀 INICIANDO CORRECCIONES DE PRIORIDAD ALTA")
    print("=" * 60)
    
    # 1. Verificar que Docker esté corriendo
    print("\n1️⃣ Verificando servicios Docker...")
    if not run_command("docker ps", "Verificando contenedores activos"):
        print("❌ Error: Docker no está corriendo o hay problemas")
        return
    
    # 2. Reiniciar servicios con nueva configuración
    print("\n2️⃣ Reiniciando servicios con nueva configuración...")
    if not run_command("docker-compose -f docker-compose-simple.yaml down", "Deteniendo servicios"):
        print("⚠️ Advertencia: Error al detener servicios")
    
    if not run_command("docker-compose -f docker-compose-simple.yaml up -d", "Iniciando servicios"):
        print("❌ Error: No se pudieron iniciar los servicios")
        return
    
    # 3. Esperar a que PostgreSQL esté listo
    print("\n3️⃣ Esperando a que PostgreSQL esté listo...")
    time.sleep(10)
    
    # 4. Probar conexión desde backend
    print("\n4️⃣ Probando conexión a PostgreSQL...")
    if not run_command("docker exec proyectopuertagrande-backend-1 python /app/test_db_connection.py", "Probando conexión desde backend"):
        print("❌ Error: No se pudo conectar a PostgreSQL")
        return
    
    # 5. Poblar base de datos con datos reales
    print("\n5️⃣ Poblando base de datos con datos reales...")
    if not run_command("docker exec proyectopuertagrande-backend-1 python /app/populate_real_data.py", "Poblando datos reales"):
        print("❌ Error: No se pudieron poblar los datos")
        return
    
    # 6. Verificar datos insertados
    print("\n6️⃣ Verificando datos insertados...")
    if not run_command("docker exec proyectopuertagrande-backend-1 python /app/test_db_connection.py", "Verificando datos finales"):
        print("⚠️ Advertencia: Error al verificar datos")
    
    print("\n🎉 CORRECCIONES COMPLETADAS!")
    print("=" * 60)
    print("✅ PostgreSQL configurado correctamente")
    print("✅ Base de datos poblada con datos reales")
    print("✅ Dashboard listo para usar")
    print("\n🌐 Para acceder al dashboard:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")

if __name__ == "__main__":
    main() 