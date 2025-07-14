#!/bin/bash

check_device() {
    local vendor_id="1162"
    local product_id="2201"
    local device_found=false

    echo "Verificando dispositivo SecuGen..."
    
    # Verificar si el dispositivo está presente
    if lsusb | grep -q "ID ${vendor_id}:${product_id}"; then
        echo "✓ Dispositivo SecuGen encontrado"
        device_found=true
    else
        echo "✗ Dispositivo SecuGen no encontrado"
        return 1
    fi

    # Verificar permisos USB
    if [ -d "/dev/bus/usb" ]; then
        echo "✓ Directorio USB presente"
        if ls -l /dev/bus/usb/*/* | grep -q "plugdev"; then
            echo "✓ Permisos USB correctos"
        else
            echo "✗ Permisos USB incorrectos"
            return 1
        fi
    else
        echo "✗ Directorio USB no encontrado"
        return 1
    fi

    # Verificar bibliotecas
    if ldconfig -p | grep -q "libsgfplib"; then
        echo "✓ Bibliotecas SecuGen encontradas"
    else
        echo "✗ Bibliotecas SecuGen no encontradas"
        return 1
    fi

    return 0
}

check_device 