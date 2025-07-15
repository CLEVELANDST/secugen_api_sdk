#!/bin/bash

# Script simple para fijar dispositivo SecuGen en puerto USB específico
# Uso: sudo ./puerto_fijo_simple.sh [puerto_usb]

VENDOR_ID="1162"
PRODUCT_ID="2201"
PUERTO_DESEADO=${1:-"2-1"}  # Puerto por defecto

# Verificar root
if [[ $EUID -ne 0 ]]; then
    echo "❌ Este script requiere permisos de root"
    echo "Uso: sudo $0 [puerto_usb]"
    exit 1
fi

echo "🔍 Configurando puerto fijo para dispositivo SecuGen..."
echo "   Vendor ID: $VENDOR_ID"
echo "   Product ID: $PRODUCT_ID"
echo "   Puerto deseado: $PUERTO_DESEADO"

# 1. Crear reglas udev mejoradas
echo "📝 Creando reglas udev..."
cat > /etc/udev/rules.d/99-secugen-puerto-fijo.rules << EOF
# Reglas para fijar dispositivo SecuGen en puerto específico
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", SYMLINK+="secugen_device"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", ATTR{power/autosuspend}="-1"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", ATTR{power/control}="on"
EOF

# 2. Crear script de reubicación automática
echo "🔧 Creando script de reubicación..."
cat > /usr/local/bin/secugen_relocate.sh << 'EOF'
#!/bin/bash
# Script para reubicar dispositivo SecuGen al puerto preferido

VENDOR_ID="1162"
PRODUCT_ID="2201"
PUERTO_PREFERIDO="2-1"

# Función para encontrar el dispositivo actual
find_current_device() {
    for device in /sys/bus/usb/devices/*; do
        if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
            vendor=$(cat "$device/idVendor" 2>/dev/null)
            product=$(cat "$device/idProduct" 2>/dev/null)
            
            if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                echo $(basename "$device")
                return 0
            fi
        fi
    done
    return 1
}

# Función para hacer soft reset del dispositivo
soft_reset_device() {
    local device_path=$1
    echo "🔄 Realizando soft reset del dispositivo..."
    
    # Deshabilitar autosuspend
    echo -1 > "/sys/bus/usb/devices/$device_path/power/autosuspend" 2>/dev/null || true
    echo on > "/sys/bus/usb/devices/$device_path/power/control" 2>/dev/null || true
    
    # Reset autorizado
    echo 1 > "/sys/bus/usb/devices/$device_path/authorized" 2>/dev/null || true
    sleep 1
    echo 0 > "/sys/bus/usb/devices/$device_path/authorized" 2>/dev/null || true
    sleep 1
    echo 1 > "/sys/bus/usb/devices/$device_path/authorized" 2>/dev/null || true
    
    echo "✅ Soft reset completado"
}

# Buscar dispositivo
current_device=$(find_current_device)
if [[ -n "$current_device" ]]; then
    echo "📍 Dispositivo encontrado en: $current_device"
    current_port=$(echo "$current_device" | cut -d'-' -f1-2)
    
    if [[ "$current_port" != "$PUERTO_PREFERIDO" ]]; then
        echo "⚠️ Dispositivo no está en puerto preferido ($PUERTO_PREFERIDO)"
        echo "🔄 Intentando reubicación..."
        soft_reset_device "$current_device"
    else
        echo "✅ Dispositivo ya está en puerto preferido"
    fi
else
    echo "❌ Dispositivo SecuGen no encontrado"
fi
EOF

chmod +x /usr/local/bin/secugen_relocate.sh

# 3. Actualizar puerto preferido en el script
sed -i "s/PUERTO_PREFERIDO=.*/PUERTO_PREFERIDO=\"$PUERTO_DESEADO\"/" /usr/local/bin/secugen_relocate.sh

# 4. Aplicar reglas udev
echo "🔄 Aplicando reglas udev..."
udevadm control --reload-rules
udevadm trigger

# 5. Configurar para prevenir autosuspend
echo "⚙️ Configurando parámetros USB..."
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", TEST=="power/control", ATTR{power/control}="on"' >> /etc/udev/rules.d/99-secugen-puerto-fijo.rules

# 6. Crear alias para facilitar uso
echo "📝 Creando alias de comando..."
cat > /usr/local/bin/secugen-port << 'EOF'
#!/bin/bash
case "$1" in
    "status")
        echo "=== Estado del Dispositivo SecuGen ==="
        if lsusb | grep -q "1162:2201"; then
            echo "✅ Dispositivo: CONECTADO"
            lsusb | grep "1162:2201"
            
            # Mostrar puerto actual
            for device in /sys/bus/usb/devices/*; do
                if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
                    vendor=$(cat "$device/idVendor" 2>/dev/null)
                    product=$(cat "$device/idProduct" 2>/dev/null)
                    
                    if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                        device_name=$(basename "$device")
                        busnum=$(cat "$device/busnum" 2>/dev/null)
                        devnum=$(cat "$device/devnum" 2>/dev/null)
                        
                        echo "📍 Puerto: $device_name (Bus: $busnum, Device: $devnum)"
                        echo "📍 Ruta: /dev/bus/usb/$(printf "%03d" $busnum)/$(printf "%03d" $devnum)"
                        
                        # Verificar permisos
                        device_file="/dev/bus/usb/$(printf "%03d" $busnum)/$(printf "%03d" $devnum)"
                        if [[ -e "$device_file" ]]; then
                            perms=$(ls -l "$device_file" | cut -d' ' -f1)
                            echo "📋 Permisos: $perms"
                        fi
                        break
                    fi
                fi
            done
        else
            echo "❌ Dispositivo: NO CONECTADO"
        fi
        ;;
    "relocate")
        echo "🔄 Reubicando dispositivo..."
        /usr/local/bin/secugen_relocate.sh
        ;;
    "fix")
        echo "🔧 Aplicando configuración completa..."
        udevadm control --reload-rules
        udevadm trigger
        /usr/local/bin/secugen_relocate.sh
        ;;
    *)
        echo "Uso: secugen-port {status|relocate|fix}"
        echo ""
        echo "  status    - Mostrar estado del dispositivo"
        echo "  relocate  - Intentar reubicar al puerto preferido"
        echo "  fix       - Aplicar configuración completa"
        ;;
esac
EOF

chmod +x /usr/local/bin/secugen-port

# 7. Verificar configuración actual
echo ""
echo "✅ Configuración completada!"
echo ""
echo "📋 Comandos disponibles:"
echo "   secugen-port status    - Ver estado del dispositivo"
echo "   secugen-port relocate  - Reubicar al puerto preferido"
echo "   secugen-port fix       - Aplicar configuración completa"
echo ""

# Mostrar estado actual
echo "📊 Estado actual:"
/usr/local/bin/secugen-port status

echo ""
echo "🎯 Puerto configurado: $PUERTO_DESEADO"
echo "💡 Para cambiar puerto: sudo $0 nuevo_puerto"
echo "💡 Ejemplo: sudo $0 1-2"
echo ""
echo "📝 Archivos creados:"
echo "   /etc/udev/rules.d/99-secugen-puerto-fijo.rules"
echo "   /usr/local/bin/secugen_relocate.sh"
echo "   /usr/local/bin/secugen-port" 