FROM postgres:15

# Instalar herramientas necesarias
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de backups
RUN mkdir -p /backups /var/log

# Copiar script de backup
COPY ../scripts/backup_postgres.sh /usr/local/bin/backup_postgres.sh
RUN chmod +x /usr/local/bin/backup_postgres.sh

# Crear archivo de configuración de cron
RUN echo "0 2 * * 0 /usr/local/bin/backup_postgres.sh backup >> /var/log/cron.log 2>&1" > /etc/cron.d/backup-cron
RUN chmod 0644 /etc/cron.d/backup-cron

# Crear script de inicio
RUN echo '#!/bin/bash\n\
# Iniciar cron\n\
service cron start\n\
\n\
# Ejecutar backup inicial si es la primera vez\n\
if [ ! -f /backups/.initialized ]; then\n\
    echo "Ejecutando backup inicial..."\n\
    /usr/local/bin/backup_postgres.sh backup\n\
    touch /backups/.initialized\n\
fi\n\
\n\
# Mantener el contenedor corriendo\n\
tail -f /var/log/backup.log /var/log/cron.log\n\
' > /usr/local/bin/start.sh

RUN chmod +x /usr/local/bin/start.sh

# Exponer volumen de backups
VOLUME ["/backups"]

# Comando por defecto
CMD ["/usr/local/bin/start.sh"] 