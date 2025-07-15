#!/bin/bash

# DOCKER ENTRYPOINT - Sistema Robusto para Contenedor
# ==================================================
# Script de inicio para contenedor Docker que integra
# el sistema robusto de SecuGen

echo "🐳 INICIANDO CONTENEDOR SECUGEN CON SISTEMA ROBUSTO"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
LOG_FILE="/app/logs/docker_entrypoint.log"
PYTHON_PATH="/app"

# Función para logging
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Función para mostrar pasos
show_step() {
    echo -e "\n${BLUE}🔧 $1${NC}"
    echo "----------------------------------------"
}

# Función para verificar dispositivo USB
verify_usb_device() {
    show_step "VERIFICANDO DISPOSITIVO USB"
    
    # Esperar un momento para que el dispositivo se estabilice
    sleep 2
    
    # Verificar dispositivo SecuGen
    if lsusb | grep -q "1162:2201"; then
        echo -e "${GREEN}✅ Dispositivo SecuGen detectado${NC}"
        lsusb | grep "1162:2201"
        log_message "Dispositivo SecuGen detectado"
        return 0
    else
        echo -e "${YELLOW}⚠️ Dispositivo SecuGen no detectado${NC}"
        echo "Dispositivos USB disponibles:"
        lsusb
        log_message "Dispositivo SecuGen no detectado"
        return 1
    fi
}

# Función para verificar permisos
verify_permissions() {
    show_step "VERIFICANDO PERMISOS"
    
    # Verificar que estamos en el grupo correcto
    if groups | grep -q "dialout"; then
        echo -e "${GREEN}✅ Usuario en grupo dialout${NC}"
    else
        echo -e "${YELLOW}⚠️ Usuario no en grupo dialout${NC}"
    fi
    
    if groups | grep -q "plugdev"; then
        echo -e "${GREEN}✅ Usuario en grupo plugdev${NC}"
    else
        echo -e "${YELLOW}⚠️ Usuario no en grupo plugdev${NC}"
    fi
    
    # Verificar permisos de directorio
    if [ -w "/app/logs" ]; then
        echo -e "${GREEN}✅ Permisos de escritura en logs${NC}"
    else
        echo -e "${RED}❌ Sin permisos de escritura en logs${NC}"
        return 1
    fi
    
    log_message "Verificación de permisos completada"
    return 0
}

# Función para configurar entorno
setup_environment() {
    show_step "CONFIGURANDO ENTORNO"
    
    # Crear directorios necesarios
    mkdir -p /app/logs /app/templates /app/backups
    
    # Configurar variables de entorno
    export PYTHONPATH="/app"
    export FLASK_ENV="production"
    export FLASK_APP="app.py"
    
    # Configurar logging
    touch "$LOG_FILE"
    
    echo -e "${GREEN}✅ Entorno configurado${NC}"
    log_message "Entorno configurado"
}

# Función para probar SDK
test_sdk() {
    show_step "PROBANDO SDK SECUGEN"
    
    # Probar importación del SDK
    if python3 -c "
import sys
sys.path.insert(0, '/app')
try:
    from sdk import PYSGFPLib
    print('✅ SDK importado correctamente')
    exit(0)
except Exception as e:
    print(f'❌ Error importando SDK: {e}')
    exit(1)
" 2>>/app/logs/sdk_test.log; then
        echo -e "${GREEN}✅ SDK funciona correctamente${NC}"
        log_message "SDK probado exitosamente"
        return 0
    else
        echo -e "${YELLOW}⚠️ SDK no se pudo probar completamente${NC}"
        echo "Esto puede ser normal si el dispositivo no está conectado"
        log_message "SDK no se pudo probar completamente"
        return 1
    fi
}

# Función para reset USB si es necesario
reset_usb_if_needed() {
    show_step "VERIFICANDO NECESIDAD DE RESET USB"
    
    # Verificar si el dispositivo responde correctamente
    if python3 -c "
import sys
sys.path.insert(0, '/app')
try:
    from sdk import PYSGFPLib
    from python.sgfdxerrorcode import SGFDxErrorCode
    sgfp = PYSGFPLib()
    sgfp.Create()
    sgfp.Init(1)
    result = sgfp.OpenDevice(0)
    print(f'OpenDevice result: {result}')
    exit(0 if result == SGFDxErrorCode.SGFDX_ERROR_NONE else 1)
except Exception as e:
    print(f'Error: {e}')
    exit(1)
" 2>/dev/null; then
        echo -e "${GREEN}✅ Dispositivo USB funcionando correctamente${NC}"
        log_message "Dispositivo USB funcionando correctamente"
        return 0
    else
        echo -e "${YELLOW}⚠️ Dispositivo USB necesita reset${NC}"
        echo "🔄 Ejecutando reset USB..."
        
        # Ejecutar reset USB
        if python3 /app/reset_usb_device.py 2>/dev/null; then
            echo -e "${GREEN}✅ Reset USB completado${NC}"
            log_message "Reset USB completado"
            return 0
        else
            echo -e "${YELLOW}⚠️ Reset USB tuvo problemas${NC}"
            log_message "Reset USB tuvo problemas"
            return 1
        fi
    fi
}

# Función para iniciar aplicación
start_application() {
    show_step "INICIANDO APLICACIÓN FLASK"
    
    # Verificar que el archivo existe
    if [ ! -f "/app/app.py" ]; then
        echo -e "${RED}❌ app.py no encontrado${NC}"
        log_message "ERROR: app.py no encontrado"
        exit 1
    fi
    
    # Verificar sintaxis
    if python3 -m py_compile /app/app.py 2>/dev/null; then
        echo -e "${GREEN}✅ Sintaxis Python correcta${NC}"
        log_message "Sintaxis Python verificada"
    else
        echo -e "${RED}❌ Error de sintaxis en app.py${NC}"
        log_message "ERROR: Error de sintaxis en app.py"
        
        # Intentar restaurar desde backup
        if [ -f "/app/app_backup.py" ]; then
            echo "🔧 Restaurando desde backup..."
            cp /app/app_backup.py /app/app.py
            log_message "Restaurado desde backup"
        else
            echo -e "${RED}❌ No se puede continuar sin archivo válido${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Iniciando aplicación Flask...${NC}"
    log_message "Iniciando aplicación Flask"
    
    # Cambiar al directorio de la aplicación
    cd /app
    
    # Iniciar Flask
    exec python3 app.py
}

# Función para cleanup al salir
cleanup() {
    echo -e "\n${YELLOW}🛑 Deteniendo contenedor...${NC}"
    log_message "Contenedor detenido"
    
    # Terminar procesos hijo
    pkill -P $$
    
    exit 0
}

# Configurar trap para cleanup
trap cleanup SIGTERM SIGINT

# Función principal
main() {
    log_message "=== INICIANDO CONTENEDOR SECUGEN ==="
    
    # Mostrar información del contenedor
    echo "🐳 Contenedor SecuGen iniciado"
    echo "📅 Fecha: $(date)"
    echo "🖥️ Hostname: $(hostname)"
    echo "👤 Usuario: $(whoami)"
    echo "📁 Directorio: $(pwd)"
    echo "🔧 Python: $(python3 --version)"
    
    # Ejecutar verificaciones
    setup_environment
    verify_permissions
    verify_usb_device
    test_sdk
    reset_usb_if_needed
    
    # Esperar un momento para estabilización
    sleep 2
    
    # Iniciar aplicación
    start_application
}

# Ejecutar función principal
main "$@" 