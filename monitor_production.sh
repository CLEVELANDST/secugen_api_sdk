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

