#!/bin/bash

# Script para identificar puertos USB disponibles y ayudar a elegir el puerto específico
# para el dispositivo SecuGen

echo "🔍 IDENTIFICADOR DE PUERTOS USB PARA SECUGEN"
echo "============================================"
echo ""

# Función para mostrar información del dispositivo SecuGen si está conectado
show_secugen_info() {
    echo "📱 INFORMACIÓN DEL DISPOSITIVO SECUGEN:"
    echo "========================================"
    
    if lsusb | grep -q "1162:2201"; then
        echo "✅ Estado: CONECTADO"
        
        # Mostrar información de lsusb
        echo ""
        echo "📋 Información básica:"
        lsusb | grep "1162:2201"
        
        # Buscar información detallada del dispositivo
        for device in /sys/bus/usb/devices/*; do
            if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
                vendor=$(cat "$device/idVendor" 2>/dev/null)
                product=$(cat "$device/idProduct" 2>/dev/null)
                
                if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                    device_name=$(basename "$device")
                    busnum=$(cat "$device/busnum" 2>/dev/null)
                    devnum=$(cat "$device/devnum" 2>/dev/null)
                    
                    echo ""
                    echo "📍 Puerto actual: $device_name"
                    echo "📍 Bus: $busnum"
                    echo "📍 Device: $devnum"
                    echo "📍 Ruta completa: /dev/bus/usb/$(printf "%03d" $busnum)/$(printf "%03d" $devnum)"
                    
                    # Información adicional del dispositivo
                    if [[ -f "$device/manufacturer" ]]; then
                        manufacturer=$(cat "$device/manufacturer" 2>/dev/null)
                        echo "🏭 Fabricante: $manufacturer"
                    fi
                    
                    if [[ -f "$device/product" ]]; then
                        product_name=$(cat "$device/product" 2>/dev/null)
                        echo "📦 Producto: $product_name"
                    fi
                    
                    if [[ -f "$device/serial" ]]; then
                        serial=$(cat "$device/serial" 2>/dev/null)
                        echo "🔢 Serie: $serial"
                    fi
                    
                    # Verificar estado de energía
                    if [[ -f "$device/power/autosuspend" ]]; then
                        autosuspend=$(cat "$device/power/autosuspend" 2>/dev/null)
                        echo "⚡ Autosuspend: $autosuspend"
                    fi
                    
                    if [[ -f "$device/power/control" ]]; then
                        power_control=$(cat "$device/power/control" 2>/dev/null)
                        echo "⚡ Control energía: $power_control"
                    fi
                    
                    break
                fi
            fi
        done
    else
        echo "❌ Estado: NO CONECTADO"
        echo ""
        echo "💡 Conecte el dispositivo SecuGen para ver información detallada"
    fi
}

# Función para mostrar topología de puertos USB
show_usb_topology() {
    echo ""
    echo "🌳 TOPOLOGÍA DE PUERTOS USB:"
    echo "============================"
    
    # Mostrar árbol USB si está disponible
    if command -v lsusb &> /dev/null; then
        echo ""
        echo "📊 Árbol USB completo:"
        lsusb -t
        
        echo ""
        echo "📋 Dispositivos USB conectados:"
        lsusb | while read line; do
            # Extraer bus y device
            bus=$(echo "$line" | grep -o "Bus [0-9]*" | cut -d' ' -f2)
            device=$(echo "$line" | grep -o "Device [0-9]*" | cut -d' ' -f2)
            
            # Buscar el puerto correspondiente
            for sysdev in /sys/bus/usb/devices/*; do
                if [[ -f "$sysdev/busnum" && -f "$sysdev/devnum" ]]; then
                    sysbus=$(cat "$sysdev/busnum" 2>/dev/null)
                    sysdevice=$(cat "$sysdev/devnum" 2>/dev/null)
                    
                    if [[ "$sysbus" == "$bus" && "$sysdevice" == "$device" ]]; then
                        device_name=$(basename "$sysdev")
                        echo "   Puerto $device_name: $line"
                        break
                    fi
                fi
            done
        done
    fi
}

# Función para mostrar puertos USB disponibles
show_available_ports() {
    echo ""
    echo "🔌 PUERTOS USB DISPONIBLES:"
    echo "=========================="
    
    # Listar todos los puertos USB del sistema
    echo ""
    echo "📍 Puertos USB identificados:"
    
    for device in /sys/bus/usb/devices/*; do
        device_name=$(basename "$device")
        
        # Filtrar solo puertos reales (formato X-Y o X-Y.Z)
        if [[ $device_name =~ ^[0-9]+-[0-9]+(\.[0-9]+)*$ ]]; then
            # Verificar si hay un dispositivo conectado
            if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
                vendor=$(cat "$device/idVendor" 2>/dev/null)
                product=$(cat "$device/idProduct" 2>/dev/null)
                
                # Obtener información del dispositivo
                device_info=""
                if [[ -f "$device/manufacturer" && -f "$device/product" ]]; then
                    manufacturer=$(cat "$device/manufacturer" 2>/dev/null)
                    product_name=$(cat "$device/product" 2>/dev/null)
                    device_info="$manufacturer $product_name"
                fi
                
                # Marcar si es SecuGen
                if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                    echo "   ✅ $device_name - SecuGen UPx (ACTUAL) - $device_info"
                else
                    echo "   📱 $device_name - $device_info (${vendor}:${product})"
                fi
            else
                echo "   🔌 $device_name - Puerto libre"
            fi
        fi
    done
}

# Función para recomendar puertos
recommend_ports() {
    echo ""
    echo "💡 RECOMENDACIONES:"
    echo "=================="
    
    echo ""
    echo "🎯 Puertos recomendados para SecuGen:"
    echo "   • 1-1 o 1-2: Puertos USB 2.0 del hub raíz (mayor estabilidad)"
    echo "   • 2-1 o 2-2: Puertos USB 3.0 del hub raíz (mayor velocidad)"
    echo "   • Evite puertos con múltiples niveles (ej: 1-2.3.4)"
    echo ""
    echo "⚠️ Consideraciones:"
    echo "   • Use puertos físicos traseros para mayor estabilidad"
    echo "   • Evite hubs USB externos para dispositivos biométricos"
    echo "   • Prefiera puertos de conexión directa a la motherboard"
    echo ""
    echo "🔧 Para configurar un puerto específico:"
    echo "   sudo ./puerto_fijo_simple.sh [puerto]"
    echo "   Ejemplo: sudo ./puerto_fijo_simple.sh 1-2"
}

# Función para generar comandos de configuración
generate_config_commands() {
    echo ""
    echo "📝 COMANDOS DE CONFIGURACIÓN:"
    echo "============================"
    
    echo ""
    echo "🔧 Para configurar diferentes puertos:"
    echo ""
    
    # Listar puertos disponibles como comandos
    for device in /sys/bus/usb/devices/*; do
        device_name=$(basename "$device")
        
        if [[ $device_name =~ ^[0-9]+-[0-9]+$ ]]; then
            # Verificar si hay dispositivo conectado
            if [[ -f "$device/idVendor" && -f "$device/idProduct" ]]; then
                vendor=$(cat "$device/idVendor" 2>/dev/null)
                product=$(cat "$device/idProduct" 2>/dev/null)
                
                if [[ "$vendor" == "1162" && "$product" == "2201" ]]; then
                    echo "   sudo ./puerto_fijo_simple.sh $device_name  # (Puerto actual - SecuGen)"
                else
                    echo "   sudo ./puerto_fijo_simple.sh $device_name  # (Puerto ocupado)"
                fi
            else
                echo "   sudo ./puerto_fijo_simple.sh $device_name  # (Puerto libre)"
            fi
        fi
    done
    
    echo ""
    echo "📋 Comandos de gestión:"
    echo "   secugen-port status     # Ver estado actual"
    echo "   secugen-port relocate   # Reubicar al puerto preferido"
    echo "   secugen-port fix        # Aplicar configuración completa"
}

# Función para mostrar información del sistema
show_system_info() {
    echo ""
    echo "💻 INFORMACIÓN DEL SISTEMA:"
    echo "=========================="
    
    echo ""
    echo "🐧 Sistema operativo:"
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "   $PRETTY_NAME"
    fi
    
    echo ""
    echo "🔌 Controladores USB:"
    lsmod | grep -i usb | head -5
    
    echo ""
    echo "⚡ Estado de energía USB:"
    if [[ -f /sys/module/usbcore/parameters/autosuspend ]]; then
        autosuspend=$(cat /sys/module/usbcore/parameters/autosuspend)
        echo "   Autosuspend global: $autosuspend"
    fi
    
    echo ""
    echo "🔍 Hubs USB detectados:"
    lsusb | grep -i hub | head -3
}

# Función principal
main() {
    show_secugen_info
    show_usb_topology
    show_available_ports
    recommend_ports
    generate_config_commands
    show_system_info
    
    echo ""
    echo "============================================"
    echo "✅ Análisis completado"
    echo ""
    echo "📖 Próximos pasos:"
    echo "1. Identifique el puerto USB deseado de la lista anterior"
    echo "2. Ejecute: sudo ./puerto_fijo_simple.sh [puerto]"
    echo "3. Verifique con: secugen-port status"
    echo ""
    echo "💡 Para ayuda adicional:"
    echo "   ./puerto_fijo_simple.sh          # Configurar puerto por defecto (2-1)"
    echo "   ./fix_puerto_permanente.sh       # Configuración avanzada completa"
    echo "============================================"
}

# Verificar si se ejecuta el script directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 