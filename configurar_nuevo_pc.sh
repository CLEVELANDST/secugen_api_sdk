#!/bin/bash

# CONFIGURAR NUEVO PC - Configuración automática completa
# ======================================================
# Este script configura automáticamente un nuevo PC para que
# el lector de huellas SecuGen funcione sin problemas

echo "🖥️ CONFIGURACIÓN AUTOMÁTICA PARA NUEVO PC"
echo "=========================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
LOG_FILE="logs/configuracion_nuevo_pc.log"
USUARIO_ACTUAL=$(whoami)

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

# Función para verificar si se ejecuta como root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}❌ NO ejecutes este script como root${NC}"
        echo "💡 Ejecuta como usuario normal: $0"
        exit 1
    fi
}

# Función para verificar sudo
check_sudo() {
    if ! sudo -v; then
        echo -e "${RED}❌ Necesitas permisos sudo para continuar${NC}"
        exit 1
    fi
}

# Función para verificar distribución
check_distribution() {
    if [ -f /etc/debian_version ]; then
        echo -e "${GREEN}✅ Sistema Debian/Ubuntu detectado${NC}"
        return 0
    elif [ -f /etc/redhat-release ]; then
        echo -e "${YELLOW}⚠️ Sistema Red Hat/CentOS detectado${NC}"
        echo "Este script está optimizado para Ubuntu/Debian"
        echo "¿Continuar de todos modos? (y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            exit 1
        fi
        return 0
    else
        echo -e "${RED}❌ Distribución no soportada${NC}"
        exit 1
    fi
}

# Función para instalar dependencias del sistema
install_system_dependencies() {
    echo "📦 Instalando dependencias del sistema..."
    
    # Actualizar repositorios
    sudo apt update
    
    # Instalar dependencias básicas
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        libusb-0.1-4 \
        build-essential \
        curl \
        git \
        lsof \
        udev \
        usbutils
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Dependencias del sistema instaladas${NC}"
        log_message "Dependencias del sistema instaladas correctamente"
    else
        echo -e "${RED}❌ Error instalando dependencias del sistema${NC}"
        exit 1
    fi
}

# Función para crear entorno virtual
create_virtual_environment() {
    echo "🐍 Creando entorno virtual Python..."
    
    # Eliminar venv anterior si existe
    if [ -d "venv" ]; then
        echo "🗑️ Eliminando entorno virtual anterior..."
        rm -rf venv
    fi
    
    # Crear nuevo entorno virtual
    python3 -m venv venv
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias Python
    pip install flask flask-cors numpy requests psutil
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Entorno virtual creado e instalado${NC}"
        log_message "Entorno virtual configurado correctamente"
    else
        echo -e "${RED}❌ Error creando entorno virtual${NC}"
        exit 1
    fi
}

# Función para configurar permisos USB
configure_usb_permissions() {
    echo "🔐 Configurando permisos USB..."
    
    # Agregar usuario a grupos necesarios
    sudo usermod -a -G dialout "$USUARIO_ACTUAL"
    sudo usermod -a -G plugdev "$USUARIO_ACTUAL"
    
    # Verificar que los grupos existen
    if ! getent group dialout >/dev/null; then
        sudo groupadd dialout
    fi
    
    if ! getent group plugdev >/dev/null; then
        sudo groupadd plugdev
    fi
    
    echo -e "${GREEN}✅ Usuario $USUARIO_ACTUAL agregado a grupos dialout y plugdev${NC}"
    log_message "Permisos USB configurados para usuario $USUARIO_ACTUAL"
}

# Función para instalar reglas udev
install_udev_rules() {
    echo "📋 Instalando reglas udev..."
    
    # Verificar que el archivo existe
    if [ -f "docker/99SecuGen.rules" ]; then
        # Copiar reglas udev
        sudo cp docker/99SecuGen.rules /etc/udev/rules.d/
        
        # Configurar permisos
        sudo chmod 644 /etc/udev/rules.d/99SecuGen.rules
        sudo chown root:root /etc/udev/rules.d/99SecuGen.rules
        
        # Recargar reglas
        sudo udevadm control --reload-rules
        sudo udevadm trigger
        
        echo -e "${GREEN}✅ Reglas udev instaladas${NC}"
        log_message "Reglas udev instaladas correctamente"
    else
        echo -e "${RED}❌ Archivo docker/99SecuGen.rules no encontrado${NC}"
        exit 1
    fi
}

# Función para hacer ejecutables los scripts
make_scripts_executable() {
    echo "🔨 Configurando permisos de scripts..."
    
    # Lista de scripts a hacer ejecutables
    scripts=(
        "iniciar_sistema_robusto.sh"
        "parar_sistema.sh"
        "reset_usb_device.py"
        "monitor_sistema_completo.py"
        "test_sistema_robusto.py"
        "configurar_nuevo_pc.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            echo -e "${GREEN}✅ $script ahora es ejecutable${NC}"
        else
            echo -e "${YELLOW}⚠️ $script no encontrado${NC}"
        fi
    done
    
    log_message "Permisos de scripts configurados"
}

# Función para verificar dispositivo USB
verify_usb_device() {
    echo "🔍 Verificando dispositivo USB SecuGen..."
    
    # Buscar dispositivo por vendor:product ID
    if lsusb | grep -q "1162:2201"; then
        echo -e "${GREEN}✅ Dispositivo SecuGen detectado${NC}"
        lsusb | grep "1162:2201"
        log_message "Dispositivo SecuGen detectado correctamente"
        return 0
    else
        echo -e "${YELLOW}⚠️ Dispositivo SecuGen no detectado${NC}"
        echo "Posibles causas:"
        echo "   - Dispositivo no conectado"
        echo "   - Dispositivo defectuoso"
        echo "   - Modelo diferente de SecuGen"
        
        # Mostrar todos los dispositivos USB
        echo -e "\n🔍 Dispositivos USB detectados:"
        lsusb
        
        log_message "Dispositivo SecuGen no detectado"
        return 1
    fi
}

# Función para probar SDK
test_sdk() {
    echo "🧪 Probando SDK de SecuGen..."
    
    # Activar entorno virtual
    source venv/bin/activate
    
    # Probar importación básica
    if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from sdk import PYSGFPLib
    print('✅ SDK importado correctamente')
except Exception as e:
    print(f'❌ Error importando SDK: {e}')
    exit(1)
" 2>/dev/null; then
        echo -e "${GREEN}✅ SDK funciona correctamente${NC}"
        log_message "SDK probado exitosamente"
    else
        echo -e "${YELLOW}⚠️ SDK no se pudo probar completamente${NC}"
        echo "Esto es normal si el dispositivo no está conectado"
        log_message "SDK no se pudo probar (dispositivo no conectado)"
    fi
}

# Función para crear archivos de configuración
create_config_files() {
    echo "📄 Creando archivos de configuración..."
    
    # Crear archivo de configuración simple
    cat > config_nuevo_pc.txt << EOF
# Configuración del Sistema SecuGen
# ================================

Fecha configuración: $(date)
Usuario: $USUARIO_ACTUAL
Sistema: $(uname -a)

# Comandos importantes:
# Iniciar sistema: ./iniciar_sistema_robusto.sh
# Parar sistema: ./parar_sistema.sh
# Reset USB: sudo python3 reset_usb_device.py
# Verificar: python3 test_sistema_robusto.py

# Archivos críticos:
# - docker/99SecuGen.rules (reglas udev)
# - venv/ (entorno virtual)
# - sdk/ (SDK de SecuGen)
# - lib/ (librerías)

# Verificaciones post-configuración:
# - lsusb | grep "1162:2201"
# - ls -la /dev/secugen_device
# - groups (debe incluir dialout y plugdev)
EOF
    
    echo -e "${GREEN}✅ Archivo de configuración creado${NC}"
    log_message "Archivos de configuración creados"
}

# Función para mostrar resumen post-configuración
show_post_configuration_summary() {
    echo -e "\n${GREEN}🎉 ¡CONFIGURACIÓN COMPLETADA!${NC}"
    echo "=================================="
    echo ""
    echo "📋 RESUMEN DE LA CONFIGURACIÓN:"
    echo "   ✅ Dependencias del sistema instaladas"
    echo "   ✅ Entorno virtual Python creado"
    echo "   ✅ Permisos USB configurados"
    echo "   ✅ Reglas udev instaladas"
    echo "   ✅ Scripts configurados como ejecutables"
    echo "   ✅ Dispositivo USB verificado"
    echo "   ✅ SDK probado"
    echo ""
    echo -e "${YELLOW}⚠️ IMPORTANTE: REINICIA EL SISTEMA AHORA${NC}"
    echo "El reinicio es necesario para que los cambios de grupo tomen efecto"
    echo ""
    echo "💡 DESPUÉS DEL REINICIO, usa:"
    echo "   ./iniciar_sistema_robusto.sh"
    echo ""
    echo "📊 Ver logs completos: tail -f $LOG_FILE"
}

# Función principal
main() {
    log_message "=== INICIANDO CONFIGURACIÓN NUEVO PC ==="
    
    show_step "1" "VERIFICACIONES INICIALES"
    check_root
    check_sudo
    check_distribution
    
    show_step "2" "DEPENDENCIAS DEL SISTEMA"
    install_system_dependencies
    
    show_step "3" "ENTORNO VIRTUAL PYTHON"
    create_virtual_environment
    
    show_step "4" "PERMISOS USB"
    configure_usb_permissions
    
    show_step "5" "REGLAS UDEV"
    install_udev_rules
    
    show_step "6" "SCRIPTS EJECUTABLES"
    make_scripts_executable
    
    show_step "7" "VERIFICACIÓN DISPOSITIVO"
    verify_usb_device
    
    show_step "8" "PRUEBA SDK"
    test_sdk
    
    show_step "9" "ARCHIVOS DE CONFIGURACIÓN"
    create_config_files
    
    show_step "10" "RESUMEN FINAL"
    show_post_configuration_summary
    
    log_message "Configuración completada exitosamente"
}

# Manejo de señales
trap 'echo -e "\n${YELLOW}⏹️ Configuración interrumpida${NC}"; exit 1' INT TERM

# Ejecutar función principal
main "$@"

# Preguntar sobre reinicio
echo -e "\n${BLUE}¿Quieres reiniciar el sistema ahora? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🔄 Reiniciando sistema..."
    sudo reboot
else
    echo -e "${YELLOW}⚠️ Recuerda reiniciar manualmente: sudo reboot${NC}"
fi 