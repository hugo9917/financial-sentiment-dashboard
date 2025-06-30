# dbt Configuration

Este directorio contiene la configuración de dbt para el proyecto de análisis de sentimiento financiero.

## Configuración de Credenciales

### 1. Variables de Entorno Requeridas

Para que dbt funcione correctamente, necesitas configurar las siguientes variables de entorno:

```bash
# Redshift Configuration
REDSHIFT_HOST=your_redshift_cluster_endpoint
REDSHIFT_USER=your_redshift_username
REDSHIFT_PASSWORD=your_redshift_password
REDSHIFT_PORT=5439
REDSHIFT_DBNAME=dev
```

### 2. Configuración del Perfil

1. Copia el archivo de ejemplo:
   ```bash
   cp profiles.yml.example profiles.yml
   ```

2. Configura las variables de entorno en tu archivo `.env` o en tu sistema.

### 3. Verificación

Para verificar que la configuración es correcta:

```bash
dbt debug
```

## Estructura del Proyecto

- `models/`: Modelos de dbt
  - `staging/`: Modelos de staging (datos crudos)
  - `marts/`: Modelos de marts (datos procesados)
- `profiles.yml`: Configuración de conexiones (NO subir a Git)
- `profiles.yml.example`: Ejemplo de configuración
- `dbt_project.yml`: Configuración del proyecto

## Comandos Útiles

```bash
# Ejecutar todos los modelos
dbt run

# Ejecutar un modelo específico
dbt run --select model_name

# Ejecutar tests
dbt test

# Generar documentación
dbt docs generate
dbt docs serve

# Limpiar
dbt clean
```

## Seguridad

⚠️ **IMPORTANTE**: El archivo `profiles.yml` contiene credenciales sensibles y NO debe subirse a Git. Está incluido en `.gitignore` para evitar este problema.

Si accidentalmente subiste credenciales a Git:
1. Cambia inmediatamente las credenciales en Redshift
2. Usa `git filter-branch` o `BFG Repo-Cleaner` para eliminar las credenciales del historial
3. Configura las variables de entorno correctamente 