#!/bin/bash

# INICIAR SISTEMA ROBUSTO - Prevención de Problemas Comunes
# ========================================================
# Este script inicia el sistema de forma robusta, previniendo
# y solucionando automáticamente los problemas más comunes.

echo "🚀 INICIANDO SISTEMA ROBUSTO"
echo "=============================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
APP_FILE="app.py"
BACKUP_FILE="app_backup.py"
PORT=5000
VENV_PATH="venv"
LOG_FILE="logs/sistema_robusto.log"

# Crear directorio de logs
mkdir -p logs

# Función para logging
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Función para mostrar pasos
show_step() {
    echo -e "\n${BLUE}🔧 PASO $1: $2${NC}"
    echo "----------------------------------------"
}

# Función para verificar comandos
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅ $1 disponible${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 no encontrado${NC}"
        return 1
    fi
}

# Función para matar procesos Flask
kill_flask_processes() {
    echo "🔪 Terminando procesos Flask existentes..."
    
    # Buscar procesos Flask
    FLASK_PIDS=$(ps aux | grep "[p]ython3.*app.py" | awk '{print $2}')
    
    if [ -n "$FLASK_PIDS" ]; then
        echo "Terminando procesos: $FLASK_PIDS"
        echo "$FLASK_PIDS" | xargs kill -TERM 2>/dev/null
        sleep 2
        echo "$FLASK_PIDS" | xargs kill -KILL 2>/dev/null
        echo -e "${GREEN}✅ Procesos Flask terminados${NC}"
    else
        echo -e "${GREEN}✅ No hay procesos Flask ejecutándose${NC}"
    fi
}

# Función para liberar puerto
free_port() {
    echo "🔓 Liberando puerto $PORT..."
    
    # Buscar procesos en el puerto
    PORT_PIDS=$(lsof -t -i:$PORT 2>/dev/null)
    
    if [ -n "$PORT_PIDS" ]; then
        echo "Terminando procesos en puerto $PORT: $PORT_PIDS"
        echo "$PORT_PIDS" | xargs kill -TERM 2>/dev/null
        sleep 2
        echo "$PORT_PIDS" | xargs kill -KILL 2>/dev/null
        echo -e "${GREEN}✅ Puerto $PORT liberado${NC}"
    else
        echo -e "${GREEN}✅ Puerto $PORT ya está libre${NC}"
    fi
}

# Función para verificar sintaxis Python
check_python_syntax() {
    echo "🔍 Verificando sintaxis de Python..."
    
    if python3 -m py_compile "$APP_FILE" 2>/dev/null; then
        echo -e "${GREEN}✅ Sintaxis Python correcta${NC}"
        return 0
    else
        echo -e "${RED}❌ Error de sintaxis en $APP_FILE${NC}"
        return 1
    fi
}

# Función para restaurar desde backup
restore_from_backup() {
    if [ -f "$BACKUP_FILE" ]; then
        echo "📁 Restaurando desde backup..."
        cp "$BACKUP_FILE" "$APP_FILE"
        echo -e "${GREEN}✅ Archivo restaurado desde backup${NC}"
        return 0
    else
        echo -e "${RED}❌ Archivo de backup no encontrado${NC}"
        return 1
    fi
}

# Función para configurar dispositivo USB
setup_usb_device() {
    echo "🔌 Configurando dispositivo USB SecuGen..."
    
    # Verificar si el dispositivo está presente
    if lsusb | grep -q "1162:2201"; then
        echo -e "${GREEN}✅ Dispositivo SecuGen detectado${NC}"
    else
        echo -e "${RED}❌ Dispositivo SecuGen no detectado${NC}"
        return 1
    fi
    
    # Verificar reglas udev
    if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
        echo -e "${GREEN}✅ Reglas udev instaladas${NC}"
    else
        echo "⚠️ Instalando reglas udev..."
        if [ -f "docker/99SecuGen.rules" ]; then
            sudo cp docker/99SecuGen.rules /etc/udev/rules.d/
            sudo udevadm control --reload-rules
            sudo udevadm trigger
            echo -e "${GREEN}✅ Reglas udev instaladas${NC}"
        else
            echo -e "${RED}❌ Archivo de reglas udev no encontrado${NC}"
            return 1
        fi
    fi
    
    # Verificar symlink persistente
    if [ -L "/dev/secugen_device" ]; then
        echo -e "${GREEN}✅ Symlink persistente configurado${NC}"
    else
        echo "⚠️ Symlink persistente no encontrado"
        # Intentar crear manualmente
        sudo udevadm trigger
        sleep 2
        if [ -L "/dev/secugen_device" ]; then
            echo -e "${GREEN}✅ Symlink persistente creado${NC}"
        else
            echo -e "${YELLOW}⚠️ Symlink persistente no disponible${NC}"
        fi
    fi
}

# Función para activar entorno virtual
activate_venv() {
    if [ -d "$VENV_PATH" ]; then
        echo "🐍 Activando entorno virtual..."
        source "$VENV_PATH/bin/activate"
        echo -e "${GREEN}✅ Entorno virtual activado${NC}"
        return 0
    else
        echo -e "${RED}❌ Entorno virtual no encontrado${NC}"
        return 1
    fi
}

# Función para verificar dependencias Python
check_python_dependencies() {
    echo "📦 Verificando dependencias Python..."
    
    # Lista de dependencias críticas
    dependencies=("flask" "flask_cors" "numpy" "requests")
    
    for dep in "${dependencies[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            echo -e "${GREEN}✅ $dep disponible${NC}"
        else
            echo -e "${RED}❌ $dep no disponible${NC}"
            echo "Instalando $dep..."
            pip install "$dep"
        fi
    done
}

# Función para resetear dispositivo USB si es necesario
reset_usb_if_needed() {
    echo "🔄 Verificando estado del dispositivo USB..."
    
    # Probar conexión básica con el SDK
    if python3 -c "
from sdk import PYSGFPLib
from python.sgfdxerrorcode import SGFDxErrorCode
sgfp = PYSGFPLib()
sgfp.Create()
sgfp.Init(1)
result = sgfp.OpenDevice(0)
print(f'OpenDevice result: {result}')
exit(0 if result == SGFDxErrorCode.SGFDX_ERROR_NONE else 1)
" 2>/dev/null; then
        echo -e "${GREEN}✅ Dispositivo USB funcionando correctamente${NC}"
    else
        echo -e "${YELLOW}⚠️ Dispositivo USB necesita reset${NC}"
        echo "🔄 Ejecutando reset USB..."
        
        if python3 reset_usb_device.py; then
            echo -e "${GREEN}✅ Reset USB completado${NC}"
        else
            echo -e "${RED}❌ Reset USB falló${NC}"
            return 1
        fi
    fi
}

# Función para iniciar Flask de forma robusta
start_flask_robust() {
    echo "🚀 Iniciando Flask de forma robusta..."
    
    # Verificar que todo esté listo
    if ! check_python_syntax; then
        echo "❌ No se puede iniciar Flask debido a errores de sintaxis"
        return 1
    fi
    
    # Iniciar Flask con manejo de errores
    echo "🔥 Iniciando servidor Flask..."
    
    # Iniciar en background con logs
    nohup python3 "$APP_FILE" > "logs/flask_output.log" 2>&1 &
    FLASK_PID=$!
    
    # Esperar a que inicie
    echo "⏳ Esperando inicio del servidor..."
    sleep 5
    
    # Verificar que esté corriendo
    if kill -0 "$FLASK_PID" 2>/dev/null; then
        echo -e "${GREEN}✅ Flask iniciado correctamente (PID: $FLASK_PID)${NC}"
        echo "$FLASK_PID" > "logs/flask.pid"
        
        # Verificar que responda
        if curl -s http://localhost:$PORT/ >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Servidor Flask responde correctamente${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️ Servidor Flask iniciado pero no responde${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Flask no pudo iniciarse${NC}"
        return 1
    fi
}

# Función principal
main() {
    log_message "=== INICIANDO SISTEMA ROBUSTO ==="
    
    # Paso 1: Verificar herramientas básicas
    show_step "1" "VERIFICACIÓN DE HERRAMIENTAS"
    check_command "python3"
    check_command "pip"
    check_command "lsof"
    check_command "curl"
    
    # Paso 2: Limpiar procesos existentes
    show_step "2" "LIMPIEZA DE PROCESOS"
    kill_flask_processes
    free_port
    
    # Paso 3: Activar entorno virtual
    show_step "3" "ENTORNO VIRTUAL"
    if ! activate_venv; then
        echo -e "${RED}❌ No se puede continuar sin entorno virtual${NC}"
        exit 1
    fi
    
    # Paso 4: Verificar dependencias
    show_step "4" "DEPENDENCIAS PYTHON"
    check_python_dependencies
    
    # Paso 5: Verificar sintaxis
    show_step "5" "VERIFICACIÓN DE SINTAXIS"
    if ! check_python_syntax; then
        echo "🔧 Intentando restaurar desde backup..."
        if restore_from_backup; then
            if ! check_python_syntax; then
                echo -e "${RED}❌ No se pudo corregir la sintaxis${NC}"
                exit 1
            fi
        else
            echo -e "${RED}❌ No se puede continuar con errores de sintaxis${NC}"
            exit 1
        fi
    fi
    
    # Paso 6: Configurar dispositivo USB
    show_step "6" "CONFIGURACIÓN USB"
    setup_usb_device
    
    # Paso 7: Reset USB si es necesario
    show_step "7" "VERIFICACIÓN/RESET USB"
    reset_usb_if_needed
    
    # Paso 8: Iniciar Flask
    show_step "8" "INICIO DE FLASK"
    if start_flask_robust; then
        echo -e "\n${GREEN}🎉 ¡SISTEMA INICIADO EXITOSAMENTE!${NC}"
        echo "====================================="
        echo "📱 URL: http://localhost:$PORT"
        echo "📊 Logs: tail -f logs/flask_output.log"
        echo "🛑 Parar: ./parar_sistema.sh"
        echo "🔍 Monitor: python3 monitor_sistema_completo.py"
        
        # Mostrar endpoints disponibles
        echo -e "\n🔗 ENDPOINTS DISPONIBLES:"
        echo "   POST /initialize       - Inicializar dispositivo"
        echo "   POST /led             - Controlar LED"
        echo "   POST /capturar-huella - Capturar huella"
        echo "   POST /comparar-huellas - Comparar huellas"
        
        log_message "Sistema iniciado exitosamente"
        
        # Ofrecer iniciar monitor
        echo -e "\n${BLUE}¿Iniciar monitor del sistema? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "🔍 Iniciando monitor del sistema..."
            python3 monitor_sistema_completo.py &
            MONITOR_PID=$!
            echo "$MONITOR_PID" > "logs/monitor.pid"
            echo -e "${GREEN}✅ Monitor iniciado (PID: $MONITOR_PID)${NC}"
        fi
        
    else
        echo -e "\n${RED}❌ ERROR AL INICIAR EL SISTEMA${NC}"
        echo "=============================="
        echo "📋 Revisa los logs para más detalles:"
        echo "   tail -f logs/flask_output.log"
        echo "   tail -f logs/sistema_robusto.log"
        
        log_message "Error al iniciar el sistema"
        exit 1
    fi
}

# Manejo de señales
trap 'echo -e "\n${YELLOW}⏹️ Proceso interrumpido${NC}"; exit 1' INT TERM

# Ejecutar función principal
main "$@" 