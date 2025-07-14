#!/bin/bash

# Debe ejecutarse como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, ejecute como root"
    exit 1
fi

# Instalar dependencias necesarias
apt-get update
apt-get install -y \
    udev \
    libusb-1.0-0 \
    libusb-1.0-0-dev

# Copiar reglas udev al host
cp docker/99SecuGen.rules /etc/udev/rules.d/
chmod 644 /etc/udev/rules.d/99SecuGen.rules
chown root:root /etc/udev/rules.d/99SecuGen.rules

# Recargar reglas udev
udevadm control --reload-rules
udevadm trigger

echo "Dependencias instaladas correctamente" 