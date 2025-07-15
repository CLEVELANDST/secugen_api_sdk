#!/bin/bash
# Script para verificar dispositivo SecuGen persistente

echo "🔍 Verificando dispositivo SecuGen persistente..."

# Verificar dispositivo USB
if lsusb | grep -q "1162:2201"; then
    echo "✅ Dispositivo USB detectado"
    lsusb | grep "1162:2201"
else
    echo "❌ Dispositivo USB no encontrado"
fi

# Verificar reglas udev
if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
    echo "✅ Reglas udev instaladas"
else
    echo "❌ Reglas udev no instaladas"
fi

# Verificar symlink
if [ -L "/dev/secugen_device" ]; then
    echo "✅ Symlink persistente funcional"
    ls -la /dev/secugen_device
else
    echo "❌ Symlink persistente no existe"
fi

# Verificar permisos
if [ -r "/dev/secugen_device" ]; then
    echo "✅ Permisos de lectura OK"
else
    echo "⚠️ Sin permisos de lectura"
fi

echo "🏁 Verificación completada"
