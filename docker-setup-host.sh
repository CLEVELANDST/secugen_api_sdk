#!/bin/bash

# DOCKER SETUP HOST - Configuración automática del host
# =====================================================
# Este script configura el host para que Docker funcione
# correctamente con el dispositivo USB SecuGen

echo "🐳 CONFIGURACIÓN DEL HOST PARA DOCKER SECUGEN"
echo "=============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
LOG_FILE="logs/docker_setup_host.log"
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

# Función para verificar Docker
check_docker() {
    echo "🐳 Verificando Docker..."
    
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}⚠️ Docker no está instalado${NC}"
        echo "🔧 Instalando Docker..."
        
        # Instalar Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
        
        # Agregar usuario al grupo docker
        sudo usermod -aG docker "$USUARIO_ACTUAL"
        
        echo -e "${GREEN}✅ Docker instalado${NC}"
        log_message "Docker instalado correctamente"
    else
        echo -e "${GREEN}✅ Docker ya está instalado${NC}"
        log_message "Docker ya está disponible"
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}⚠️ Docker Compose no está instalado${NC}"
        echo "🔧 Instalando Docker Compose..."
        
        # Instalar Docker Compose
        sudo apt update
        sudo apt install -y docker-compose
        
        echo -e "${GREEN}✅ Docker Compose instalado${NC}"
        log_message "Docker Compose instalado correctamente"
    else
        echo -e "${GREEN}✅ Docker Compose ya está instalado${NC}"
        log_message "Docker Compose ya está disponible"
    fi
}

# Función para verificar dispositivo USB
verify_usb_device() {
    echo "🔍 Verificando dispositivo USB SecuGen..."
    
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

# Función para instalar reglas udev
install_udev_rules() {
    echo "📋 Configurando reglas udev..."
    
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
    
    # Configurar permisos para Docker
    sudo usermod -a -G docker "$USUARIO_ACTUAL"
    
    echo -e "${GREEN}✅ Permisos USB configurados${NC}"
    log_message "Permisos USB configurados para $USUARIO_ACTUAL"
}

# Función para crear directorios necesarios
create_directories() {
    echo "📁 Creando directorios necesarios..."
    
    # Crear directorios con permisos correctos
    mkdir -p logs templates backups
    
    # Configurar permisos
    chmod 755 logs templates backups
    
    echo -e "${GREEN}✅ Directorios creados${NC}"
    log_message "Directorios creados correctamente"
}

# Función para configurar firewall
configure_firewall() {
    echo "🔥 Configurando firewall..."
    
    # Verificar si ufw está instalado
    if command -v ufw &> /dev/null; then
        # Permitir puerto 5000 para Flask
        sudo ufw allow 5000/tcp
        
        echo -e "${GREEN}✅ Firewall configurado${NC}"
        log_message "Firewall configurado para puerto 5000"
    else
        echo -e "${YELLOW}⚠️ UFW no está instalado${NC}"
        log_message "UFW no está disponible"
    fi
}

# Función para crear archivos de configuración
create_docker_config() {
    echo "📄 Creando configuración de Docker..."
    
    # Crear archivo de configuración
    cat > docker-config.txt << EOF
# Configuración Docker SecuGen
# ============================

Fecha configuración: $(date)
Usuario: $USUARIO_ACTUAL
Docker: $(docker --version 2>/dev/null || echo "No instalado")
Docker Compose: $(docker-compose --version 2>/dev/null || echo "No instalado")

# Comandos Docker:
# Construir: docker-compose build
# Iniciar: docker-compose up -d
# Parar: docker-compose down
# Logs: docker-compose logs -f
# Estado: docker-compose ps

# Comandos de contenedor:
# Acceder: docker exec -it secugen-fingerprint-api bash
# Reiniciar: docker-compose restart
# Limpiar: docker system prune -a

# Verificaciones:
# - lsusb | grep "1162:2201" (dispositivo)
# - docker ps (contenedores)
# - curl -X POST http://localhost:5000/initialize (API)
EOF
    
    echo -e "${GREEN}✅ Configuración de Docker creada${NC}"
    log_message "Configuración de Docker creada"
}

# Función para verificar instalación
verify_installation() {
    echo "✅ Verificando instalación..."
    
    # Verificar Docker
    if docker --version >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker funciona${NC}"
    else
        echo -e "${RED}❌ Docker no funciona${NC}"
        return 1
    fi
    
    # Verificar Docker Compose
    if docker-compose --version >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker Compose funciona${NC}"
    else
        echo -e "${RED}❌ Docker Compose no funciona${NC}"
        return 1
    fi
    
    # Verificar grupos de usuario
    if groups "$USUARIO_ACTUAL" | grep -q "docker"; then
        echo -e "${GREEN}✅ Usuario en grupo docker${NC}"
    else
        echo -e "${YELLOW}⚠️ Usuario no en grupo docker${NC}"
        echo "Será necesario reiniciar sesión o reboot"
    fi
    
    # Verificar reglas udev
    if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
        echo -e "${GREEN}✅ Reglas udev instaladas${NC}"
    else
        echo -e "${RED}❌ Reglas udev no instaladas${NC}"
        return 1
    fi
    
    log_message "Verificación completada"
    return 0
}

# Función para mostrar resumen
show_summary() {
    echo -e "\n${GREEN}🎉 ¡CONFIGURACIÓN DEL HOST COMPLETADA!${NC}"
    echo "======================================"
    echo ""
    echo "📋 RESUMEN DE LA CONFIGURACIÓN:"
    echo "   ✅ Docker instalado y configurado"
    echo "   ✅ Docker Compose instalado"
    echo "   ✅ Reglas udev instaladas"
    echo "   ✅ Permisos USB configurados"
    echo "   ✅ Directorios creados"
    echo "   ✅ Firewall configurado"
    echo ""
    echo "🐳 PRÓXIMOS PASOS:"
    echo "   1. Reiniciar sesión o reboot (para grupos de usuario)"
    echo "   2. Ejecutar: docker-compose up -d"
    echo "   3. Verificar: curl -X POST http://localhost:5000/initialize"
    echo ""
    echo "🔧 COMANDOS ÚTILES:"
    echo "   docker-compose up -d      # Iniciar contenedores"
    echo "   docker-compose down       # Parar contenedores"
    echo "   docker-compose logs -f    # Ver logs"
    echo "   docker-compose ps         # Ver estado"
    echo ""
    echo "📊 Ver logs: tail -f $LOG_FILE"
}

# Función principal
main() {
    log_message "=== INICIANDO CONFIGURACIÓN HOST DOCKER ==="
    
    show_step "1" "VERIFICACIONES INICIALES"
    check_root
    check_sudo
    
    show_step "2" "VERIFICACIÓN/INSTALACIÓN DOCKER"
    check_docker
    
    show_step "3" "VERIFICACIÓN DISPOSITIVO USB"
    verify_usb_device
    
    show_step "4" "REGLAS UDEV"
    install_udev_rules
    
    show_step "5" "PERMISOS USB"
    configure_usb_permissions
    
    show_step "6" "DIRECTORIOS"
    create_directories
    
    show_step "7" "FIREWALL"
    configure_firewall
    
    show_step "8" "CONFIGURACIÓN DOCKER"
    create_docker_config
    
    show_step "9" "VERIFICACIÓN"
    verify_installation
    
    show_step "10" "RESUMEN"
    show_summary
    
    log_message "Configuración del host completada exitosamente"
}

# Manejo de señales
trap 'echo -e "\n${YELLOW}⏹️ Configuración interrumpida${NC}"; exit 1' INT TERM

# Ejecutar función principal
main "$@"

# Preguntar sobre reinicio
echo -e "\n${BLUE}¿Quieres reiniciar sesión ahora para aplicar cambios de grupos? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🔄 Cerrando sesión..."
    gnome-session-quit --logout --no-prompt 2>/dev/null || pkill -KILL -u "$USUARIO_ACTUAL"
else
    echo -e "${YELLOW}⚠️ Recuerda reiniciar sesión o hacer reboot antes de usar Docker${NC}"
fi 