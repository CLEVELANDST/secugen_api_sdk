#!/bin/bash
# Script de comandos para dispositivo persistente SecuGen

echo "🔗 DISPOSITIVO PERSISTENTE SECUGEN - COMANDOS DISPONIBLES"
echo "=========================================================="

echo ""
echo "📱 INFORMACIÓN ACTUAL:"
echo "   Dispositivo persistente: /dev/secugen_device"
if [ -L "/dev/secugen_device" ]; then
    echo "   Apunta a: $(readlink /dev/secugen_device)"
    echo "   Estado: ✅ FUNCIONAL"
else
    echo "   Estado: ❌ NO CONFIGURADO"
fi

echo ""
echo "🚀 COMANDOS PRINCIPALES:"
echo "   sudo ./crear_symlink_persistente.sh       # Crear/configurar symlink"
echo "   ./verificar_dispositivo.sh                # Verificar estado"
echo "   python3 monitor_dispositivo_persistente.py --status  # Estado detallado"

echo ""
echo "🔧 MANTENIMIENTO:"
echo "   sudo python3 reset_usb_device.py          # Reset completo"
echo "   python3 monitor_dispositivo_persistente.py --reset   # Reset específico"
echo "   python3 monitor_dispositivo_persistente.py --recreate # Recrear symlink"

echo ""
echo "📊 MONITOREO:"
echo "   python3 monitor_dispositivo_persistente.py           # Monitoreo continuo"
echo "   python3 monitor_dispositivo_persistente.py --status  # Ver estado"
echo "   tail -f logs/monitor_dispositivo.log                 # Ver logs"

echo ""
echo "🔍 DIAGNÓSTICO:"
echo "   lsusb | grep SecuGen                       # Verificar USB"
echo "   ls -la /dev/secugen_device                 # Verificar symlink"
echo "   cat /etc/udev/rules.d/99SecuGen.rules      # Ver reglas udev"

echo ""
echo "📝 DOCUMENTACIÓN:"
echo "   cat README_DISPOSITIVO_PERSISTENTE.md     # Documentación completa"
echo "   python3 monitor_dispositivo_persistente.py --help    # Ayuda monitor"

echo ""
echo "🎯 PARA USAR EN APLICACIONES:"
echo "   device_path = '/dev/secugen_device'       # Ruta fija en tu código"

echo ""
echo "=========================================================="
echo "¡El dispositivo SecuGen ahora tiene una ruta persistente!" 