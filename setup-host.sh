#!/bin/bash
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARN: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Verificar permisos de root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Este script debe ejecutarse con permisos de root (sudo)"
        exit 1
    fi
}

# Instalar reglas udev en el host
setup_udev_rules() {
    log "Configurando reglas udev para dispositivos SecuGen..."
    
    if [ -f "docker/99SecuGen.rules" ]; then
        cp docker/99SecuGen.rules /etc/udev/rules.d/
        chmod 644 /etc/udev/rules.d/99SecuGen.rules
        chown root:root /etc/udev/rules.d/99SecuGen.rules
        log "Reglas udev copiadas exitosamente"
    else
        error "No se encontró el archivo docker/99SecuGen.rules"
        exit 1
    fi
    
    # Recargar reglas udev
    log "Recargando reglas udev..."
    udevadm control --reload-rules
    udevadm trigger
    log "Reglas udev recargadas"
}

# Configurar permisos del dispositivo SecuGen
setup_device_permissions() {
    log "Buscando y configurando dispositivo SecuGen..."
    
    # Buscar dispositivo SecuGen
    found_device=false
    for device_path in /sys/bus/usb/devices/*; do
        if [ -f "$device_path/idVendor" ] && [ -f "$device_path/idProduct" ]; then
            vendor=$(cat "$device_path/idVendor")
            product=$(cat "$device_path/idProduct")
            
            if [ "$vendor" = "1162" ] && [ "$product" = "2201" ]; then
                busnum=$(cat "$device_path/busnum")
                devnum=$(cat "$device_path/devnum")
                device_file="/dev/bus/usb/$(printf "%03d" $busnum)/$(printf "%03d" $devnum)"
                
                log "Dispositivo SecuGen encontrado: $device_file"
                
                # Configurar permisos
                chmod 666 "$device_file"
                chown root:plugdev "$device_file"
                
                log "Permisos configurados para el dispositivo SecuGen"
                found_device=true
                break
            fi
        fi
    done
    
    if [ "$found_device" = false ]; then
        warn "No se encontró dispositivo SecuGen conectado. Conéctalo y ejecuta este script nuevamente."
    fi
}

# Verificar Docker
check_docker() {
    log "Verificando Docker..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado"
        exit 1
    fi
    
    if ! systemctl is-active --quiet docker; then
        log "Iniciando servicio Docker..."
        systemctl start docker
    fi
    
    log "Docker está funcionando correctamente"
}

# Verificar docker-compose
check_docker_compose() {
    log "Verificando Docker Compose..."
    
    # Verificar si existe la versión moderna
    if [ -f "/usr/local/bin/docker-compose" ]; then
        log "Docker Compose v2 encontrado en /usr/local/bin/docker-compose"
        return
    fi
    
    # Verificar versión del sistema
    if command -v docker-compose &> /dev/null; then
        version=$(docker-compose --version | grep -o '[0-9]\+\.[0-9]\+' | head -1)
        if [ "$(echo "$version" | cut -d. -f1)" -lt 2 ]; then
            warn "Docker Compose v1 detectado. Instalando v2..."
            install_docker_compose_v2
        else
            log "Docker Compose v2 encontrado"
        fi
    else
        warn "Docker Compose no encontrado. Instalando..."
        install_docker_compose_v2
    fi
}

# Instalar Docker Compose v2
install_docker_compose_v2() {
    log "Instalando Docker Compose v2..."
    
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    log "Docker Compose v2 instalado exitosamente"
}

# Crear script de inicio completo
create_startup_script() {
    log "Creando script de inicio completo..."
    
    cat > run-secugen-api.sh << 'EOF'
#!/bin/bash
set -e

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Verificar si somos root
if [ "$EUID" -ne 0 ]; then
    error "Este script debe ejecutarse con sudo"
    exit 1
fi

log "Configurando permisos del dispositivo SecuGen..."

# Configurar permisos del dispositivo SecuGen
for device_path in /sys/bus/usb/devices/*; do
    if [ -f "$device_path/idVendor" ] && [ -f "$device_path/idProduct" ]; then
        vendor=$(cat "$device_path/idVendor")
        product=$(cat "$device_path/idProduct")
        
        if [ "$vendor" = "1162" ] && [ "$product" = "2201" ]; then
            busnum=$(cat "$device_path/busnum")
            devnum=$(cat "$device_path/devnum")
            device_file="/dev/bus/usb/$(printf "%03d" $busnum)/$(printf "%03d" $devnum)"
            
            log "Dispositivo SecuGen encontrado: $device_file"
            chmod 666 "$device_file"
            chown root:plugdev "$device_file"
            log "Permisos configurados"
            break
        fi
    fi
done

# Determinar qué docker-compose usar
if [ -f "/usr/local/bin/docker-compose" ]; then
    DOCKER_COMPOSE="/usr/local/bin/docker-compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

log "Iniciando aplicación SecuGen API..."
$DOCKER_COMPOSE up --build -d

log "Aplicación iniciada exitosamente!"
log "API disponible en: http://localhost:5000"
log ""
log "Para ver los logs: sudo docker logs -f secugen_api_sdk-api-1"
log "Para parar: sudo $DOCKER_COMPOSE down"
EOF

    chmod +x run-secugen-api.sh
    log "Script 'run-secugen-api.sh' creado exitosamente"
}

# Función principal
main() {
    log "=== Configuración del Host para SecuGen API SDK ==="
    
    check_root
    check_docker
    check_docker_compose
    setup_udev_rules
    setup_device_permissions
    create_startup_script
    
    log "=== Configuración completada exitosamente ==="
    log ""
    log "Para iniciar la aplicación, ejecuta:"
    log "  sudo ./run-secugen-api.sh"
    log ""
    log "O si prefieres hacerlo manualmente:"
    log "  sudo /usr/local/bin/docker-compose up --build -d"
}

main "$@" 