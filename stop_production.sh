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

