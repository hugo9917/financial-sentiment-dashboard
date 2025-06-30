# 🔒 Guía de Seguridad

## Credenciales y Variables de Entorno

### Archivos Sensibles
Los siguientes archivos contienen información sensible y NO deben subirse a Git:

- `config.env` - Variables de entorno con credenciales reales
- `dbt/profiles.yml` - Configuración de dbt con credenciales de base de datos
- `terraform/terraform.tfvars` - Variables de Terraform con credenciales

### Configuración Segura

#### 1. Variables de Entorno
Copia el archivo de ejemplo y configura tus credenciales:
```bash
cp config.example.env config.env
cp dbt/profiles.yml.example dbt/profiles.yml
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

#### 2. Configurar Variables de Entorno
Edita `config.env` con tus credenciales reales:
```bash
# API Keys
NEWS_API_KEY=tu_api_key_real
ALPHA_VANTAGE_API_KEY=tu_api_key_real

# Base de datos
DB_PASSWORD=tu_password_seguro

# Redshift
REDSHIFT_HOST=tu_cluster_endpoint
REDSHIFT_USER=tu_usuario
REDSHIFT_PASSWORD=tu_password_seguro
REDSHIFT_MASTER_PASSWORD=tu_master_password_seguro
```

#### 3. Configurar Terraform
Edita `terraform/terraform.tfvars`:
```bash
redshift_master_password = "${REDSHIFT_MASTER_PASSWORD}"
```

### API Keys Expuestas
Si accidentalmente subiste API keys a Git:

1. **Revoca inmediatamente las API keys** en los servicios correspondientes
2. **Genera nuevas API keys**
3. **Actualiza tu archivo config.env** con las nuevas keys
4. **Usa git filter-branch** para eliminar las keys del historial

### Comandos de Limpieza de Git

#### Eliminar archivo del historial:
```bash
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch archivo_sensible" --prune-empty --tag-name-filter cat -- --all
```

#### Forzar push después de limpieza:
```bash
git push origin main --force
```

### Verificación de Seguridad

#### Buscar credenciales hardcodeadas:
```bash
grep -r "password\|secret\|key\|token" . --exclude-dir=venv --exclude-dir=node_modules
```

#### Verificar archivos en .gitignore:
```bash
git check-ignore config.env dbt/profiles.yml terraform/terraform.tfvars
```

### Mejores Prácticas

1. **Nunca hardcodees credenciales** en el código
2. **Usa variables de entorno** para todas las credenciales
3. **Mantén archivos de ejemplo** sin credenciales reales
4. **Revisa regularmente** el historial de Git por credenciales
5. **Usa herramientas de seguridad** como pre-commit hooks
6. **Rota las credenciales** regularmente

### Servicios de API

#### Alpha Vantage
- URL: https://www.alphavantage.co/support/#api-key
- Gratuito: 500 requests/day
- Revocar key si se expone

#### News API
- URL: https://newsapi.org/register
- Gratuito: 100 requests/day
- Revocar key si se expone

### Monitoreo de Seguridad

Considera implementar:
- Pre-commit hooks para detectar credenciales
- Escaneo automático de secretos
- Rotación automática de credenciales
- Alertas de seguridad

### Contacto de Emergencia

Si encuentras un problema de seguridad:
1. Revoca inmediatamente las credenciales afectadas
2. Genera nuevas credenciales
3. Actualiza la documentación
4. Notifica al equipo 