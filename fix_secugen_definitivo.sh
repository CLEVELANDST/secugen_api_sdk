#!/bin/bash

echo "🔧 ESTABILIZACIÓN DEFINITIVA SECUGEN - INICIANDO"
echo "================================================="

# 1. Limpiar procesos Flask
echo "1️⃣ Limpiando procesos Flask..."
pkill -f "python3 app.py" 2>/dev/null || true
sleep 1

# 2. Verificar dispositivo
echo "2️⃣ Verificando dispositivo SecuGen..."
DEVICE_INFO=$(lsusb | grep -i "1162:2201" | head -1)
if [ -z "$DEVICE_INFO" ]; then
    echo "❌ ERROR: Dispositivo SecuGen no encontrado"
    exit 1
fi

echo "✅ Dispositivo encontrado: $DEVICE_INFO"
BUS=$(echo "$DEVICE_INFO" | cut -d' ' -f2)
DEVICE=$(echo "$DEVICE_INFO" | cut -d' ' -f4 | cut -d':' -f1)
echo "📍 Ubicación: Bus $BUS Device $DEVICE"

# 3. Crear regla udev específica
echo "3️⃣ Creando regla udev específica..."
sudo tee /etc/udev/rules.d/99-secugen-definitivo.rules > /dev/null << 'EOF'
# SecuGen USB UPx - Regla definitiva
SUBSYSTEM=="usb", ATTRS{idVendor}=="1162", ATTRS{idProduct}=="2201", \
    MODE="0666", GROUP="plugdev", \
    SYMLINK+="secugen_device", \
    RUN+="/bin/bash -c 'echo on > /sys/bus/usb/devices/%k/power/level'", \
    RUN+="/bin/bash -c 'echo -1 > /sys/bus/usb/devices/%k/power/autosuspend_delay_ms'"

# Desactivar HID para SecuGen
SUBSYSTEM=="usb", ATTRS{idVendor}=="1162", ATTRS{idProduct}=="2201", \
    DRIVER=="usbhid", \
    RUN+="/bin/bash -c 'echo %k > /sys/bus/usb/drivers/usbhid/unbind'"
EOF

# 4. Recargar reglas udev
echo "4️⃣ Recargando reglas udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# 5. Configurar power management
echo "5️⃣ Configurando power management..."
DEVICE_PATH="/sys/bus/usb/devices/$BUS-*"
for path in $DEVICE_PATH; do
    if [ -d "$path" ]; then
        echo "📝 Configurando $path..."
        sudo bash -c "echo on > $path/power/level" 2>/dev/null || true
        sudo bash -c "echo -1 > $path/power/autosuspend_delay_ms" 2>/dev/null || true
        sudo bash -c "echo disabled > $path/power/wakeup" 2>/dev/null || true
    fi
done

# 6. Reiniciar módulos USB
echo "6️⃣ Reiniciando módulos USB..."
sudo modprobe -r usbhid
sleep 1
sudo modprobe usbhid

# 7. Desvincular de HID si está vinculado
echo "7️⃣ Desvinculando de HID..."
sudo bash -c "echo '1162:2201' > /sys/bus/usb/drivers/usbhid/unbind" 2>/dev/null || echo "   Device not bound to HID"

# 8. Verificar permisos
echo "8️⃣ Verificando permisos..."
USB_DEVICE_PATH="/dev/bus/usb/$BUS/$DEVICE"
if [ -c "$USB_DEVICE_PATH" ]; then
    sudo chmod 666 "$USB_DEVICE_PATH"
    echo "✅ Permisos configurados: $(ls -la $USB_DEVICE_PATH)"
else
    echo "⚠️  Dispositivo no encontrado en: $USB_DEVICE_PATH"
fi

# 9. Configurar kernel parameters
echo "9️⃣ Configurando parámetros del kernel..."
echo 'usbcore.autosuspend=-1' | sudo tee -a /etc/default/grub.d/usb-autosuspend.conf > /dev/null 2>&1 || true

# 10. Verificar estabilidad
echo "🔟 Verificando estabilidad..."
sleep 2
FINAL_CHECK=$(lsusb | grep -i "1162:2201")
if [ ! -z "$FINAL_CHECK" ]; then
    echo "✅ Dispositivo estable: $FINAL_CHECK"
else
    echo "❌ ERROR: Dispositivo no estable"
    exit 1
fi

echo ""
echo "🎉 ESTABILIZACIÓN COMPLETADA EXITOSAMENTE"
echo "========================================="
echo "📍 Dispositivo: $FINAL_CHECK"
echo "📁 Permisos: $(ls -la $USB_DEVICE_PATH 2>/dev/null || echo 'N/A')"
echo "🔗 Symlink: $(ls -la /dev/secugen_device 2>/dev/null || echo 'N/A')"
echo ""
echo "🚀 Ahora puede ejecutar: python3 app.py" 