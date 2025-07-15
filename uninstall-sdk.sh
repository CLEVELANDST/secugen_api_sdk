#!/bin/bash

# Script para desinstalar SDK de SecuGen del sistema host

echo "🗑️ Desinstalando SDK de SecuGen del sistema host..."

# Verificar si se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script debe ejecutarse como root (sudo)"
   exit 1
fi

echo "📁 Eliminando librerías SecuGen de /usr/lib/..."
rm -f /usr/lib/libsgfdu*.so*
rm -f /usr/lib/libsgfp*.so*
rm -f /usr/lib/libsgnfiq*.so*
rm -f /usr/lib/libjnisgfplib*.so*
rm -f /usr/lib/libpysgfplib*.so*

echo "🔧 Actualizando cache de librerías..."
ldconfig

echo "🔗 Eliminando reglas udev para SecuGen..."
rm -f /etc/udev/rules.d/99-secugen.rules

echo "🔄 Recargando reglas udev..."
udevadm control --reload-rules
udevadm trigger

echo "✅ SDK de SecuGen desinstalado correctamente del sistema host"
echo ""
echo "📋 Nota: El usuario sigue en el grupo plugdev"
echo "Para eliminarlo ejecutar: sudo deluser \$USER plugdev" 