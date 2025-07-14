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

