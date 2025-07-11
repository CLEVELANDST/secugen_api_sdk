#!/bin/bash

# Script para mostrar todos los comandos disponibles del sistema
# de huellas digitales SecuGen

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo "=================================================="
echo -e "${BOLD}🎮 COMANDOS DISPONIBLES - SISTEMA DE HUELLAS DIGITALES${NC}"
echo "=================================================="
echo ""

echo -e "${CYAN}📋 CONFIGURACIÓN INICIAL${NC}"
echo "  ./pre_production_check.sh    # Verificar que todo esté listo"
echo "  ./setup_production.sh        # Configurar para producción"
echo ""

echo -e "${CYAN}🚀 ADMINISTRACIÓN DE LA APLICACIÓN${NC}"
echo "  ./start_production.sh        # Iniciar aplicación"
echo "  ./stop_production.sh         # Parar aplicación"
echo "  ./restart_production.sh      # Reiniciar aplicación"
echo "  ./status_production.sh       # Ver estado completo"
echo ""

echo -e "${CYAN}🔧 SERVICIOS SYSTEMD${NC}"
echo "  sudo systemctl start secugen-fingerprint-api     # Iniciar servicio"
echo "  sudo systemctl stop secugen-fingerprint-api      # Parar servicio"
echo "  sudo systemctl restart secugen-fingerprint-api   # Reiniciar servicio"
echo "  sudo systemctl status secugen-fingerprint-api    # Ver estado"
echo "  sudo systemctl enable secugen-fingerprint-api    # Habilitar auto-inicio"
echo "  sudo systemctl disable secugen-fingerprint-api   # Deshabilitar auto-inicio"
echo ""

echo -e "${CYAN}📊 MONITOREO Y LOGS${NC}"
echo "  ./monitor_production.sh      # Monitorear sistema manualmente"
echo "  tail -f logs/app.log         # Ver logs de la aplicación"
echo "  tail -f logs/startup.log     # Ver logs de inicio"
echo "  tail -f logs/monitor.log     # Ver logs de monitoreo"
echo "  sudo journalctl -u secugen-fingerprint-api -f   # Logs systemd en tiempo real"
echo ""

echo -e "${CYAN}💾 BACKUP Y RECUPERACIÓN${NC}"
echo "  ./backup_production.sh       # Crear backup manual"
echo "  ls -la backups/              # Ver backups disponibles"
echo "  tar -xzf backups/backup_*.tar.gz  # Restaurar backup"
echo ""

echo -e "${CYAN}🧪 PRUEBAS DE STRESS${NC}"
echo "  python3 simple_stress_test.py      # Prueba básica (recomendada)"
echo "  python3 run_stress_test.py         # Prueba intensa automática"
echo "  python3 extreme_stress_test.py     # Prueba extrema con concurrencia"
echo ""

echo -e "${CYAN}🔍 DIAGNÓSTICO${NC}"
echo "  curl -X POST http://localhost:5000/initialize    # Probar API"
echo "  curl -X POST -d '{\"state\":true}' -H 'Content-Type: application/json' http://localhost:5000/led"
echo "  lsusb | grep -i secugen      # Verificar dispositivo USB"
echo "  ps aux | grep python3        # Ver procesos Python"
echo "  netstat -tuln | grep 5000    # Verificar puerto"
echo ""

echo -e "${CYAN}⚙️ CONFIGURACIÓN${NC}"
echo "  nano config/production.env   # Editar configuración"
echo "  crontab -l                   # Ver tareas programadas"
echo "  crontab -e                   # Editar tareas programadas"
echo "  groups                       # Ver grupos del usuario"
echo "  ls -la /etc/udev/rules.d/99SecuGen.rules  # Ver reglas USB"
echo ""

echo -e "${CYAN}🛠️ MANTENIMIENTO${NC}"
echo "  sudo apt update && sudo apt upgrade  # Actualizar sistema"
echo "  source venv/bin/activate && pip install --upgrade pip  # Actualizar pip"
echo "  sudo udevadm control --reload-rules && sudo udevadm trigger  # Recargar reglas USB"
echo "  sudo usermod -a -G plugdev \$USER   # Agregar usuario a grupo plugdev"
echo ""

echo -e "${CYAN}📁 ARCHIVOS IMPORTANTES${NC}"
echo "  app.py                       # Aplicación principal"
echo "  config/production.env        # Configuración de producción"
echo "  logs/                        # Directorio de logs"
echo "  backups/                     # Directorio de backups"
echo "  venv/                        # Entorno virtual Python"
echo "  PRODUCTION_SETUP.md          # Documentación completa"
echo ""

echo -e "${YELLOW}💡 COMANDOS ÚTILES COMBINADOS${NC}"
echo ""
echo -e "${GREEN}# Verificar estado completo del sistema${NC}"
echo "  ./status_production.sh && lsusb | grep -i secugen"
echo ""
echo -e "${GREEN}# Reiniciar todo el sistema${NC}"
echo "  ./restart_production.sh && sleep 5 && ./status_production.sh"
echo ""
echo -e "${GREEN}# Hacer backup y reiniciar${NC}"
echo "  ./backup_production.sh && ./restart_production.sh"
echo ""
echo -e "${GREEN}# Ejecutar prueba de stress después de reiniciar${NC}"
echo "  ./restart_production.sh && sleep 5 && python3 simple_stress_test.py"
echo ""
echo -e "${GREEN}# Verificar logs de las últimas 24 horas${NC}"
echo "  sudo journalctl -u secugen-fingerprint-api --since '1 day ago'"
echo ""

echo "=================================================="
echo -e "${BOLD}🎯 INICIO RÁPIDO PARA PRODUCCIÓN${NC}"
echo "=================================================="
echo ""
echo -e "${GREEN}1. Verificar sistema:${NC}        ./pre_production_check.sh"
echo -e "${GREEN}2. Configurar producción:${NC}    ./setup_production.sh"
echo -e "${GREEN}3. Iniciar aplicación:${NC}       ./start_production.sh"
echo -e "${GREEN}4. Verificar estado:${NC}         ./status_production.sh"
echo -e "${GREEN}5. Probar API:${NC}               curl -X POST http://localhost:5000/initialize"
echo ""
echo "=================================================="
echo -e "${BOLD}📖 Para más información: cat PRODUCTION_SETUP.md${NC}"
echo "==================================================" 