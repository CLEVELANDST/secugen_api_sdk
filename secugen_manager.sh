#!/bin/bash

# =============================================================================
# SECUGEN MANAGER - Script Maestro para Sistema de Huellas Digitales
# =============================================================================
# Este script unifica todas las funcionalidades necesarias para:
# - Instalar y configurar el sistema
# - Gestionar la aplicación (iniciar, parar, reiniciar)
# - Verificar estado y realizar diagnósticos
# - Hacer respaldos y monitoreo
# =============================================================================

set -e

# Configuración
APP_NAME="secugen-fingerprint-api"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_PORT="5000"
LOG_DIR="$APP_DIR/logs"
PYTHON_ENV="$APP_DIR/venv"
PID_FILE="$APP_DIR/app.pid"
CONFIG_FILE="$APP_DIR/config/production.env"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Contadores para verificaciones
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# =============================================================================
# FUNCIONES DE LOGGING
# =============================================================================

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
    ((CHECKS_PASSED++))
}

log_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
    ((CHECKS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[⚠️  WARN]${NC} $1"
    ((CHECKS_WARNING++))
}

# =============================================================================
# FUNCIONES DE VERIFICACIÓN
# =============================================================================

check_root_needed() {
    if [[ $1 == "install" || $1 == "setup" ]] && [[ $EUID -ne 0 ]]; then
        error "Este comando requiere permisos de root (sudo)"
        exit 1
    fi
}

check_device() {
    local vendor_id="1162"
    local product_id="2201"
    
    info "Verificando dispositivo SecuGen..."
    
    if lsusb | grep -q "ID ${vendor_id}:${product_id}"; then
        log_success "Dispositivo SecuGen encontrado"
        return 0
    else
        log_error "Dispositivo SecuGen no encontrado"
        return 1
    fi
}

check_system_requirements() {
    info "Verificando requisitos del sistema..."
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python 3 instalado: $PYTHON_VERSION"
    else
        log_error "Python 3 no está instalado"
    fi
    
    # Verificar pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 disponible"
    else
        log_error "pip3 no está instalado"
    fi
    
    # Verificar archivos principales
    local required_files=("app.py" "sdk/__init__.py" "lib/linux3/libpysgfplib.so")
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "Archivo requerido encontrado: $file"
        else
            log_error "Archivo requerido no encontrado: $file"
        fi
    done
    
    # Verificar puerto
    if netstat -tuln 2>/dev/null | grep ":$SERVICE_PORT " > /dev/null; then
        log_warning "Puerto $SERVICE_PORT está en uso"
    else
        log_success "Puerto $SERVICE_PORT está libre"
    fi
}

check_usb_permissions() {
    info "Verificando permisos USB..."
    
    # Verificar reglas udev
    if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
        log_success "Reglas udev configuradas"
    else
        log_warning "Reglas udev no configuradas"
    fi
    
    # Verificar grupo plugdev
    if groups | grep -q plugdev; then
        log_success "Usuario está en grupo plugdev"
    else
        log_warning "Usuario no está en grupo plugdev"
    fi
}

# =============================================================================
# FUNCIONES DE INSTALACIÓN Y CONFIGURACIÓN
# =============================================================================

install_system_dependencies() {
    log "Instalando dependencias del sistema..."
    
    apt-get update -y
    apt-get install -y \
        python3-venv \
        python3-dev \
        python3-pip \
        libusb-dev \
        libusb-0.1-4 \
        libusb-1.0-0 \
        libusb-1.0-0-dev \
        udev \
        systemd \
        curl \
        git \
        build-essential \
        pkg-config \
        net-tools
    
    log "✅ Dependencias del sistema instaladas"
}

setup_python_environment() {
    log "Configurando entorno Python..."
    
    # Crear entorno virtual si no existe
    if [ ! -d "$PYTHON_ENV" ]; then
        python3 -m venv "$PYTHON_ENV"
        log "✅ Entorno virtual creado"
    fi
    
    # Activar entorno virtual
    source "$PYTHON_ENV/bin/activate"
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias básicas
    pip install flask werkzeug flask-cors python-dotenv pyusb requests
    
    log "✅ Entorno Python configurado"
}

setup_usb_permissions() {
    log "Configurando permisos USB..."
    
    # Crear reglas udev
    cat > /etc/udev/rules.d/99SecuGen.rules << 'EOF'
# Reglas udev para dispositivos SecuGen
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", MODE="0666", GROUP="plugdev", TAG+="uaccess", SYMLINK+="secugen_device"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", SUBSYSTEM=="usb_device", MODE="0666", GROUP="plugdev"

# Reglas adicionales para otros modelos SecuGen
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="0300", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb", ATTR{idProduct}=="0200", ATTR{idVendor}=="1162", MODE="0666", GROUP="plugdev", TAG+="uaccess"
SUBSYSTEM=="usb", ATTR{idProduct}=="1000", ATTR{idVendor}=="1162", MODE="0666", GROUP="plugdev"
EOF
    
    chmod 644 /etc/udev/rules.d/99SecuGen.rules
    chown root:root /etc/udev/rules.d/99SecuGen.rules
    
    # Recargar reglas udev
    udevadm control --reload-rules
    udevadm trigger
    
    # Agregar usuario al grupo plugdev
    if [ -n "$SUDO_USER" ]; then
        usermod -a -G plugdev "$SUDO_USER"
    fi
    
    log "✅ Permisos USB configurados"
}

configure_device_permissions() {
    log "Configurando permisos del dispositivo SecuGen..."
    
    # Buscar y configurar dispositivo SecuGen
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
                chown root:plugdev "$device_file" 2>/dev/null || true
                log "Permisos configurados para el dispositivo"
                return 0
            fi
        fi
    done
    
    warning "No se encontró dispositivo SecuGen conectado"
    return 1
}

create_directories() {
    log "Creando directorios necesarios..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$APP_DIR/config"
    mkdir -p "$APP_DIR/backups"
    
    log "✅ Directorios creados"
}

create_config_file() {
    log "Creando archivo de configuración..."
    
    cat > "$CONFIG_FILE" << EOF
# Configuración de Producción
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=$SERVICE_PORT
LOG_LEVEL=INFO
LOG_FILE=$LOG_DIR/app.log
LD_LIBRARY_PATH=$APP_DIR/lib/linux3
PYTHONPATH=$APP_DIR
EOF
    
    log "✅ Archivo de configuración creado"
}

# =============================================================================
# FUNCIONES DE GESTIÓN DE LA APLICACIÓN
# =============================================================================

start_application() {
    log "Iniciando aplicación..."
    
    # Verificar que no esté corriendo
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            warning "La aplicación ya está corriendo con PID: $PID"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    # Configurar permisos del dispositivo
    configure_device_permissions || warning "Dispositivo no encontrado, continuando..."
    
    # Activar entorno virtual
    source "$PYTHON_ENV/bin/activate"
    
    # Cargar configuración si existe
    [ -f "$CONFIG_FILE" ] && source "$CONFIG_FILE"
    
    # Configurar variables de entorno
    export LD_LIBRARY_PATH="$APP_DIR/lib/linux3:$LD_LIBRARY_PATH"
    export PYTHONPATH="$APP_DIR:$PYTHONPATH"
    
    # Cambiar al directorio de la aplicación
    cd "$APP_DIR"
    
    # Iniciar aplicación en segundo plano
    nohup python3 app.py > "$LOG_DIR/app.log" 2>&1 &
    
    # Guardar PID
    APP_PID=$!
    echo $APP_PID > "$PID_FILE"
    
    log "Aplicación iniciada con PID: $APP_PID"
    
    # Verificar que esté funcionando
    sleep 3
    if ps -p $APP_PID > /dev/null; then
        log "✅ Aplicación iniciada exitosamente"
        
        # Probar endpoint
        sleep 2
        if curl -f http://localhost:$SERVICE_PORT/initialize > /dev/null 2>&1; then
            log "✅ API respondiendo correctamente"
        else
            warning "API no responde inmediatamente"
        fi
    else
        error "Error: La aplicación no se inició correctamente"
        return 1
    fi
}

stop_application() {
    log "Deteniendo aplicación..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        
        if ps -p $PID > /dev/null 2>&1; then
            log "Terminando proceso con PID: $PID"
            
            # Intentar terminar graciosamente
            kill -TERM $PID
            
            # Esperar hasta 10 segundos
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    log "✅ Proceso terminado graciosamente"
                    break
                fi
                sleep 1
            done
            
            # Si aún está corriendo, forzar terminación
            if ps -p $PID > /dev/null 2>&1; then
                log "Forzando terminación del proceso..."
                kill -KILL $PID
                sleep 2
                if ps -p $PID > /dev/null 2>&1; then
                    error "No se pudo terminar el proceso"
                    return 1
                else
                    log "✅ Proceso terminado forzosamente"
                fi
            fi
        else
            warning "Proceso no estaba corriendo"
        fi
        
        rm -f "$PID_FILE"
    else
        warning "Archivo PID no encontrado"
        
        # Buscar procesos por nombre
        PIDS=$(pgrep -f "python3 app.py" || true)
        if [ -n "$PIDS" ]; then
            log "Terminando procesos Python relacionados..."
            kill -TERM $PIDS
            sleep 2
            # Verificar si terminaron
            REMAINING=$(pgrep -f "python3 app.py" || true)
            if [ -n "$REMAINING" ]; then
                kill -KILL $REMAINING
            fi
            log "✅ Procesos terminados"
        else
            warning "No se encontraron procesos de la aplicación"
        fi
    fi
    
    log "Aplicación detenida"
}

restart_application() {
    log "Reiniciando aplicación..."
    stop_application
    sleep 3
    start_application
    log "Aplicación reiniciada"
}

status_application() {
    echo "=================================================="
    echo -e "${BOLD}🔍 ESTADO DEL SISTEMA DE HUELLAS DIGITALES${NC}"
    echo "=================================================="
    
    # Estado de la aplicación
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            log_success "Aplicación corriendo con PID: $PID"
            ps -p $PID -o pid,ppid,cmd,etime,pcpu,pmem
            
            # Verificar puerto
            if netstat -tuln | grep ":$SERVICE_PORT " > /dev/null; then
                log_success "Puerto $SERVICE_PORT está escuchando"
            else
                log_warning "Puerto $SERVICE_PORT no está escuchando"
            fi
            
            # Probar API
            if curl -f http://localhost:$SERVICE_PORT/initialize > /dev/null 2>&1; then
                log_success "API respondiendo correctamente"
            else
                log_error "API no responde"
            fi
        else
            log_error "Proceso no encontrado (PID: $PID)"
            rm -f "$PID_FILE"
        fi
    else
        log_warning "Archivo PID no encontrado"
        PIDS=$(pgrep -f "python3 app.py" || true)
        if [ -n "$PIDS" ]; then
            log_warning "Procesos Python relacionados encontrados:"
            ps -p $PIDS -o pid,ppid,cmd,etime,pcpu,pmem
        else
            log_error "No se encontraron procesos de la aplicación"
        fi
    fi
    
    echo ""
    echo "🔌 Estado del Dispositivo USB:"
    if lsusb | grep -i secugen > /dev/null; then
        log_success "Dispositivo SecuGen detectado:"
        lsusb | grep -i secugen
    else
        log_error "Dispositivo SecuGen no detectado"
    fi
    
    echo ""
    echo "🔒 Permisos y Configuración:"
    if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
        log_success "Reglas udev configuradas"
    else
        log_error "Reglas udev no configuradas"
    fi
    
    if groups | grep -q plugdev; then
        log_success "Usuario en grupo plugdev"
    else
        log_error "Usuario no está en grupo plugdev"
    fi
    
    echo ""
    echo "📋 Logs Recientes:"
    if [ -f "$LOG_DIR/app.log" ]; then
        echo "Últimas 5 líneas del log:"
        tail -n 5 "$LOG_DIR/app.log"
    else
        log_warning "No se encontraron logs de la aplicación"
    fi
    
    echo "=================================================="
}

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

create_backup() {
    log "Creando backup..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$APP_DIR/backups/backup_$TIMESTAMP.tar.gz"
    
    mkdir -p "$APP_DIR/backups"
    
    tar -czf "$BACKUP_FILE" \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='logs/*.log' \
        --exclude='backups' \
        -C "$APP_DIR/.." \
        "$(basename "$APP_DIR")"
    
    log "Backup creado: $BACKUP_FILE"
    
    # Limpiar backups antiguos (mantener solo los últimos 5)
    cd "$APP_DIR/backups"
    ls -t backup_*.tar.gz | tail -n +6 | xargs -r rm -f
    
    log "✅ Backup completado"
}

show_help() {
    echo "=================================================="
    echo -e "${BOLD}🎮 SECUGEN MANAGER - COMANDOS DISPONIBLES${NC}"
    echo "=================================================="
    echo ""
    echo -e "${CYAN}📋 CONFIGURACIÓN INICIAL${NC}"
    echo "  sudo $0 install          # Instalar dependencias del sistema"
    echo "  sudo $0 setup            # Configurar sistema completo"
    echo "  $0 check                 # Verificar requisitos del sistema"
    echo ""
    echo -e "${CYAN}🚀 GESTIÓN DE LA APLICACIÓN${NC}"
    echo "  $0 start                 # Iniciar aplicación"
    echo "  $0 stop                  # Parar aplicación"
    echo "  $0 restart               # Reiniciar aplicación"
    echo "  $0 status                # Ver estado completo"
    echo ""
    echo -e "${CYAN}🔧 UTILIDADES${NC}"
    echo "  $0 backup                # Crear backup"
    echo "  $0 test                  # Probar API básica"
    echo "  $0 logs                  # Ver logs en tiempo real"
    echo "  $0 help                  # Mostrar esta ayuda"
    echo ""
    echo -e "${CYAN}📊 EJEMPLOS DE USO${NC}"
    echo "  # Configuración inicial completa:"
    echo "  sudo $0 setup"
    echo ""
    echo "  # Iniciar y verificar:"
    echo "  $0 start && $0 status"
    echo ""
    echo "  # Hacer backup y reiniciar:"
    echo "  $0 backup && $0 restart"
    echo ""
    echo "=================================================="
}

test_api() {
    log "Probando API..."
    
    # Verificar que esté corriendo
    if ! curl -f http://localhost:$SERVICE_PORT/initialize > /dev/null 2>&1; then
        error "API no responde. ¿Está la aplicación corriendo?"
        return 1
    fi
    
    # Probar inicialización
    echo "Probando inicialización del dispositivo..."
    INIT_RESULT=$(curl -s -X POST -H "Content-Type: application/json" http://localhost:$SERVICE_PORT/initialize)
    echo "Resultado: $INIT_RESULT"
    
    # Probar LED
    echo "Probando control de LED..."
    LED_RESULT=$(curl -s -X POST -H "Content-Type: application/json" -d '{"state":true}' http://localhost:$SERVICE_PORT/led)
    echo "Resultado: $LED_RESULT"
    
    sleep 2
    
    # Apagar LED
    curl -s -X POST -H "Content-Type: application/json" -d '{"state":false}' http://localhost:$SERVICE_PORT/led > /dev/null
    
    log "✅ Pruebas de API completadas"
}

show_logs() {
    if [ -f "$LOG_DIR/app.log" ]; then
        log "Mostrando logs en tiempo real (Ctrl+C para salir)..."
        tail -f "$LOG_DIR/app.log"
    else
        error "No se encontraron logs de la aplicación"
        return 1
    fi
}

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

main() {
    case "${1:-help}" in
        "install")
            check_root_needed "$1"
            log "=== INSTALANDO DEPENDENCIAS DEL SISTEMA ==="
            install_system_dependencies
            log "✅ Instalación completada"
            ;;
        
        "setup")
            check_root_needed "$1"
            log "=== CONFIGURACIÓN COMPLETA DEL SISTEMA ==="
            install_system_dependencies
            setup_usb_permissions
            configure_device_permissions || warning "Dispositivo no encontrado"
            
            # Cambiar al usuario original para configurar Python
            if [ -n "$SUDO_USER" ]; then
                sudo -u "$SUDO_USER" bash -c "
                    cd '$APP_DIR'
                    source /dev/stdin << 'EOF'
$(declare -f setup_python_environment create_directories create_config_file log warning)
setup_python_environment
create_directories
create_config_file
EOF
                "
            else
                setup_python_environment
                create_directories
                create_config_file
            fi
            
            log "✅ Configuración completa terminada"
            log "Para iniciar la aplicación: $0 start"
            ;;
        
        "check")
            log "=== VERIFICACIÓN DE REQUISITOS ==="
            check_system_requirements
            check_usb_permissions
            check_device || warning "Conecte el dispositivo SecuGen"
            
            echo ""
            echo "📋 RESUMEN:"
            echo -e "${GREEN}✅ Verificaciones exitosas: $CHECKS_PASSED${NC}"
            echo -e "${YELLOW}⚠️  Advertencias: $CHECKS_WARNING${NC}"
            echo -e "${RED}❌ Verificaciones fallidas: $CHECKS_FAILED${NC}"
            
            if [ $CHECKS_FAILED -eq 0 ]; then
                echo -e "${GREEN}🎉 Sistema listo${NC}"
            else
                echo -e "${RED}❌ Corrija los problemas antes de continuar${NC}"
            fi
            ;;
        
        "start")
            start_application
            ;;
        
        "stop")
            stop_application
            ;;
        
        "restart")
            restart_application
            ;;
        
        "status")
            status_application
            ;;
        
        "backup")
            create_backup
            ;;
        
        "test")
            test_api
            ;;
        
        "logs")
            show_logs
            ;;
        
        "help"|*)
            show_help
            ;;
    esac
}

# Verificar que se ejecute desde el directorio correcto
if [ ! -f "app.py" ]; then
    error "Este script debe ejecutarse desde el directorio del proyecto"
    error "Debe existir el archivo 'app.py' en el directorio actual"
    exit 1
fi

# Ejecutar función principal con todos los argumentos
main "$@" 