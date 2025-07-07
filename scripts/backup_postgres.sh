#!/bin/bash

# Script de backup automático para PostgreSQL
# Se ejecuta semanalmente (domingo a las 2:00 AM)

set -e

# Configuración
DB_HOST="${DB_HOST:-postgres}"
DB_NAME="${DB_NAME:-financial_sentiment}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-password}"
DB_PORT="${DB_PORT:-5432}"

# Directorio de backups
BACKUP_DIR="/backups"
BACKUP_FILE="financial_sentiment_$(date +%Y%m%d_%H%M%S).sql.gz"

# Logging
LOG_FILE="/var/log/backup.log"
echo "$(date): Iniciando backup de PostgreSQL" >> $LOG_FILE

# Función para limpiar backups antiguos (mantener solo 4 semanas)
cleanup_old_backups() {
    echo "$(date): Limpiando backups antiguos..." >> $LOG_FILE
    find $BACKUP_DIR -name "financial_sentiment_*.sql.gz" -mtime +28 -delete
    echo "$(date): Limpieza completada" >> $LOG_FILE
}

# Función para hacer el backup
perform_backup() {
    echo "$(date): Iniciando backup de $DB_NAME..." >> $LOG_FILE
    
    # Crear backup comprimido
    PGPASSWORD=$DB_PASSWORD pg_dump \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        --verbose \
        --no-password \
        | gzip > "$BACKUP_DIR/$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "$(date): Backup completado exitosamente: $BACKUP_FILE" >> $LOG_FILE
        
        # Verificar el tamaño del backup
        BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
        echo "$(date): Tamaño del backup: $BACKUP_SIZE" >> $LOG_FILE
        
        # Limpiar backups antiguos
        cleanup_old_backups
        
        return 0
    else
        echo "$(date): ERROR - Fallo en el backup" >> $LOG_FILE
        return 1
    fi
}

# Función para verificar conectividad
check_connection() {
    echo "$(date): Verificando conectividad a PostgreSQL..." >> $LOG_FILE
    
    PGPASSWORD=$DB_PASSWORD pg_isready \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME
    
    if [ $? -eq 0 ]; then
        echo "$(date): Conexión a PostgreSQL exitosa" >> $LOG_FILE
        return 0
    else
        echo "$(date): ERROR - No se puede conectar a PostgreSQL" >> $LOG_FILE
        return 1
    fi
}

# Función para restaurar backup (para testing)
restore_backup() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        echo "Uso: $0 restore <archivo_backup>"
        exit 1
    fi
    
    if [ ! -f "$BACKUP_DIR/$backup_file" ]; then
        echo "ERROR: Archivo de backup no encontrado: $backup_file"
        exit 1
    fi
    
    echo "$(date): Restaurando backup: $backup_file" >> $LOG_FILE
    
    PGPASSWORD=$DB_PASSWORD psql \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
    
    gunzip -c "$BACKUP_DIR/$backup_file" | PGPASSWORD=$DB_PASSWORD psql \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME
    
    echo "$(date): Restauración completada" >> $LOG_FILE
}

# Función para listar backups disponibles
list_backups() {
    echo "$(date): Listando backups disponibles..." >> $LOG_FILE
    ls -la $BACKUP_DIR/financial_sentiment_*.sql.gz 2>/dev/null || echo "No hay backups disponibles"
}

# Main script
case "${1:-backup}" in
    "backup")
        check_connection && perform_backup
        ;;
    "restore")
        restore_backup $2
        ;;
    "list")
        list_backups
        ;;
    "test")
        check_connection
        ;;
    *)
        echo "Uso: $0 [backup|restore <archivo>|list|test]"
        echo "  backup  - Crear backup (default)"
        echo "  restore - Restaurar backup"
        echo "  list    - Listar backups disponibles"
        echo "  test    - Probar conectividad"
        exit 1
        ;;
esac 