#!/bin/bash
set -e  # Salir en caso de error

# Función para log
log() {
    echo "[$(date -u)] $1"
}

# Verificar permisos y dispositivos
check_requirements() {
    log "Verificando requisitos del sistema..."
    
    # Buscar dispositivo SecuGen específicamente
    for device in /sys/bus/usb/devices/*; do
        if [ -f "$device/idVendor" ] && [ -f "$device/idProduct" ]; then
            vendor=$(cat "$device/idVendor")
            product=$(cat "$device/idProduct")
            if [ "$vendor" = "1162" ] && [ "$product" = "2201" ]; then
                busnum=$(cat "$device/busnum")
                devnum=$(cat "$device/devnum")
                log "Dispositivo SecuGen encontrado en bus $busnum dispositivo $devnum"
                chmod 666 "/dev/bus/usb/$busnum/$devnum" || true
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
