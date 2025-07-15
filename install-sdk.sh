#!/bin/bash

# Script para instalar SDK de SecuGen en el sistema host
# Debe ejecutarse ANTES de docker-compose up

echo "🚀 Instalando SDK de SecuGen en el sistema host..."

# Verificar si se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script debe ejecutarse como root (sudo)"
   exit 1
fi

# Verificar que existe la carpeta lib/linux3
if [ ! -d "lib/linux3" ]; then
    echo "❌ Error: No se encuentra la carpeta lib/linux3"
    echo "   Asegúrate de ejecutar este script desde el directorio del proyecto"
    exit 1
fi

echo "📁 Copiando librerías SecuGen a /usr/lib/..."
cp lib/linux3/*.so /usr/lib/

echo "🔧 Actualizando cache de librerías..."
ldconfig

echo "👥 Creando grupo plugdev si no existe..."
groupadd -f plugdev

echo "🔗 Creando reglas udev para SecuGen..."
cat > /etc/udev/rules.d/99-secugen.rules << 'EOF'
# Reglas udev para dispositivos SecuGen
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="0300", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device_0300"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="0200", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device_0200"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="1000", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device_1000"
EOF

echo "🔄 Recargando reglas udev..."
udevadm control --reload-rules
udevadm trigger

echo "👤 Agregando usuario actual al grupo plugdev..."
USER_NAME="${SUDO_USER:-$USER}"
if [ "$USER_NAME" != "root" ]; then
    usermod -a -G plugdev "$USER_NAME"
    echo "   Usuario $USER_NAME agregado al grupo plugdev"
else
    echo "   ⚠️  No se pudo determinar el usuario. Agregar manualmente al grupo plugdev"
fi

echo "✅ SDK de SecuGen instalado correctamente en el sistema host"
echo ""
echo "📋 Pasos siguientes:"
echo "1. Reiniciar sesión o ejecutar: newgrp plugdev"
echo "2. Conectar el dispositivo SecuGen"
echo "3. Ejecutar: docker-compose up --build"
echo ""
echo "🔍 Para verificar la instalación:"
echo "   ldd /usr/lib/libsgfdu06.so"
echo "   ls -la /dev/secugen*" 