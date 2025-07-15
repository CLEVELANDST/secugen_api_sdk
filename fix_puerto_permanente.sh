#!/bin/bash

# Script para fijar el dispositivo SecuGen en un puerto USB específico
# Uso: ./fix_puerto_permanente.sh [puerto_preferido]

set -e

# Configuración
VENDOR_ID="1162"
PRODUCT_ID="2201"
DEVICE_NAME="SecuGen_UPx"
PUERTO_PREFERIDO=${1:-"2-1"}  # Puerto USB preferido (ej: 2-1, 1-2, etc.)

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Función para verificar si el script se ejecuta como root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Este script debe ejecutarse como root"
        echo "Uso: sudo $0 [puerto_preferido]"
        exit 1
    fi
}

# Función para encontrar el dispositivo SecuGen
find_secugen_device() {
    log "🔍 Buscando dispositivo SecuGen..."
    
    # Buscar por lsusb
    if lsusb | grep -q "${VENDOR_ID}:${PRODUCT_ID}"; then
        log "✅ Dispositivo SecuGen encontrado en lsusb"
        lsusb | grep "${VENDOR_ID}:${PRODUCT_ID}"
        return 0
    else
        warning "❌ Dispositivo SecuGen no encontrado en lsusb"
        return 1
    fi
}

# Función para obtener información del puerto actual
get_current_port() {
    log "📍 Obteniendo información del puerto actual..."
    
    for device in /sys/bus/usb/devices/*; do
        if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
            vendor=$(cat "$device/idVendor" 2>/dev/null)
            product=$(cat "$device/idProduct" 2>/dev/null)
            
            if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                device_name=$(basename "$device")
                busnum=$(cat "$device/busnum" 2>/dev/null)
                devnum=$(cat "$device/devnum" 2>/dev/null)
                
                info "📍 Puerto actual: $device_name (Bus: $busnum, Device: $devnum)"
                echo "$device_name"
                return 0
            fi
        fi
    done
    
    warning "❌ No se pudo determinar el puerto actual"
    return 1
}

# Función para crear reglas udev mejoradas
create_advanced_udev_rules() {
    log "📝 Creando reglas udev avanzadas..."
    
    cat > /etc/udev/rules.d/99-secugen-puerto-fijo.rules << 'EOF'
# Reglas udev para fijar dispositivo SecuGen en puerto específico
# Dispositivo SecuGen UPx (1162:2201)

# Regla principal: Crear symlink persistente
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device"

# Regla para dispositivos USB específicos
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Regla para dispositivos HID (si aplica)
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1162", ATTRS{idProduct}=="2201", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Regla para dispositivos de entrada (input)
SUBSYSTEM=="input", ATTRS{idVendor}=="1162", ATTRS{idProduct}=="2201", MODE="0666", GROUP="plugdev", TAG+="uaccess"

# Regla para asignación de puerto específico (ejecutar script de reubicación)
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", ACTION=="add", RUN+="/usr/local/bin/secugen_port_manager.sh %k"

# Regla para prevenir auto-suspend
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", ATTR{power/autosuspend}="-1"

# Regla para dispositivos por ttyUSB (si aplica)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1162", ATTRS{idProduct}=="2201", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_tty"
EOF

    log "✅ Reglas udev avanzadas creadas"
}

# Función para crear script de gestión de puertos
create_port_manager_script() {
    log "🔧 Creando script de gestión de puertos..."
    
    cat > /usr/local/bin/secugen_port_manager.sh << 'EOF'
#!/bin/bash
# Script automático para gestionar puertos USB del dispositivo SecuGen
# Llamado automáticamente por udev

DEVICE_PATH=$1
VENDOR_ID="1162"
PRODUCT_ID="2201"
PUERTO_PREFERIDO="2-1"  # Puerto USB preferido
LOGFILE="/var/log/secugen_port_manager.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOGFILE"
}

log_message "SecuGen device detected: $DEVICE_PATH"

# Obtener información del dispositivo
if [[ -f "/sys/bus/usb/devices/$DEVICE_PATH/idVendor" ]]; then
    vendor=$(cat "/sys/bus/usb/devices/$DEVICE_PATH/idVendor")
    product=$(cat "/sys/bus/usb/devices/$DEVICE_PATH/idProduct")
    
    if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
        current_port=$(echo "$DEVICE_PATH" | cut -d'-' -f1-2)
        log_message "Current port: $current_port, Preferred: $PUERTO_PREFERIDO"
        
        if [[ "$current_port" != "$PUERTO_PREFERIDO" ]]; then
            log_message "Device not on preferred port, attempting relocation..."
            
            # Crear symlink específico para el puerto preferido
            ln -sf "/dev/bus/usb/$current_port" "/dev/secugen_preferred_port" 2>/dev/null || true
            
            # Deshabilitar autosuspend
            echo -1 > "/sys/bus/usb/devices/$DEVICE_PATH/power/autosuspend" 2>/dev/null || true
            echo on > "/sys/bus/usb/devices/$DEVICE_PATH/power/control" 2>/dev/null || true
            
            log_message "Port management completed"
        else
            log_message "Device already on preferred port"
        fi
    fi
fi
EOF

    chmod +x /usr/local/bin/secugen_port_manager.sh
    log "✅ Script de gestión de puertos creado"
}

# Función para configurar parámetros del kernel
configure_kernel_parameters() {
    log "⚙️ Configurando parámetros del kernel..."
    
    # Crear configuración para módulos USB
    cat > /etc/modprobe.d/secugen-usb.conf << 'EOF'
# Configuración para dispositivo SecuGen
# Deshabilitar autosuspend para dispositivos SecuGen
options usbcore autosuspend=-1

# Configuración específica para el hub USB
options ehci-hcd park=0
options ohci-hcd park=0
options uhci-hcd park=0
options xhci-hcd park=0
EOF

    # Parámetros del kernel para USB
    cat > /etc/sysctl.d/99-secugen-usb.conf << 'EOF'
# Configuración USB para dispositivo SecuGen
# Aumentar timeouts USB
kernel.usb.timeout = 5000
kernel.usb.autosuspend = -1
EOF

    log "✅ Parámetros del kernel configurados"
}

# Función para crear script de bind/unbind para puerto específico
create_port_bind_script() {
    log "🔗 Creando script de bind/unbind de puertos..."
    
    cat > /usr/local/bin/secugen_bind_port.sh << 'EOF'
#!/bin/bash
# Script para hacer bind/unbind del dispositivo SecuGen a un puerto específico

VENDOR_ID="1162"
PRODUCT_ID="2201"
PUERTO_PREFERIDO="2-1"  # Puerto USB preferido

bind_to_preferred_port() {
    echo "Intentando bind al puerto preferido: $PUERTO_PREFERIDO"
    
    # Encontrar el controlador USB del puerto preferido
    USB_CONTROLLER=$(find /sys/bus/usb/devices -name "$PUERTO_PREFERIDO" -type d)
    
    if [[ -n "$USB_CONTROLLER" ]]; then
        echo "Controlador encontrado: $USB_CONTROLLER"
        
        # Obtener el driver del controlador
        DRIVER_PATH=$(readlink -f "$USB_CONTROLLER/driver")
        DRIVER_NAME=$(basename "$DRIVER_PATH")
        
        echo "Driver: $DRIVER_NAME"
        
        # Hacer rebind del puerto
        echo "$PUERTO_PREFERIDO" > "$DRIVER_PATH/unbind" 2>/dev/null || true
        sleep 1
        echo "$PUERTO_PREFERIDO" > "$DRIVER_PATH/bind" 2>/dev/null || true
        
        echo "Bind completado"
    else
        echo "No se encontró el controlador para el puerto $PUERTO_PREFERIDO"
    fi
}

unbind_from_current_port() {
    echo "Desvinculando dispositivo del puerto actual..."
    
    for device in /sys/bus/usb/devices/*; do
        if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
            vendor=$(cat "$device/idVendor" 2>/dev/null)
            product=$(cat "$device/idProduct" 2>/dev/null)
            
            if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                device_name=$(basename "$device")
                echo "Dispositivo encontrado en: $device_name"
                
                # Unbind del dispositivo actual
                if [[ -f "$device/driver/unbind" ]]; then
                    echo "$device_name" > "$device/driver/unbind" 2>/dev/null || true
                    echo "Dispositivo desvinculado de $device_name"
                fi
                break
            fi
        fi
    done
}

case "$1" in
    "bind")
        bind_to_preferred_port
        ;;
    "unbind")
        unbind_from_current_port
        ;;
    "rebind")
        unbind_from_current_port
        sleep 2
        bind_to_preferred_port
        ;;
    *)
        echo "Uso: $0 {bind|unbind|rebind}"
        exit 1
        ;;
esac
EOF

    chmod +x /usr/local/bin/secugen_bind_port.sh
    log "✅ Script de bind/unbind creado"
}

# Función para crear servicio systemd de monitoreo
create_monitoring_service() {
    log "🔍 Creando servicio de monitoreo..."
    
    cat > /etc/systemd/system/secugen-port-monitor.service << 'EOF'
[Unit]
Description=SecuGen Port Monitor Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/secugen_port_monitor.sh
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF

    cat > /usr/local/bin/secugen_port_monitor.sh << 'EOF'
#!/bin/bash
# Servicio de monitoreo para el puerto del dispositivo SecuGen

VENDOR_ID="1162"
PRODUCT_ID="2201"
PUERTO_PREFERIDO="2-1"
LOGFILE="/var/log/secugen_port_monitor.log"
CHECK_INTERVAL=30  # Verificar cada 30 segundos

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOGFILE"
}

check_device_port() {
    for device in /sys/bus/usb/devices/*; do
        if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
            vendor=$(cat "$device/idVendor" 2>/dev/null)
            product=$(cat "$device/idProduct" 2>/dev/null)
            
            if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                device_name=$(basename "$device")
                current_port=$(echo "$device_name" | cut -d'-' -f1-2)
                
                if [[ "$current_port" != "$PUERTO_PREFERIDO" ]]; then
                    log_message "Device on wrong port: $current_port (expected: $PUERTO_PREFERIDO)"
                    return 1
                else
                    log_message "Device on correct port: $current_port"
                    return 0
                fi
            fi
        fi
    done
    
    log_message "Device not found"
    return 1
}

log_message "SecuGen port monitor started"

while true; do
    if ! check_device_port; then
        log_message "Attempting to relocate device to preferred port..."
        /usr/local/bin/secugen_bind_port.sh rebind
    fi
    
    sleep $CHECK_INTERVAL
done
EOF

    chmod +x /usr/local/bin/secugen_port_monitor.sh
    
    systemctl daemon-reload
    systemctl enable secugen-port-monitor.service
    
    log "✅ Servicio de monitoreo creado y habilitado"
}

# Función para aplicar configuración
apply_configuration() {
    log "🔄 Aplicando configuración..."
    
    # Recargar reglas udev
    udevadm control --reload-rules
    udevadm trigger
    
    # Aplicar configuración del kernel
    sysctl -p /etc/sysctl.d/99-secugen-usb.conf 2>/dev/null || true
    
    # Reiniciar servicios USB si es necesario
    modprobe -r usbcore 2>/dev/null || true
    modprobe usbcore 2>/dev/null || true
    
    log "✅ Configuración aplicada"
}

# Función para verificar configuración
verify_configuration() {
    log "✅ Verificando configuración..."
    
    # Verificar reglas udev
    if [[ -f "/etc/udev/rules.d/99-secugen-puerto-fijo.rules" ]]; then
        info "✅ Reglas udev instaladas"
    else
        warning "❌ Reglas udev no encontradas"
    fi
    
    # Verificar scripts
    if [[ -f "/usr/local/bin/secugen_port_manager.sh" ]]; then
        info "✅ Script de gestión de puertos instalado"
    else
        warning "❌ Script de gestión no encontrado"
    fi
    
    # Verificar servicio
    if systemctl is-enabled secugen-port-monitor.service >/dev/null 2>&1; then
        info "✅ Servicio de monitoreo habilitado"
    else
        warning "❌ Servicio de monitoreo no habilitado"
    fi
    
    # Verificar dispositivo
    if find_secugen_device >/dev/null 2>&1; then
        info "✅ Dispositivo SecuGen detectado"
        current_port=$(get_current_port)
        info "📍 Puerto actual: $current_port"
        info "📍 Puerto preferido: $PUERTO_PREFERIDO"
        
        if [[ "$current_port" == "$PUERTO_PREFERIDO"* ]]; then
            info "✅ Dispositivo en puerto preferido"
        else
            warning "⚠️ Dispositivo no está en puerto preferido"
        fi
    else
        warning "❌ Dispositivo SecuGen no detectado"
    fi
}

# Función para crear script de uso
create_usage_script() {
    log "📖 Creando script de uso..."
    
    cat > /usr/local/bin/secugen_port_control.sh << 'EOF'
#!/bin/bash
# Script de control para el puerto del dispositivo SecuGen

show_help() {
    echo "Uso: secugen_port_control.sh [COMANDO]"
    echo ""
    echo "Comandos disponibles:"
    echo "  status      - Mostrar estado del dispositivo y puerto"
    echo "  bind        - Forzar bind al puerto preferido"
    echo "  unbind      - Desvincular del puerto actual"
    echo "  rebind      - Desvincular y volver a vincular"
    echo "  monitor     - Iniciar monitoreo del puerto"
    echo "  set-port    - Establecer puerto preferido"
    echo "  help        - Mostrar esta ayuda"
}

show_status() {
    echo "=== Estado del Dispositivo SecuGen ==="
    
    # Verificar si el dispositivo está presente
    if lsusb | grep -q "1162:2201"; then
        echo "✅ Dispositivo: CONECTADO"
        lsusb | grep "1162:2201"
    else
        echo "❌ Dispositivo: NO CONECTADO"
        return 1
    fi
    
    # Mostrar puerto actual
    for device in /sys/bus/usb/devices/*; do
        if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
            vendor=$(cat "$device/idVendor" 2>/dev/null)
            product=$(cat "$device/idProduct" 2>/dev/null)
            
            if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                device_name=$(basename "$device")
                busnum=$(cat "$device/busnum" 2>/dev/null)
                devnum=$(cat "$device/devnum" 2>/dev/null)
                
                echo "📍 Puerto actual: $device_name (Bus: $busnum, Device: $devnum)"
                echo "📍 Puerto preferido: 2-1"
                
                if [[ "$device_name" == "2-1"* ]]; then
                    echo "✅ Estado: EN PUERTO PREFERIDO"
                else
                    echo "⚠️ Estado: NO EN PUERTO PREFERIDO"
                fi
                break
            fi
        fi
    done
    
    # Mostrar estado del servicio
    if systemctl is-active secugen-port-monitor.service >/dev/null 2>&1; then
        echo "✅ Servicio de monitoreo: ACTIVO"
    else
        echo "❌ Servicio de monitoreo: INACTIVO"
    fi
}

case "$1" in
    "status")
        show_status
        ;;
    "bind")
        /usr/local/bin/secugen_bind_port.sh bind
        ;;
    "unbind")
        /usr/local/bin/secugen_bind_port.sh unbind
        ;;
    "rebind")
        /usr/local/bin/secugen_bind_port.sh rebind
        ;;
    "monitor")
        echo "Iniciando monitoreo del puerto..."
        systemctl start secugen-port-monitor.service
        ;;
    "set-port")
        if [[ -n "$2" ]]; then
            sed -i "s/PUERTO_PREFERIDO=.*/PUERTO_PREFERIDO=\"$2\"/" /usr/local/bin/secugen_port_manager.sh
            sed -i "s/PUERTO_PREFERIDO=.*/PUERTO_PREFERIDO=\"$2\"/" /usr/local/bin/secugen_bind_port.sh
            sed -i "s/PUERTO_PREFERIDO=.*/PUERTO_PREFERIDO=\"$2\"/" /usr/local/bin/secugen_port_monitor.sh
            echo "Puerto preferido establecido a: $2"
        else
            echo "Error: Especifique el puerto (ej: 2-1)"
        fi
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "Comando no reconocido: $1"
        show_help
        exit 1
        ;;
esac
EOF

    chmod +x /usr/local/bin/secugen_port_control.sh
    log "✅ Script de control creado"
}

# Función principal
main() {
    log "🚀 Iniciando configuración de puerto fijo para dispositivo SecuGen..."
    
    check_root
    
    info "Puerto preferido configurado: $PUERTO_PREFERIDO"
    
    # Verificar si el dispositivo está presente
    if ! find_secugen_device; then
        warning "Dispositivo no encontrado, pero continuando con la configuración..."
    fi
    
    # Crear todas las configuraciones
    create_advanced_udev_rules
    create_port_manager_script
    configure_kernel_parameters
    create_port_bind_script
    create_monitoring_service
    create_usage_script
    
    # Aplicar configuración
    apply_configuration
    
    # Iniciar servicio de monitoreo
    systemctl start secugen-port-monitor.service
    
    # Verificar configuración
    verify_configuration
    
    log "✅ Configuración completada exitosamente!"
    
    echo ""
    echo "=== COMANDOS DISPONIBLES ==="
    echo "secugen_port_control.sh status    - Ver estado del dispositivo"
    echo "secugen_port_control.sh bind      - Forzar bind al puerto preferido"
    echo "secugen_port_control.sh rebind    - Reconfigurar puerto"
    echo "secugen_port_control.sh set-port [puerto] - Cambiar puerto preferido"
    echo ""
    echo "Para cambiar el puerto preferido:"
    echo "secugen_port_control.sh set-port 1-2  # Por ejemplo"
    echo ""
    echo "El servicio de monitoreo está activo y verificará el puerto cada 30 segundos."
}

# Ejecutar función principal
main "$@" 