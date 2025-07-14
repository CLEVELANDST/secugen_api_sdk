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

