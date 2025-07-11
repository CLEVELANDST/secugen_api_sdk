#!/bin/bash

# Script de Configuración para Producción
# Sistema de Huellas Digitales SecuGen
# Automatiza toda la configuración necesaria para producción

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración
APP_NAME="secugen-fingerprint-api"
APP_DIR="$(pwd)"
SERVICE_USER="$USER"
SERVICE_PORT="5000"
PYTHON_ENV="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"
BACKUP_DIR="$APP_DIR/backups"

# Función para logging
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

# Función para verificar si el script se ejecuta como root cuando es necesario
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "Este script no debe ejecutarse como root"
        exit 1
    fi
}

# Función para verificar dependencias del sistema
check_system_dependencies() {
    log "Verificando dependencias del sistema..."
    
    # Verificar distribución
    if ! command -v apt-get &> /dev/null; then
        error "Este script está diseñado para sistemas basados en Debian/Ubuntu"
        exit 1
    fi
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 no está instalado"
        exit 1
    fi
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 no está instalado"
        exit 1
    fi
    
    log "✅ Dependencias del sistema verificadas"
}

# Función para instalar dependencias del sistema
install_system_dependencies() {
    log "Instalando dependencias del sistema..."
    
    # Actualizar repositorios
    sudo apt-get update -y
    
    # Instalar dependencias
    sudo apt-get install -y \
        python3-venv \
        python3-dev \
        libusb-dev \
        libusb-0.1-4 \
        udev \
        systemd \
        curl \
        git \
        build-essential \
        pkg-config
    
    log "✅ Dependencias del sistema instaladas"
}

# Función para configurar entorno Python
setup_python_environment() {
    log "Configurando entorno Python..."
    
    # Crear directorio virtual si no existe
    if [ ! -d "$PYTHON_ENV" ]; then
        python3 -m venv "$PYTHON_ENV"
        log "✅ Entorno virtual creado"
    fi
    
    # Activar entorno virtual
    source "$PYTHON_ENV/bin/activate"
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias
    if [ -f "requirements-minimal.txt" ]; then
        pip install -r requirements-minimal.txt
        log "✅ Dependencias Python instaladas desde requirements-minimal.txt"
    else
        # Instalar dependencias básicas
        pip install flask werkzeug flask-cors python-dotenv pyusb requests
        log "✅ Dependencias Python básicas instaladas"
    fi
    
    log "✅ Entorno Python configurado"
}

# Función para configurar permisos USB
setup_usb_permissions() {
    log "Configurando permisos USB..."
    
    # Copiar reglas udev
    if [ -f "docker/99SecuGen.rules" ]; then
        sudo cp docker/99SecuGen.rules /etc/udev/rules.d/
        log "✅ Reglas udev copiadas"
    else
        # Crear reglas udev básicas
        sudo tee /etc/udev/rules.d/99SecuGen.rules > /dev/null <<EOF
# SecuGen Fingerprint Reader Rules
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="2201", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="0300", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="0400", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}=="1162", ATTR{idProduct}=="0500", MODE="0666", GROUP="plugdev"
EOF
        log "✅ Reglas udev creadas"
    fi
    
    # Recargar reglas udev
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    # Agregar usuario al grupo plugdev
    sudo usermod -a -G plugdev "$SERVICE_USER"
    
    log "✅ Permisos USB configurados"
}

# Función para crear directorios necesarios
create_directories() {
    log "Creando directorios necesarios..."
    
    # Crear directorio de logs
    mkdir -p "$LOG_DIR"
    
    # Crear directorio de backups
    mkdir -p "$BACKUP_DIR"
    
    # Crear directorio de configuración
    mkdir -p "$APP_DIR/config"
    
    log "✅ Directorios creados"
}

# Función para crear archivo de configuración
create_config_file() {
    log "Creando archivo de configuración..."
    
    cat > "$APP_DIR/config/production.env" <<EOF
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

# Función para crear script de inicio
create_startup_script() {
    log "Creando script de inicio..."
    
    cat > "$APP_DIR/start_production.sh" <<'EOF'
#!/bin/bash

# Script de Inicio para Producción
set -e

# Configuración
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$APP_DIR/logs"
PYTHON_ENV="$APP_DIR/venv"
CONFIG_FILE="$APP_DIR/config/production.env"

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/startup.log"
}

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

log "Iniciando aplicación en modo producción..."

# Verificar que el entorno virtual existe
if [ ! -d "$PYTHON_ENV" ]; then
    log "ERROR: Entorno virtual no encontrado en $PYTHON_ENV"
    exit 1
fi

# Verificar que el archivo de configuración existe
if [ ! -f "$CONFIG_FILE" ]; then
    log "ERROR: Archivo de configuración no encontrado en $CONFIG_FILE"
    exit 1
fi

# Activar entorno virtual
source "$PYTHON_ENV/bin/activate"

# Cargar configuración
source "$CONFIG_FILE"

# Verificar conexión del dispositivo
log "Verificando conexión del dispositivo..."
if ! lsusb | grep -i secugen > /dev/null; then
    log "WARNING: Dispositivo SecuGen no detectado"
fi

# Verificar que el puerto esté libre
if netstat -tuln | grep ":$FLASK_PORT " > /dev/null; then
    log "ERROR: Puerto $FLASK_PORT ya está en uso"
    exit 1
fi

# Cambiar al directorio de la aplicación
cd "$APP_DIR"

# Configurar variables de entorno
export LD_LIBRARY_PATH="$APP_DIR/lib/linux3:$LD_LIBRARY_PATH"
export PYTHONPATH="$APP_DIR:$PYTHONPATH"

# Iniciar aplicación
log "Iniciando aplicación en puerto $FLASK_PORT..."
nohup python3 app.py > "$LOG_DIR/app.log" 2>&1 &

# Obtener PID
APP_PID=$!
echo $APP_PID > "$APP_DIR/app.pid"

log "Aplicación iniciada con PID: $APP_PID"

# Esperar un momento y verificar que esté funcionando
sleep 3
if ps -p $APP_PID > /dev/null; then
    log "✅ Aplicación iniciada exitosamente"
    
    # Probar endpoint de salud
    sleep 2
    if curl -f http://localhost:$FLASK_PORT/initialize > /dev/null 2>&1; then
        log "✅ API respondiendo correctamente"
    else
        log "⚠️ API no responde al endpoint de salud"
    fi
else
    log "❌ Error: La aplicación no se inició correctamente"
    exit 1
fi

EOF
    
    chmod +x "$APP_DIR/start_production.sh"
    log "✅ Script de inicio creado"
}

# Función para crear script de parada
create_stop_script() {
    log "Creando script de parada..."
    
    cat > "$APP_DIR/stop_production.sh" <<'EOF'
#!/bin/bash

# Script de Parada para Producción
set -e

# Configuración
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$APP_DIR/app.pid"

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/shutdown.log"
}

log "Deteniendo aplicación..."

# Verificar si existe el archivo PID
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    # Verificar si el proceso está corriendo
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
                log "❌ Error: No se pudo terminar el proceso"
                exit 1
            else
                log "✅ Proceso terminado forzosamente"
            fi
        fi
    else
        log "⚠️ Proceso no estaba corriendo"
    fi
    
    # Eliminar archivo PID
    rm -f "$PID_FILE"
else
    log "⚠️ Archivo PID no encontrado"
    
    # Buscar procesos por nombre
    PIDS=$(pgrep -f "python3 app.py" || true)
    if [ -n "$PIDS" ]; then
        log "Encontrados procesos Python relacionados, terminando..."
        kill -TERM $PIDS
        sleep 2
        # Verificar si terminaron
        REMAINING=$(pgrep -f "python3 app.py" || true)
        if [ -n "$REMAINING" ]; then
            log "Forzando terminación de procesos restantes..."
            kill -KILL $REMAINING
        fi
        log "✅ Procesos terminados"
    else
        log "⚠️ No se encontraron procesos de la aplicación"
    fi
fi

log "Aplicación detenida"

EOF
    
    chmod +x "$APP_DIR/stop_production.sh"
    log "✅ Script de parada creado"
}

# Función para crear script de reinicio
create_restart_script() {
    log "Creando script de reinicio..."
    
    cat > "$APP_DIR/restart_production.sh" <<'EOF'
#!/bin/bash

# Script de Reinicio para Producción
set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$APP_DIR/logs"

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/restart.log"
}

log "Reiniciando aplicación..."

# Detener aplicación
"$APP_DIR/stop_production.sh"

# Esperar un momento
sleep 3

# Iniciar aplicación
"$APP_DIR/start_production.sh"

log "Aplicación reiniciada"

EOF
    
    chmod +x "$APP_DIR/restart_production.sh"
    log "✅ Script de reinicio creado"
}

# Función para crear script de estado
create_status_script() {
    log "Creando script de estado..."
    
    cat > "$APP_DIR/status_production.sh" <<'EOF'
#!/bin/bash

# Script de Estado para Producción
set -e

# Configuración
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$APP_DIR/app.pid"
CONFIG_FILE="$APP_DIR/config/production.env"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función de logging con colores
log_status() {
    echo -e "${GREEN}[STATUS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "=================================================="
echo "🔍 ESTADO DEL SISTEMA DE HUELLAS DIGITALES"
echo "=================================================="

# Verificar configuración
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    log_status "Configuración cargada desde $CONFIG_FILE"
else
    log_error "Archivo de configuración no encontrado"
    FLASK_PORT=5000
fi

# Verificar proceso de la aplicación
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        log_status "Aplicación corriendo con PID: $PID"
        
        # Obtener información del proceso
        ps -p $PID -o pid,ppid,cmd,etime,pcpu,pmem
        
        # Verificar puerto
        if netstat -tuln | grep ":$FLASK_PORT " > /dev/null; then
            log_status "Puerto $FLASK_PORT está escuchando"
        else
            log_warning "Puerto $FLASK_PORT no está escuchando"
        fi
        
        # Probar API
        if curl -f http://localhost:$FLASK_PORT/initialize > /dev/null 2>&1; then
            log_status "API respondiendo correctamente"
        else
            log_error "API no responde"
        fi
    else
        log_error "Proceso no encontrado (PID: $PID)"
        rm -f "$PID_FILE"
    fi
else
    log_warning "Archivo PID no encontrado"
    
    # Buscar procesos relacionados
    PIDS=$(pgrep -f "python3 app.py" || true)
    if [ -n "$PIDS" ]; then
        log_warning "Procesos Python relacionados encontrados:"
        ps -p $PIDS -o pid,ppid,cmd,etime,pcpu,pmem
    else
        log_error "No se encontraron procesos de la aplicación"
    fi
fi

# Verificar dispositivo USB
echo ""
echo "🔌 Estado del Dispositivo USB:"
if lsusb | grep -i secugen > /dev/null; then
    log_status "Dispositivo SecuGen detectado:"
    lsusb | grep -i secugen
else
    log_error "Dispositivo SecuGen no detectado"
fi

# Verificar permisos
echo ""
echo "🔒 Permisos y Configuración:"
if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
    log_status "Reglas udev configuradas"
else
    log_error "Reglas udev no configuradas"
fi

if groups | grep -q plugdev; then
    log_status "Usuario en grupo plugdev"
else
    log_error "Usuario no está en grupo plugdev"
fi

# Verificar logs
echo ""
echo "📋 Logs Recientes:"
if [ -f "$APP_DIR/logs/app.log" ]; then
    echo "Últimas 5 líneas del log:"
    tail -n 5 "$APP_DIR/logs/app.log"
else
    log_warning "No se encontraron logs de la aplicación"
fi

echo ""
echo "=================================================="

EOF
    
    chmod +x "$APP_DIR/status_production.sh"
    log "✅ Script de estado creado"
}

# Función para crear servicio systemd
create_systemd_service() {
    log "Creando servicio systemd..."
    
    cat > "/tmp/$APP_NAME.service" <<EOF
[Unit]
Description=SecuGen Fingerprint API Service
After=network.target
Wants=network.target

[Service]
Type=forking
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/start_production.sh
ExecStop=$APP_DIR/stop_production.sh
ExecReload=$APP_DIR/restart_production.sh
Restart=always
RestartSec=10
PIDFile=$APP_DIR/app.pid

# Configuración de entorno
Environment=LD_LIBRARY_PATH=$APP_DIR/lib/linux3
Environment=PYTHONPATH=$APP_DIR

# Configuración de límites
LimitNOFILE=65536
LimitCORE=infinity

# Configuración de seguridad
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$APP_DIR
ReadWritePaths=$LOG_DIR

[Install]
WantedBy=multi-user.target
EOF
    
    # Copiar e instalar servicio
    sudo mv "/tmp/$APP_NAME.service" "/etc/systemd/system/"
    sudo systemctl daemon-reload
    sudo systemctl enable "$APP_NAME"
    
    log "✅ Servicio systemd creado y habilitado"
}

# Función para crear script de backup
create_backup_script() {
    log "Creando script de backup..."
    
    cat > "$APP_DIR/backup_production.sh" <<'EOF'
#!/bin/bash

# Script de Backup para Producción
set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$APP_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Iniciando backup..."

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR"

# Crear backup
tar -czf "$BACKUP_FILE" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs/*.log' \
    --exclude='backups' \
    -C "$APP_DIR/.." \
    "$(basename "$APP_DIR")"

log "Backup creado: $BACKUP_FILE"

# Limpiar backups antiguos (mantener solo los últimos 10)
cd "$BACKUP_DIR"
ls -t backup_*.tar.gz | tail -n +11 | xargs -r rm -f

log "Backup completado"

EOF
    
    chmod +x "$APP_DIR/backup_production.sh"
    log "✅ Script de backup creado"
}

# Función para crear script de monitoreo
create_monitoring_script() {
    log "Creando script de monitoreo..."
    
    cat > "$APP_DIR/monitor_production.sh" <<'EOF'
#!/bin/bash

# Script de Monitoreo para Producción
set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$APP_DIR/logs"
PID_FILE="$APP_DIR/app.pid"
CONFIG_FILE="$APP_DIR/config/production.env"

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/monitor.log"
}

# Cargar configuración
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Verificar si la aplicación está corriendo
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ! ps -p $PID > /dev/null 2>&1; then
        log "ERROR: Aplicación no está corriendo. Reiniciando..."
        "$APP_DIR/start_production.sh"
        exit 0
    fi
else
    log "ERROR: Archivo PID no encontrado. Reiniciando..."
    "$APP_DIR/start_production.sh"
    exit 0
fi

# Verificar que la API responda
if ! curl -f http://localhost:${FLASK_PORT:-5000}/initialize > /dev/null 2>&1; then
    log "ERROR: API no responde. Reiniciando..."
    "$APP_DIR/restart_production.sh"
    exit 0
fi

# Verificar dispositivo USB
if ! lsusb | grep -i secugen > /dev/null; then
    log "WARNING: Dispositivo SecuGen no detectado"
fi

# Verificar uso de memoria
MEMORY_USAGE=$(ps -p $PID -o %mem --no-headers | tr -d ' ')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    log "WARNING: Uso de memoria alto: $MEMORY_USAGE%"
fi

# Verificar tamaño de logs
LOG_SIZE=$(du -m "$LOG_DIR/app.log" 2>/dev/null | cut -f1 || echo 0)
if [ $LOG_SIZE -gt 100 ]; then
    log "WARNING: Log muy grande ($LOG_SIZE MB). Rotando..."
    mv "$LOG_DIR/app.log" "$LOG_DIR/app.log.$(date +%Y%m%d_%H%M%S)"
fi

EOF
    
    chmod +x "$APP_DIR/monitor_production.sh"
    log "✅ Script de monitoreo creado"
}

# Función para configurar cron para monitoreo
setup_cron_monitoring() {
    log "Configurando monitoreo automático..."
    
    # Agregar tarea cron para monitoreo cada 5 minutos
    (crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/monitor_production.sh") | crontab -
    
    # Agregar tarea cron para backup diario
    (crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup_production.sh") | crontab -
    
    log "✅ Monitoreo automático configurado"
}

# Función para verificar instalación
verify_installation() {
    log "Verificando instalación..."
    
    # Verificar archivos principales
    local files=(
        "app.py"
        "start_production.sh"
        "stop_production.sh"
        "restart_production.sh"
        "status_production.sh"
        "backup_production.sh"
        "monitor_production.sh"
        "config/production.env"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$APP_DIR/$file" ]; then
            log "✅ $file existe"
        else
            error "❌ $file no encontrado"
            return 1
        fi
    done
    
    # Verificar servicio systemd
    if systemctl is-enabled "$APP_NAME" > /dev/null 2>&1; then
        log "✅ Servicio systemd habilitado"
    else
        warning "⚠️ Servicio systemd no habilitado"
    fi
    
    # Verificar permisos USB
    if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
        log "✅ Reglas udev configuradas"
    else
        warning "⚠️ Reglas udev no configuradas"
    fi
    
    log "✅ Verificación completada"
}

# Función principal
main() {
    echo "=================================================="
    echo "🚀 CONFIGURACIÓN PARA PRODUCCIÓN"
    echo "   Sistema de Huellas Digitales SecuGen"
    echo "=================================================="
    
    # Verificaciones iniciales
    check_root
    check_system_dependencies
    
    # Instalación y configuración
    install_system_dependencies
    setup_python_environment
    setup_usb_permissions
    create_directories
    create_config_file
    
    # Scripts de administración
    create_startup_script
    create_stop_script
    create_restart_script
    create_status_script
    create_backup_script
    create_monitoring_script
    
    # Configuración de servicios
    create_systemd_service
    setup_cron_monitoring
    
    # Verificación final
    verify_installation
    
    echo ""
    echo "=================================================="
    echo "✅ CONFIGURACIÓN COMPLETADA"
    echo "=================================================="
    echo ""
    echo "🎯 COMANDOS DISPONIBLES:"
    echo "   • Iniciar:     ./start_production.sh"
    echo "   • Parar:       ./stop_production.sh"
    echo "   • Reiniciar:   ./restart_production.sh"
    echo "   • Estado:      ./status_production.sh"
    echo "   • Backup:      ./backup_production.sh"
    echo "   • Monitor:     ./monitor_production.sh"
    echo ""
    echo "🔧 SERVICIOS SYSTEMD:"
    echo "   • Iniciar:     sudo systemctl start $APP_NAME"
    echo "   • Parar:       sudo systemctl stop $APP_NAME"
    echo "   • Reiniciar:   sudo systemctl restart $APP_NAME"
    echo "   • Estado:      sudo systemctl status $APP_NAME"
    echo "   • Logs:        sudo journalctl -u $APP_NAME -f"
    echo ""
    echo "📋 ARCHIVOS IMPORTANTES:"
    echo "   • Config:      $APP_DIR/config/production.env"
    echo "   • Logs:        $APP_DIR/logs/"
    echo "   • Backups:     $APP_DIR/backups/"
    echo "   • PID:         $APP_DIR/app.pid"
    echo ""
    echo "⚠️  NOTA: Es necesario reiniciar la sesión para que los"
    echo "   cambios de grupo (plugdev) tengan efecto."
    echo ""
    echo "🚀 Para iniciar la aplicación ahora:"
    echo "   ./start_production.sh"
    echo ""
}

# Ejecutar función principal
main "$@" 