#!/bin/bash
# Script para configurar dispositivo SecuGen persistente

# Verificar permisos
if [ "$EUID" -ne 0 ]; then
    echo "Por favor ejecute como root: sudo $0"
    exit 1
fi

# Instalar reglas udev
if [ ! -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
    echo "Instalando reglas udev..."
    cp docker/99SecuGen.rules /etc/udev/rules.d/99SecuGen.rules
    chmod 644 /etc/udev/rules.d/99SecuGen.rules
    chown root:root /etc/udev/rules.d/99SecuGen.rules
fi

# Recargar reglas
echo "Recargando reglas udev..."
udevadm control --reload-rules
udevadm trigger

# Esperar
sleep 2

# Verificar
if [ -L "/dev/secugen_device" ]; then
    echo "✅ Dispositivo persistente configurado: /dev/secugen_device"
    ls -la /dev/secugen_device
else
    echo "❌ Error: Symlink persistente no creado"
    exit 1
fi

echo "✅ Configuración completada"
