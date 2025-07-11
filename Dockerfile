# Imagen base
FROM ubuntu:20.04

# Evitar interacciones durante la instalación
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgtk2.0-dev \
    libusb-0.1-4 \
    libusb-dev \
    build-essential \
    udev \
    gcc \
    python3-dev \
    usbutils \
    libusb-1.0-0 \
    libusb-1.0-0-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear grupo y usuario para SecuGen
RUN groupadd -r secugen && \
    groupmod -g 1001 plugdev && \
    useradd -r -g secugen -G plugdev,dialout secugen

WORKDIR /app

# Configurar Python y bibliotecas
RUN mkdir -p /usr/local/lib/python3.8/dist-packages/sgfplib

# Copiar SDK y configurar
COPY --chown=secugen:secugen sdk /usr/local/lib/python3.8/dist-packages/sgfplib/

# Copiar todas las bibliotecas compartidas
COPY lib/linux3/*.so /usr/local/lib/
RUN ldconfig

# Instalar dependencias de Python como root
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir pyusb

# Copiar y aplicar reglas udev
COPY docker/99SecuGen.rules /etc/udev/rules.d/
RUN chmod 644 /etc/udev/rules.d/99SecuGen.rules && \
    chown root:root /etc/udev/rules.d/99SecuGen.rules

# Copiar el resto de archivos
COPY --chown=secugen:secugen . .

# Configurar permisos
RUN mkdir -p /app/images && \
    chown -R secugen:secugen /app && \
    chmod -R 755 /app && \
    chmod 777 /app/images && \
    chmod +x start.sh && \
    chmod -R 777 /usr/local/lib/*.so && \
    chmod -R 777 /dev/bus/usb || true

# Configurar permisos adicionales para USB
RUN chmod -R 777 /usr/local/lib/*.so && \
    chmod 666 /dev/bus/usb/*/* || true && \
    chmod 755 /dev/bus/usb && \
    chmod 755 /dev/bus/usb/* && \
    chown root:plugdev /dev/bus/usb/*/* || true && \
    ldconfig

# Cambiar al usuario secugen
USER secugen

EXPOSE 5000

CMD ["./start.sh"]