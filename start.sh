#!/bin/bash

echo "🚀 Iniciando Proyecto Puerta Grande - Pipeline de Datos Financieros"
echo "================================================================"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde env.example..."
    cp env.example .env
    echo "✅ Archivo .env creado. Puedes editarlo si necesitas cambiar configuraciones."
fi

# Inicializar Airflow si es la primera vez
if [ ! -d "logs" ]; then
    echo "🔧 Inicializando Airflow..."
    docker-compose --profile init up airflow-init
    echo "✅ Airflow inicializado correctamente."
fi

# Construir las imágenes
echo "🔨 Construyendo imágenes Docker..."
docker-compose build --no-cache

# Iniciar todos los servicios
echo "🚀 Iniciando todos los servicios..."
docker-compose up -d

# Esperar un momento para que los servicios se inicien
echo "⏳ Esperando que los servicios se inicien..."
sleep 30

# Verificar el estado de los servicios
echo "🔍 Verificando estado de los servicios..."
docker-compose ps

echo ""
echo "🎉 ¡Proyecto iniciado correctamente!"
echo ""
echo "📊 Servicios disponibles:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • Airflow UI: http://localhost:8080 (usuario: airflow, contraseña: airflow)"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo ""
echo "📋 Comandos útiles:"
echo "   • Ver logs: docker-compose logs -f"
echo "   • Detener servicios: docker-compose down"
echo "   • Reiniciar servicios: docker-compose restart"
echo "   • Ver estado: docker-compose ps"
echo ""
echo "🔧 Para desarrollo:"
echo "   • Los cambios en el código se reflejan automáticamente"
echo "   • Los logs se pueden ver con: docker-compose logs -f [servicio]"
echo "" 