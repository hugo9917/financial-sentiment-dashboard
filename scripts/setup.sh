#!/bin/bash

# Script de setup para Financial Sentiment Dashboard
# Este script configura el entorno de desarrollo

set -e

echo "🚀 Configurando Financial Sentiment Dashboard..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

print_status "Docker y Docker Compose encontrados"

# Verificar que Git esté instalado
if ! command -v git &> /dev/null; then
    print_error "Git no está instalado. Por favor instala Git primero."
    exit 1
fi

print_status "Git encontrado"

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    print_status "Creando archivo .env..."
    cp env.example .env
    print_warning "Por favor edita el archivo .env con tus API keys"
else
    print_status "Archivo .env ya existe"
fi

# Crear directorios necesarios
print_status "Creando directorios necesarios..."
mkdir -p logs
mkdir -p data
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Verificar si existe config.env
if [ ! -f config.env ]; then
    print_warning "Archivo config.env no encontrado. Creando desde ejemplo..."
    if [ -f config.example.env ]; then
        cp config.example.env config.env
        print_warning "Por favor edita config.env con tus credenciales reales"
    else
        print_error "config.example.env no encontrado"
        exit 1
    fi
fi

# Construir imágenes de Docker
print_status "Construyendo imágenes de Docker..."
docker-compose -f docker-compose.dev.yml build

# Verificar que las imágenes se construyeron correctamente
if [ $? -eq 0 ]; then
    print_status "Imágenes construidas exitosamente"
else
    print_error "Error construyendo imágenes de Docker"
    exit 1
fi

# Crear red de Docker si no existe
print_status "Configurando red de Docker..."
docker network create financial_network 2>/dev/null || print_status "Red ya existe"

# Inicializar base de datos
print_status "Inicializando base de datos..."
docker-compose -f docker-compose.dev.yml up -d postgres

# Esperar a que PostgreSQL esté listo
print_status "Esperando a que PostgreSQL esté listo..."
sleep 10

# Verificar conexión a la base de datos
if docker-compose -f docker-compose.dev.yml exec -T postgres pg_isready -U postgres; then
    print_status "PostgreSQL está listo"
else
    print_error "PostgreSQL no está respondiendo"
    exit 1
fi

# Ejecutar migraciones de DBT
print_status "Ejecutando migraciones de DBT..."
docker-compose -f docker-compose.dev.yml run --rm dbt dbt deps
docker-compose -f docker-compose.dev.yml run --rm dbt dbt run

# Iniciar todos los servicios
print_status "Iniciando todos los servicios..."
docker-compose -f docker-compose.dev.yml up -d

# Esperar a que los servicios estén listos
print_status "Esperando a que los servicios estén listos..."
sleep 15

# Verificar estado de los servicios
print_status "Verificando estado de los servicios..."

# Verificar backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Backend está funcionando en http://localhost:8000"
else
    print_warning "⚠️  Backend no está respondiendo"
fi

# Verificar frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "✅ Frontend está funcionando en http://localhost:3000"
else
    print_warning "⚠️  Frontend no está respondiendo"
fi

# Verificar Grafana
if curl -f http://localhost:3001 > /dev/null 2>&1; then
    print_status "✅ Grafana está funcionando en http://localhost:3001"
else
    print_warning "⚠️  Grafana no está respondiendo"
fi

# Verificar Prometheus
if curl -f http://localhost:9090 > /dev/null 2>&1; then
    print_status "✅ Prometheus está funcionando en http://localhost:9090"
else
    print_warning "⚠️  Prometheus no está respondiendo"
fi

# Mostrar información final
echo ""
echo "🎉 ¡Setup completado!"
echo ""
echo "📊 Servicios disponibles:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • Grafana: http://localhost:3001 (admin/admin)"
echo "   • Prometheus: http://localhost:9090"
echo "   • Airflow: http://localhost:8080"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "   • Parar servicios: docker-compose -f docker-compose.dev.yml down"
echo "   • Reiniciar servicios: docker-compose -f docker-compose.dev.yml restart"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Edita config.env con tus API keys reales"
echo "   2. Ejecuta los tests: ./scripts/run-tests.sh"
echo "   3. Configura el pipeline de CI/CD en GitHub"
echo ""

print_status "Setup completado exitosamente!" 