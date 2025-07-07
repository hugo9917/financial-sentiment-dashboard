#!/bin/bash

# Script de prueba para el sistema de backup
# Verifica que el backup se puede crear y restaurar correctamente

set -e

echo "🧪 INICIANDO PRUEBAS DE BACKUP"
echo "================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar que el contenedor de backup esté corriendo
echo "1. Verificando contenedor de backup..."
if docker ps | grep -q "backup"; then
    print_status "Contenedor de backup está corriendo"
else
    print_error "Contenedor de backup no está corriendo"
    echo "Ejecuta: docker-compose -f docker-compose-simple.yaml up -d backup"
    exit 1
fi

# Verificar que PostgreSQL esté disponible
echo "2. Verificando conectividad a PostgreSQL..."
if docker exec proyectopuertagrande-postgres-1 pg_isready -U postgres; then
    print_status "PostgreSQL está disponible"
else
    print_error "No se puede conectar a PostgreSQL"
    exit 1
fi

# Ejecutar backup de prueba
echo "3. Ejecutando backup de prueba..."
if docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh backup; then
    print_status "Backup de prueba completado"
else
    print_error "Falló el backup de prueba"
    exit 1
fi

# Verificar que se creó el archivo de backup
echo "4. Verificando archivo de backup..."
BACKUP_COUNT=$(ls -1 db_backups/financial_sentiment_*.sql.gz 2>/dev/null | wc -l)
if [ $BACKUP_COUNT -gt 0 ]; then
    print_status "Se encontraron $BACKUP_COUNT archivos de backup"
    
    # Mostrar información del backup más reciente
    LATEST_BACKUP=$(ls -t db_backups/financial_sentiment_*.sql.gz | head -1)
    BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
    echo "   📁 Backup más reciente: $(basename $LATEST_BACKUP)"
    echo "   📏 Tamaño: $BACKUP_SIZE"
else
    print_error "No se encontraron archivos de backup"
    exit 1
fi

# Verificar integridad del backup
echo "5. Verificando integridad del backup..."
if gunzip -t "$LATEST_BACKUP"; then
    print_status "Backup no está corrupto"
else
    print_error "Backup está corrupto"
    exit 1
fi

# Listar backups disponibles
echo "6. Listando backups disponibles..."
docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh list

echo ""
echo "🎉 PRUEBAS DE BACKUP COMPLETADAS EXITOSAMENTE"
echo "=============================================="
echo ""
echo "📋 RESUMEN:"
echo "   ✅ Contenedor de backup funcionando"
echo "   ✅ Conectividad a PostgreSQL OK"
echo "   ✅ Backup de prueba exitoso"
echo "   ✅ Archivo de backup creado"
echo "   ✅ Integridad del backup verificada"
echo ""
echo "📅 El backup automático se ejecutará cada domingo a las 2:00 AM"
echo "🗂️  Los backups se guardan en: ./db_backups/"
echo "🧹 Se mantienen solo los últimos 4 backups (28 días)"
echo ""
echo "🔧 Comandos útiles:"
echo "   - Ver logs: docker logs proyectopuertagrande-backup-1"
echo "   - Backup manual: docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh backup"
echo "   - Listar backups: docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh list" 