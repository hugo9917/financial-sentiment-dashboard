#!/bin/bash

# Script para ejecutar todos los tests del proyecto

set -e

echo "🧪 Ejecutando tests del Financial Sentiment Dashboard..."

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

# Función para ejecutar tests del backend
run_backend_tests() {
    print_status "Ejecutando tests del backend..."
    cd backend
    
    # Instalar dependencias si no están instaladas
    if [ ! -d "venv" ]; then
        print_status "Creando entorno virtual..."
        python -m venv venv
    fi
    
    source venv/bin/activate
    
    # Instalar dependencias
    pip install -r requirements.txt
    
    # Ejecutar linting
    print_status "Ejecutando linting..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    # Verificar formato con black
    print_status "Verificando formato con black..."
    black --check --diff .
    
    # Verificar imports con isort
    print_status "Verificando imports con isort..."
    isort --check-only --diff .
    
    # Ejecutar tests
    print_status "Ejecutando tests con pytest..."
    pytest --cov=. --cov-report=term-missing --cov-report=html
    
    deactivate
    cd ..
}

# Función para ejecutar tests del frontend
run_frontend_tests() {
    print_status "Ejecutando tests del frontend..."
    cd frontend
    
    # Instalar dependencias si no están instaladas
    if [ ! -d "node_modules" ]; then
        print_status "Instalando dependencias de Node.js..."
        npm install
    fi
    
    # Ejecutar linting
    print_status "Ejecutando linting..."
    npm run lint
    
    # Verificar tipos
    print_status "Verificando tipos con TypeScript..."
    npm run type-check
    
    # Ejecutar tests
    print_status "Ejecutando tests con Vitest..."
    npm run test:coverage
    
    cd ..
}

# Función para ejecutar tests de DBT
run_dbt_tests() {
    print_status "Ejecutando tests de DBT..."
    cd dbt
    
    # Verificar que la base de datos esté disponible
    if ! docker-compose -f ../docker-compose.dev.yml exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        print_warning "PostgreSQL no está disponible. Iniciando servicios..."
        docker-compose -f ../docker-compose.dev.yml up -d postgres
        sleep 10
    fi
    
    # Ejecutar tests de DBT
    docker-compose -f ../docker-compose.dev.yml run --rm dbt dbt test
    
    cd ..
}

# Función para ejecutar tests de Terraform
run_terraform_tests() {
    print_status "Verificando configuración de Terraform..."
    cd terraform
    
    # Verificar formato
    terraform fmt -check -recursive
    
    # Inicializar Terraform
    terraform init
    
    # Validar configuración
    terraform validate
    
    # Plan para verificar sintaxis
    terraform plan -no-color > /dev/null
    
    cd ..
}

# Función para ejecutar tests de seguridad
run_security_tests() {
    print_status "Ejecutando tests de seguridad..."
    
    # Verificar dependencias vulnerables en Python
    if command -v safety &> /dev/null; then
        print_status "Verificando vulnerabilidades en dependencias Python..."
        cd backend
        source venv/bin/activate
        safety check
        deactivate
        cd ..
    else
        print_warning "safety no está instalado. Instala con: pip install safety"
    fi
    
    # Verificar dependencias vulnerables en Node.js
    if command -v npm-audit &> /dev/null; then
        print_status "Verificando vulnerabilidades en dependencias Node.js..."
        cd frontend
        npm audit
        cd ..
    else
        print_warning "npm audit no disponible"
    fi
}

# Función para generar reporte de cobertura
generate_coverage_report() {
    print_status "Generando reporte de cobertura..."
    
    # Crear directorio para reportes
    mkdir -p reports
    
    # Copiar reportes de cobertura
    if [ -d "backend/htmlcov" ]; then
        cp -r backend/htmlcov reports/backend-coverage
    fi
    
    if [ -d "frontend/coverage" ]; then
        cp -r frontend/coverage reports/frontend-coverage
    fi
    
    print_status "Reportes de cobertura guardados en reports/"
}

# Función principal
main() {
    local test_type=${1:-all}
    
    case $test_type in
        "backend")
            run_backend_tests
            ;;
        "frontend")
            run_frontend_tests
            ;;
        "dbt")
            run_dbt_tests
            ;;
        "terraform")
            run_terraform_tests
            ;;
        "security")
            run_security_tests
            ;;
        "all")
            run_backend_tests
            run_frontend_tests
            run_dbt_tests
            run_terraform_tests
            run_security_tests
            generate_coverage_report
            ;;
        *)
            print_error "Tipo de test no válido: $test_type"
            echo "Tipos disponibles: backend, frontend, dbt, terraform, security, all"
            exit 1
            ;;
    esac
    
    print_status "✅ Tests completados exitosamente!"
}

# Ejecutar función principal
main "$@" 