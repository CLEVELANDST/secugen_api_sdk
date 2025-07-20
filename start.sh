#!/bin/bash
set -e  # Salir en caso de error

# Función para log
log() {
    echo "[$(date -u)] $1"
}

# Verificar permisos y dispositivos
check_requirements() {
    log "Verificando requisitos del sistema..."
    
    # Configurar permisos para operaciones USB reset
    log "Configurando permisos para reset USB..."
    chmod 666 /sys/bus/usb/drivers/usb/unbind 2>/dev/null || true
    chmod 666 /sys/bus/usb/drivers/usb/bind 2>/dev/null || true
    
    # Buscar dispositivo SecuGen específicamente
    for device in /sys/bus/usb/devices/*; do
        if [ -f "$device/idVendor" ] && [ -f "$device/idProduct" ]; then
            vendor=$(cat "$device/idVendor")
            product=$(cat "$device/idProduct")
            if [ "$vendor" = "1162" ]; then
                busnum=$(cat "$device/busnum")
                devnum=$(cat "$device/devnum")
                log "Dispositivo SecuGen encontrado en bus $busnum dispositivo $devnum (Vendor: $vendor, Product: $product)"
                chmod 666 "/dev/bus/usb/$busnum/$devnum" 2>/dev/null || true
                break
            fi
        fi
    done
    
    # Verificar reglas udev
    if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
        log "Aplicando reglas udev..."
        udevadm control --reload-rules || true
        udevadm trigger || true
    fi
    
    # Verificar que tenemos permisos de root
    if [ "$(id -u)" = "0" ]; then
        log "Ejecutando como root - permisos de reset USB disponibles"
    else
        log "ADVERTENCIA: No ejecutando como root - endpoint /reset-usb puede fallar"
    fi
}

# Iniciar la aplicación
start_application() {
    log "Iniciando aplicación Flask..."
    exec python3 app.py
}

# Ejecución principal
main() {
    log "Iniciando servicios..."
    check_requirements
    start_application
}

main
