#!/bin/bash

# PARAR SISTEMA - Detener todos los procesos de forma segura
# ========================================================

echo "🛑 PARANDO SISTEMA SECUGEN"
echo "=========================="

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Archivos PID
FLASK_PID_FILE="logs/flask.pid"
MONITOR_PID_FILE="logs/monitor.pid"

# Función para terminar proceso por PID
kill_process_by_pid() {
    local pid_file="$1"
    local process_name="$2"
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        if kill -0 "$PID" 2>/dev/null; then
            echo "🔪 Terminando $process_name (PID: $PID)..."
            kill -TERM "$PID" 2>/dev/null
            sleep 2
            if kill -0 "$PID" 2>/dev/null; then
                kill -KILL "$PID" 2>/dev/null
            fi
            echo -e "${GREEN}✅ $process_name terminado${NC}"
        else
            echo -e "${YELLOW}⚠️ $process_name no está corriendo${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️ Archivo PID de $process_name no encontrado${NC}"
    fi
}

# Función para terminar procesos por nombre
kill_processes_by_name() {
    local pattern="$1"
    local process_name="$2"
    
    PIDS=$(ps aux | grep "$pattern" | grep -v grep | awk '{print $2}')
    
    if [ -n "$PIDS" ]; then
        echo "🔪 Terminando procesos $process_name..."
        for PID in $PIDS; do
            echo "   Terminando PID: $PID"
            kill -TERM "$PID" 2>/dev/null
        done
        
        sleep 2
        
        # Forzar si es necesario
        PIDS=$(ps aux | grep "$pattern" | grep -v grep | awk '{print $2}')
        if [ -n "$PIDS" ]; then
            for PID in $PIDS; do
                kill -KILL "$PID" 2>/dev/null
            done
        fi
        
        echo -e "${GREEN}✅ Procesos $process_name terminados${NC}"
    else
        echo -e "${YELLOW}⚠️ No se encontraron procesos $process_name${NC}"
    fi
}

# Parar Flask
echo "🔥 Parando Flask..."
kill_process_by_pid "$FLASK_PID_FILE" "Flask"

# Parar monitor
echo "🔍 Parando monitor..."
kill_process_by_pid "$MONITOR_PID_FILE" "Monitor"

# Parar cualquier proceso Flask restante
echo "🧹 Limpiando procesos Flask restantes..."
kill_processes_by_name "[p]ython3.*app.py" "Flask"

# Parar procesos monitor restantes
echo "🧹 Limpiando procesos monitor restantes..."
kill_processes_by_name "[p]ython3.*monitor_sistema_completo.py" "Monitor"

# Liberar puerto
echo "🔓 Liberando puerto 5000..."
PORT_PIDS=$(lsof -t -i:5000 2>/dev/null)
if [ -n "$PORT_PIDS" ]; then
    echo "$PORT_PIDS" | xargs kill -TERM 2>/dev/null
    sleep 2
    echo "$PORT_PIDS" | xargs kill -KILL 2>/dev/null
    echo -e "${GREEN}✅ Puerto 5000 liberado${NC}"
else
    echo -e "${GREEN}✅ Puerto 5000 ya está libre${NC}"
fi

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
rm -f logs/flask.pid logs/monitor.pid
rm -f nohup.out

echo -e "\n${GREEN}🎉 ¡SISTEMA PARADO EXITOSAMENTE!${NC}"
echo "================================="
echo "📊 Logs disponibles:"
echo "   - logs/flask_output.log"
echo "   - logs/sistema_robusto.log"
echo "   - logs/monitor_sistema.log"
echo ""
echo "🚀 Para reiniciar: ./iniciar_sistema_robusto.sh" 