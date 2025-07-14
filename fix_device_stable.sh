#!/bin/bash

echo "🔧 SCRIPT PARA ESTABILIZAR DISPOSITIVO SECUGEN"
echo "============================================="

# 1. Matar aplicación Flask
echo "1. Matando aplicación Flask..."
pkill -f "python3 app.py"
sleep 2

# 2. Verificar que el dispositivo esté presente
echo "2. Verificando dispositivo SecuGen..."
if lsusb | grep -i secugen > /dev/null; then
    echo "✅ Dispositivo SecuGen encontrado"
    lsusb | grep -i secugen
else
    echo "❌ Dispositivo SecuGen NO encontrado"
    exit 1
fi

# 3. Reiniciar módulos USB HID
echo "3. Reiniciando módulos USB HID..."
sudo modprobe -r usbhid
sleep 1
sudo modprobe usbhid
sleep 2

# 4. Recargar reglas udev
echo "4. Recargando reglas udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger
sleep 2

# 5. Verificar symlink estable
echo "5. Verificando symlink estable..."
if ls -la /dev/secugen_device > /dev/null 2>&1; then
    echo "✅ Symlink estable creado:"
    ls -la /dev/secugen_device
else
    echo "⚠️ Symlink no encontrado, pero continuando..."
fi

# 6. Desactivar autosuspensión USB
echo "6. Desactivando autosuspensión USB..."
# Buscar el dispositivo USB correcto
USB_DEVICE=$(lsusb | grep -i secugen | cut -d' ' -f4 | cut -d':' -f1)
if [ ! -z "$USB_DEVICE" ]; then
    # Encontrar el path correcto del dispositivo
    for usb_path in /sys/bus/usb/devices/*/idVendor; do
        if [ -f "$usb_path" ] && [ "$(cat $usb_path)" = "1162" ]; then
            device_path=$(dirname $usb_path)
            echo "Found device path: $device_path"
            
            # Desactivar autosuspensión
            if [ -f "$device_path/power/autosuspend_delay_ms" ]; then
                echo -1 | sudo tee "$device_path/power/autosuspend_delay_ms" > /dev/null
            fi
            if [ -f "$device_path/power/control" ]; then
                echo on | sudo tee "$device_path/power/control" > /dev/null
            fi
            echo "✅ Autosuspensión desactivada"
            break
        fi
    done
fi

# 7. Verificar dispositivo final
echo "7. Verificación final del dispositivo..."
if lsusb | grep -i secugen > /dev/null; then
    echo "✅ Dispositivo SecuGen estable:"
    lsusb | grep -i secugen
else
    echo "❌ Dispositivo SecuGen perdido"
    exit 1
fi

echo ""
echo "🎉 DISPOSITIVO ESTABILIZADO CORRECTAMENTE"
echo "========================================="
echo "Ahora puede iniciar la aplicación Flask:"
echo "python3 app.py"
echo "" 