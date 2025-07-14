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

