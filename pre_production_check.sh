#!/bin/bash

# Script de Verificación Pre-Producción
# Verifica que todo esté listo antes de ejecutar setup_production.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Función para logging
log_success() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
    ((CHECKS_PASSED++))
}

log_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
    ((CHECKS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[⚠️  WARN]${NC} $1"
    ((CHECKS_WARNING++))
}

log_info() {
    echo -e "${BLUE}[ℹ️  INFO]${NC} $1"
}

# Función para verificar archivos principales
check_main_files() {
    log_info "Verificando archivos principales..."
    
    local required_files=(
        "app.py"
        "sdk/__init__.py"
        "sdk/pysgfplib.py"
        "lib/linux3/libpysgfplib.so"
        "venv/bin/activate"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "Archivo requerido encontrado: $file"
        else
            log_error "Archivo requerido no encontrado: $file"
        fi
    done
}

# Función para verificar Python y dependencias
check_python_environment() {
    log_info "Verificando entorno Python..."
    
    # Verificar Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python 3 instalado: $PYTHON_VERSION"
    else
        log_error "Python 3 no está instalado"
    fi
    
    # Verificar pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 disponible"
    else
        log_error "pip3 no está instalado"
    fi
    
    # Verificar entorno virtual
    if [ -f "venv/bin/activate" ]; then
        log_success "Entorno virtual encontrado"
        
        # Verificar dependencias en venv
        source venv/bin/activate
        if python3 -c "import flask" 2>/dev/null; then
            log_success "Flask instalado en venv"
        else
            log_warning "Flask no encontrado en venv"
        fi
        
        if python3 -c "import usb" 2>/dev/null; then
            log_success "PyUSB instalado en venv"
        else
            log_warning "PyUSB no encontrado en venv"
        fi
        
        if python3 -c "import requests" 2>/dev/null; then
            log_success "Requests instalado en venv"
        else
            log_warning "Requests no encontrado en venv"
        fi
    else
        log_error "Entorno virtual no encontrado"
    fi
}

# Función para verificar dependencias del sistema
check_system_dependencies() {
    log_info "Verificando dependencias del sistema..."
    
    # Verificar distribución
    if command -v apt-get &> /dev/null; then
        log_success "Sistema basado en Debian/Ubuntu detectado"
    else
        log_error "Sistema no es compatible (necesita apt-get)"
    fi
    
    # Verificar libusb
    if dpkg -l | grep -q libusb-0.1-4; then
        log_success "libusb-0.1-4 instalado"
    else
        log_warning "libusb-0.1-4 no está instalado"
    fi
    
    # Verificar herramientas de desarrollo
    if command -v gcc &> /dev/null; then
        log_success "GCC disponible"
    else
        log_warning "GCC no está instalado"
    fi
    
    # Verificar git
    if command -v git &> /dev/null; then
        log_success "Git disponible"
    else
        log_warning "Git no está instalado"
    fi
    
    # Verificar curl
    if command -v curl &> /dev/null; then
        log_success "curl disponible"
    else
        log_warning "curl no está instalado"
    fi
    
    # Verificar systemd
    if command -v systemctl &> /dev/null; then
        log_success "systemd disponible"
    else
        log_error "systemd no está disponible"
    fi
}

# Función para verificar dispositivo USB
check_usb_device() {
    log_info "Verificando dispositivo USB..."
    
    # Verificar que lsusb esté disponible
    if command -v lsusb &> /dev/null; then
        log_success "lsusb disponible"
        
        # Verificar dispositivo SecuGen
        if lsusb | grep -i secugen > /dev/null; then
            DEVICE_INFO=$(lsusb | grep -i secugen)
            log_success "Dispositivo SecuGen detectado: $DEVICE_INFO"
        else
            log_warning "Dispositivo SecuGen no detectado (puede estar desconectado)"
        fi
    else
        log_error "lsusb no está disponible"
    fi
}

# Función para verificar permisos
check_permissions() {
    log_info "Verificando permisos..."
    
    # Verificar grupo plugdev
    if groups | grep -q plugdev; then
        log_success "Usuario está en grupo plugdev"
    else
        log_warning "Usuario no está en grupo plugdev (se configurará automáticamente)"
    fi
    
    # Verificar reglas udev
    if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
        log_success "Reglas udev ya configuradas"
    else
        log_warning "Reglas udev no configuradas (se configurarán automáticamente)"
    fi
    
    # Verificar permisos del directorio
    if [ -w "." ]; then
        log_success "Permisos de escritura en directorio actual"
    else
        log_error "Sin permisos de escritura en directorio actual"
    fi
}

# Función para verificar red
check_network() {
    log_info "Verificando conectividad de red..."
    
    # Verificar conexión a internet
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        log_success "Conexión a internet disponible"
    else
        log_warning "Sin conexión a internet (necesaria para instalar paquetes)"
    fi
    
    # Verificar repositorios de Ubuntu
    if curl -s http://archive.ubuntu.com > /dev/null 2>&1; then
        log_success "Repositorios de Ubuntu accesibles"
    else
        log_warning "Repositorios de Ubuntu no accesibles"
    fi
}

# Función para verificar espacio en disco
check_disk_space() {
    log_info "Verificando espacio en disco..."
    
    # Verificar espacio disponible
    AVAILABLE_SPACE=$(df -h . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "${AVAILABLE_SPACE%.*}" -gt 1 ]; then
        log_success "Espacio disponible suficiente: ${AVAILABLE_SPACE}"
    else
        log_warning "Espacio en disco limitado: ${AVAILABLE_SPACE}"
    fi
}

# Función para verificar puertos
check_ports() {
    log_info "Verificando puertos..."
    
    # Verificar puerto 5000
    if netstat -tuln 2>/dev/null | grep ":5000 " > /dev/null; then
        log_warning "Puerto 5000 está en uso"
    else
        log_success "Puerto 5000 está libre"
    fi
    
    # Verificar que netstat esté disponible
    if command -v netstat &> /dev/null; then
        log_success "netstat disponible"
    else
        log_warning "netstat no está disponible"
    fi
}

# Función para verificar aplicación actual
check_current_app() {
    log_info "Verificando aplicación actual..."
    
    # Verificar si app.py se puede cargar
    if python3 -c "import sys; sys.path.insert(0, '.'); import app" 2>/dev/null; then
        log_success "app.py se puede cargar sin errores"
    else
        log_warning "app.py tiene errores de importación"
    fi
    
    # Verificar si hay procesos de la aplicación corriendo
    if pgrep -f "python3 app.py" > /dev/null; then
        log_warning "Aplicación ya está corriendo"
    else
        log_success "No hay aplicación corriendo actualmente"
    fi
}

# Función para verificar scripts de test
check_test_scripts() {
    log_info "Verificando scripts de test..."
    
    local test_scripts=(
        "simple_stress_test.py"
        "run_stress_test.py"
        "extreme_stress_test.py"
    )
    
    for script in "${test_scripts[@]}"; do
        if [ -f "$script" ]; then
            log_success "Script de test encontrado: $script"
        else
            log_warning "Script de test no encontrado: $script"
        fi
    done
}

# Función para mostrar resumen
show_summary() {
    echo ""
    echo "=================================================="
    echo "📋 RESUMEN DE VERIFICACIÓN PRE-PRODUCCIÓN"
    echo "=================================================="
    echo -e "${GREEN}✅ Verificaciones exitosas: $CHECKS_PASSED${NC}"
    echo -e "${YELLOW}⚠️  Advertencias: $CHECKS_WARNING${NC}"
    echo -e "${RED}❌ Verificaciones fallidas: $CHECKS_FAILED${NC}"
    echo ""
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 SISTEMA LISTO PARA PRODUCCIÓN${NC}"
        echo ""
        echo "✅ Todos los componentes críticos están disponibles"
        echo "✅ Se puede proceder con la configuración de producción"
        echo ""
        echo "📋 SIGUIENTE PASO:"
        echo "   ./setup_production.sh"
        echo ""
    elif [ $CHECKS_FAILED -le 2 ]; then
        echo -e "${YELLOW}⚠️  SISTEMA PARCIALMENTE LISTO${NC}"
        echo ""
        echo "⚠️  Hay algunos problemas menores que pueden ser corregidos automáticamente"
        echo "⚠️  Se recomienda proceder con precaución"
        echo ""
        echo "📋 OPCIONES:"
        echo "   1. Ejecutar: ./setup_production.sh"
        echo "   2. Corregir problemas manualmente y volver a verificar"
        echo ""
    else
        echo -e "${RED}❌ SISTEMA NO LISTO PARA PRODUCCIÓN${NC}"
        echo ""
        echo "❌ Hay problemas críticos que deben ser corregidos"
        echo "❌ NO se recomienda proceder con la configuración"
        echo ""
        echo "📋 ACCIONES REQUERIDAS:"
        echo "   1. Corregir los problemas identificados"
        echo "   2. Ejecutar este script nuevamente"
        echo "   3. Una vez resueltos, ejecutar: ./setup_production.sh"
        echo ""
    fi
}

# Función principal
main() {
    echo "=================================================="
    echo "🔍 VERIFICACIÓN PRE-PRODUCCIÓN"
    echo "   Sistema de Huellas Digitales SecuGen"
    echo "=================================================="
    echo ""
    
    # Ejecutar todas las verificaciones
    check_main_files
    echo ""
    check_python_environment
    echo ""
    check_system_dependencies
    echo ""
    check_usb_device
    echo ""
    check_permissions
    echo ""
    check_network
    echo ""
    check_disk_space
    echo ""
    check_ports
    echo ""
    check_current_app
    echo ""
    check_test_scripts
    echo ""
    
    # Mostrar resumen
    show_summary
    
    # Código de salida basado en el número de fallos
    if [ $CHECKS_FAILED -eq 0 ]; then
        exit 0
    elif [ $CHECKS_FAILED -le 2 ]; then
        exit 1
    else
        exit 2
    fi
}

# Verificar que el script se ejecute desde el directorio correcto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ ERROR: Este script debe ejecutarse desde el directorio del proyecto${NC}"
    echo "   Debe existir el archivo 'app.py' en el directorio actual"
    exit 1
fi

# Ejecutar función principal
main "$@" 