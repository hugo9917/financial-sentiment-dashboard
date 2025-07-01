FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /dbt

# Copiar requirements y instalar dbt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de DBT
COPY . .

# Crear usuario no-root
RUN groupadd -r dbtuser && useradd -r -g dbtuser dbtuser
RUN chown -R dbtuser:dbtuser /dbt
USER dbtuser

# Variables de entorno
ENV DBT_PROFILES_DIR=/dbt

# Comando por defecto
CMD ["tail", "-f", "/dev/null"] 