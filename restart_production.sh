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

