#!/bin/bash
echo "🔍 Verificando dispositivo SecuGen persistente..."
echo "📍 Symlink: /dev/secugen_device"

if [ -L "/dev/secugen_device" ]; then
    echo "✅ Symlink existe"
    TARGET=$(readlink "/dev/secugen_device")
    echo "🔗 Apunta a: $TARGET"
    
    if [ -e "/dev/secugen_device" ]; then
        echo "✅ Target accesible"
        ls -la "/dev/secugen_device"
    else
        echo "❌ Target no accesible"
    fi
else
    echo "❌ Symlink no existe"
fi

echo "📋 Dispositivos USB SecuGen:"
lsusb | grep "1162:2201" || echo "❌ No encontrado"
