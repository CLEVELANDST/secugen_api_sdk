#!/bin/bash
# Script para crear symlink persistente para dispositivo SecuGen

# Configuración
VENDOR_ID="1162"
PRODUCT_ID="2201"
SYMLINK_NAME="/dev/secugen_device"
UDEV_RULES_FILE="/etc/udev/rules.d/99SecuGen.rules"

# Función para mostrar mensajes
log() {
    echo "[$(date -u)] $1"
}

# Verificar permisos
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script requiere permisos de root"
    echo "💡 Ejecute: sudo $0"
    exit 1
fi

log "🔧 Configurando dispositivo SecuGen persistente..."

# Buscar el dispositivo
log "🔍 Buscando dispositivo SecuGen..."
USB_DEVICE=$(lsusb | grep "${VENDOR_ID}:${PRODUCT_ID}" | head -1)

if [ -z "$USB_DEVICE" ]; then
    log "❌ Dispositivo SecuGen no encontrado"
    log "💡 Conecte el dispositivo y vuelva a intentar"
    exit 1
fi

# Extraer información del dispositivo
BUS=$(echo $USB_DEVICE | awk '{print $2}')
DEVICE=$(echo $USB_DEVICE | awk '{print $4}' | sed 's/://g')
USB_PATH="/dev/bus/usb/${BUS}/${DEVICE}"

log "✅ Dispositivo encontrado: Bus $BUS, Device $DEVICE"
log "📍 Path USB: $USB_PATH"

# Crear reglas udev mejoradas
log "📋 Creando reglas udev..."

cat > "$UDEV_RULES_FILE" << EOF
# Reglas udev para dispositivos SecuGen
# Crear symlink persistente para el dispositivo principal
SUBSYSTEM=="usb", ATTR{idVendor}=="$VENDOR_ID", ATTR{idProduct}=="$PRODUCT_ID", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device"

# Crear symlink adicional en el directorio bus/usb
SUBSYSTEM=="usb", ATTR{idVendor}=="$VENDOR_ID", ATTR{idProduct}=="$PRODUCT_ID", SUBSYSTEM=="usb_device", MODE="0666", GROUP="plugdev", SYMLINK+="secugen_usb_device"

# Reglas adicionales para otros modelos SecuGen
SUBSYSTEM=="usb", ATTR{idVendor}=="$VENDOR_ID", ATTR{idProduct}=="0300", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device_0300"
SUBSYSTEM=="usb", ATTR{idProduct}=="0200", ATTR{idVendor}=="$VENDOR_ID", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device_0200"
SUBSYSTEM=="usb", ATTR{idProduct}=="1000", ATTR{idVendor}=="$VENDOR_ID", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device_1000"
EOF

# Configurar permisos
chmod 644 "$UDEV_RULES_FILE"
chown root:root "$UDEV_RULES_FILE"

log "✅ Reglas udev instaladas"

# Recargar reglas udev
log "🔄 Recargando reglas udev..."
udevadm control --reload-rules
udevadm trigger

# Esperar un momento
sleep 2

# Verificar si el symlink se creó correctamente
if [ -L "$SYMLINK_NAME" ]; then
    TARGET=$(readlink "$SYMLINK_NAME")
    log "✅ Symlink creado: $SYMLINK_NAME -> $TARGET"
    
    # Verificar si el target es correcto
    if [ "$TARGET" = "bus/usb/${BUS}/${DEVICE}" ]; then
        log "⚠️ Symlink relativo detectado, creando absoluto..."
        
        # Remover symlink existente
        rm -f "$SYMLINK_NAME"
        
        # Crear symlink absoluto
        ln -sf "$USB_PATH" "$SYMLINK_NAME"
        
        log "✅ Symlink absoluto creado: $SYMLINK_NAME -> $USB_PATH"
    fi
else
    log "⚠️ Symlink automático no creado, creando manualmente..."
    
    # Crear symlink manualmente
    ln -sf "$USB_PATH" "$SYMLINK_NAME"
    
    log "✅ Symlink manual creado: $SYMLINK_NAME -> $USB_PATH"
fi

# Verificar funcionamiento
if [ -e "$SYMLINK_NAME" ]; then
    FINAL_TARGET=$(readlink "$SYMLINK_NAME")
    log "🎉 Configuración completada!"
    log "📍 Dispositivo persistente: $SYMLINK_NAME"
    log "🔗 Apunta a: $FINAL_TARGET"
    
    # Verificar permisos
    if [ -r "$SYMLINK_NAME" ] && [ -w "$SYMLINK_NAME" ]; then
        log "✅ Permisos de lectura/escritura OK"
    else
        log "⚠️ Permisos insuficientes"
        chmod 666 "$FINAL_TARGET" 2>/dev/null || true
    fi
    
    # Mostrar información adicional
    log "📊 Información del dispositivo:"
    ls -la "$SYMLINK_NAME"
    
    # Crear script de verificación
    cat > "verificar_dispositivo.sh" << 'EOF'
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
EOF
    chmod +x "verificar_dispositivo.sh"
    log "✅ Script de verificación creado: verificar_dispositivo.sh"
    
else
    log "❌ Error: No se pudo crear el symlink"
    exit 1
fi

log "🎯 Para usar en aplicaciones: $SYMLINK_NAME"
log "🔧 Para verificar: ./verificar_dispositivo.sh" 