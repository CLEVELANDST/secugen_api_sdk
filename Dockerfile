# Dockerfile para SecuGen Fingerprint API
# =====================================
# Imagen base optimizada con sistema robusto integrado

FROM ubuntu:22.04

# Metadatos
LABEL maintainer="SecuGen Fingerprint API"
LABEL version="2.0.0"
LABEL description="API REST para lector de huellas SecuGen con sistema robusto"

# Variables de entorno
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_ENV=production
ENV FLASK_APP=app.py
ENV WORKDIR=/app

# Crear usuario no-root para seguridad
RUN groupadd -g 1000 secugen && \
    useradd -u 1000 -g secugen -m -s /bin/bash secugen && \
    usermod -a -G dialout,plugdev secugen

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libusb-0.1-4 \
    libusb-1.0-0 \
    build-essential \
    curl \
    wget \
    git \
    lsof \
    usbutils \
    udev \
    sudo \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR $WORKDIR

# Copiar archivos de dependencias primero (para cachear layers)
COPY requirements.txt ./

# Instalar dependencias Python
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs templates backups config

# Copiar SDK y librerías
COPY sdk/ ./sdk/
COPY lib/ ./lib/
COPY python/ ./python/

# Configurar permisos para archivos ejecutables
RUN chmod +x iniciar_sistema_robusto.sh parar_sistema.sh && \
    chmod +x reset_usb_device.py monitor_sistema_completo.py test_sistema_robusto.py && \
    chmod +x docker-entrypoint.sh

# Configurar permisos para el usuario secugen
RUN chown -R secugen:secugen $WORKDIR

# Crear archivo de configuración para supervisord
RUN echo '[supervisord]' > /etc/supervisor/conf.d/secugen.conf && \
    echo 'nodaemon=true' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'user=root' >> /etc/supervisor/conf.d/secugen.conf && \
    echo '' >> /etc/supervisor/conf.d/secugen.conf && \
    echo '[program:secugen-api]' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'command=/app/docker-entrypoint.sh' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'directory=/app' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'user=secugen' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'stderr_logfile=/app/logs/docker_error.log' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'stdout_logfile=/app/logs/docker_output.log' >> /etc/supervisor/conf.d/secugen.conf && \
    echo 'environment=PYTHONPATH="/app"' >> /etc/supervisor/conf.d/secugen.conf

# Configurar sudoers para usuario secugen (necesario para reset USB)
RUN echo 'secugen ALL=(ALL) NOPASSWD: /usr/bin/tee /sys/bus/usb/drivers/usb/unbind' >> /etc/sudoers && \
    echo 'secugen ALL=(ALL) NOPASSWD: /usr/bin/tee /sys/bus/usb/drivers/usb/bind' >> /etc/sudoers && \
    echo 'secugen ALL=(ALL) NOPASSWD: /usr/bin/tee /sys/bus/usb/devices/*/reset' >> /etc/sudoers && \
    echo 'secugen ALL=(ALL) NOPASSWD: /usr/bin/tee /sys/bus/usb/devices/*/power/control' >> /etc/sudoers && \
    echo 'secugen ALL=(ALL) NOPASSWD: /sbin/udevadm' >> /etc/sudoers && \
    echo 'secugen ALL=(ALL) NOPASSWD: /usr/sbin/lsof' >> /etc/sudoers

# Exponer puerto
EXPOSE 5000

# Volúmenes para datos persistentes
VOLUME ["/app/logs", "/app/templates", "/app/backups"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Cambiar a usuario no-root
USER secugen

# Comando de inicio
CMD ["python3", "app.py"]