# 🗂️ Guía del Sistema de Backup Automático

## 📋 Descripción General

El sistema de backup automático protege la base de datos PostgreSQL contra pérdida de datos mediante backups semanales automáticos, compresión y rotación de archivos.

## 🏗️ Arquitectura

### Componentes
- **Contenedor de backup**: Servicio Docker dedicado con PostgreSQL client tools
- **Script de backup**: `scripts/backup_postgres.sh` - Lógica principal de backup
- **Cron job**: Ejecución automática cada domingo a las 2:00 AM
- **Volumen compartido**: `./db_backups/` - Almacenamiento persistente de backups

### Servicios Docker
```yaml
backup:
  build:
    context: .
    dockerfile: backup/Dockerfile
  environment:
    - DB_HOST=postgres
    - DB_NAME=financial_sentiment
    - DB_USER=postgres
    - DB_PASSWORD=password
  volumes:
    - ./db_backups:/backups
    - ./scripts:/scripts
  restart: always
```

## ⚙️ Configuración

### Variables de Entorno
```bash
DB_HOST=postgres          # Host de PostgreSQL
DB_NAME=financial_sentiment  # Nombre de la base de datos
DB_USER=postgres          # Usuario de PostgreSQL
DB_PASSWORD=password      # Contraseña de PostgreSQL
DB_PORT=5432             # Puerto de PostgreSQL
```

### Programación de Backups
- **Frecuencia**: Semanal (domingo a las 2:00 AM)
- **Retención**: 4 semanas (28 días)
- **Compresión**: Sí (formato .sql.gz)
- **Verificación**: Integridad automática

## 🚀 Instalación y Uso

### 1. Iniciar el Sistema
```bash
# Iniciar todos los servicios incluyendo backup
docker-compose -f docker-compose-simple.yaml up -d

# Verificar que el contenedor de backup esté corriendo
docker ps | grep backup
```

### 2. Probar el Sistema
```bash
# Ejecutar pruebas de backup
chmod +x scripts/test_backup.sh
./scripts/test_backup.sh
```

### 3. Backup Manual
```bash
# Crear backup manual
docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh backup

# Listar backups disponibles
docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh list

# Probar conectividad
docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh test
```

## 📊 Monitoreo

### Logs del Sistema
```bash
# Ver logs del contenedor de backup
docker logs proyectopuertagrande-backup-1

# Ver logs específicos de backup
docker exec proyectopuertagrande-backup-1 cat /var/log/backup.log

# Ver logs de cron
docker exec proyectopuertagrande-backup-1 cat /var/log/cron.log
```

### Verificar Backups
```bash
# Listar archivos de backup
ls -la db_backups/

# Verificar tamaño de backups
du -h db_backups/*.sql.gz

# Verificar integridad
gunzip -t db_backups/financial_sentiment_*.sql.gz
```

## 🔧 Mantenimiento

### Limpieza Automática
- Los backups se eliminan automáticamente después de 28 días
- Se mantienen máximo 4 backups semanales
- La limpieza se ejecuta después de cada backup exitoso

### Limpieza Manual
```bash
# Eliminar backups antiguos manualmente
find db_backups/ -name "financial_sentiment_*.sql.gz" -mtime +28 -delete

# Verificar espacio usado
du -sh db_backups/
```

## 🚨 Recuperación de Datos

### Restaurar Backup
```bash
# Restaurar backup específico
docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh restore financial_sentiment_20240115_020000.sql.gz
```

### Restaurar Manualmente
```bash
# Descomprimir y restaurar manualmente
gunzip -c db_backups/financial_sentiment_20240115_020000.sql.gz | \
docker exec -i proyectopuertagrande-postgres-1 psql -U postgres -d financial_sentiment
```

## 📈 Métricas y Alertas

### Métricas Disponibles
- Número de backups exitosos/fallidos
- Tamaño de backups
- Tiempo de ejecución
- Espacio en disco usado

### Alertas Recomendadas
1. **Backup fallido**: Monitorear logs de error
2. **Espacio insuficiente**: Verificar espacio en `db_backups/`
3. **Backup corrupto**: Verificar integridad con `gunzip -t`

## 🔒 Seguridad

### Buenas Prácticas
- Los backups contienen datos sensibles - proteger acceso
- Considerar encriptación de backups para producción
- Verificar permisos de archivos de backup
- Rotar credenciales de base de datos regularmente

### Configuración de Seguridad
```bash
# Establecer permisos seguros
chmod 600 db_backups/*.sql.gz

# Verificar que solo el usuario correcto tenga acceso
ls -la db_backups/
```

## 🚀 Despliegue en Producción

### Configuraciones Recomendadas
1. **Backup en la nube**: Configurar S3 o similar
2. **Encriptación**: Encriptar backups antes de subir
3. **Monitoreo**: Integrar con sistemas de alerta
4. **Retención**: Ajustar según políticas de la empresa

### Variables de Entorno para Producción
```bash
# Configurar credenciales seguras
DB_PASSWORD=your_secure_password
DB_USER=your_secure_user

# Configurar backup en la nube (opcional)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET=your-backup-bucket
```

## 🐛 Solución de Problemas

### Problemas Comunes

#### 1. Contenedor de backup no inicia
```bash
# Verificar logs
docker logs proyectopuertagrande-backup-1

# Verificar conectividad a PostgreSQL
docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh test
```

#### 2. Backup falla
```bash
# Verificar espacio en disco
df -h

# Verificar permisos
ls -la db_backups/

# Verificar conectividad
docker exec proyectopuertagrande-backup-1 /usr/local/bin/backup_postgres.sh test
```

#### 3. Cron no ejecuta backups
```bash
# Verificar que cron esté corriendo
docker exec proyectopuertagrande-backup-1 service cron status

# Verificar archivo de cron
docker exec proyectopuertagrande-backup-1 cat /etc/cron.d/backup-cron
```

## 📚 Referencias

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/app-pgdump.html)
- [Docker Volume Management](https://docs.docker.com/storage/volumes/)
- [Cron Job Scheduling](https://crontab.guru/)
- [Gzip Compression](https://www.gnu.org/software/gzip/) 