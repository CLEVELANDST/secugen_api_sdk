#!/usr/bin/env python3
"""
IDENTIFICADOR PERSISTENTE PARA DISPOSITIVO SECUGEN
=================================================
Script para identificar y configurar un identificador persistente
para el lector de huellas SecuGen, evitando cambios en /dev/bus/usb/
"""

import os
import subprocess
import glob
import time
import sys
from pathlib import Path

# Configuración del dispositivo
SECUGEN_CONFIG = {
    'vendor_id': '1162',
    'product_id': '2201',
    'device_name': 'SecuGen',
    'persistent_symlink': '/dev/secugen_device',
    'udev_rules_path': '/etc/udev/rules.d/99SecuGen.rules',
    'project_rules_path': 'docker/99SecuGen.rules'
}

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n{title}")
    print("-" * 40)

def run_command(cmd, show_output=True):
    """Ejecutar comando y retornar resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if show_output:
            print(f"💻 {cmd}")
            if result.stdout:
                print(f"📝 {result.stdout.strip()}")
            if result.stderr and result.returncode != 0:
                print(f"⚠️ {result.stderr.strip()}")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        if show_output:
            print(f"❌ Error: {e}")
        return False, "", str(e)

def get_device_info():
    """Obtener información completa del dispositivo"""
    print_section("📱 INFORMACIÓN DEL DISPOSITIVO")
    
    device_info = {
        'found': False,
        'methods': {}
    }
    
    # Método 1: lsusb
    print("🔍 Método 1: lsusb")
    success, output, _ = run_command(f"lsusb | grep '{SECUGEN_CONFIG['vendor_id']}:{SECUGEN_CONFIG['product_id']}'", 
                                    show_output=False)
    
    if success and output:
        device_info['found'] = True
        device_info['methods']['lsusb'] = output.strip()
        
        # Extraer bus y device
        parts = output.strip().split()
        if len(parts) >= 4:
            bus = parts[1]
            device = parts[3].rstrip(':')
            device_info['bus'] = bus
            device_info['device'] = device
            device_info['usb_path'] = f"/dev/bus/usb/{bus}/{device}"
            
            print(f"✅ Bus: {bus}, Device: {device}")
            print(f"✅ Path USB: {device_info['usb_path']}")
    else:
        print("❌ No encontrado por lsusb")
    
    # Método 2: sysfs
    print("\n🗂️ Método 2: sysfs")
    sysfs_found = False
    
    for device_path in glob.glob('/sys/bus/usb/devices/*'):
        try:
            vendor_file = os.path.join(device_path, 'idVendor')
            product_file = os.path.join(device_path, 'idProduct')
            
            if os.path.exists(vendor_file) and os.path.exists(product_file):
                with open(vendor_file, 'r') as f:
                    vendor = f.read().strip()
                with open(product_file, 'r') as f:
                    product = f.read().strip()
                
                if vendor == SECUGEN_CONFIG['vendor_id'] and product == SECUGEN_CONFIG['product_id']:
                    device_info['found'] = True
                    device_info['sysfs_path'] = device_path
                    device_info['methods']['sysfs'] = device_path
                    sysfs_found = True
                    
                    print(f"✅ Sysfs path: {device_path}")
                    
                    # Información adicional
                    try:
                        info_files = ['busnum', 'devnum', 'serial', 'manufacturer', 'product']
                        for info_file in info_files:
                            info_path = os.path.join(device_path, info_file)
                            if os.path.exists(info_path):
                                with open(info_path, 'r') as f:
                                    value = f.read().strip()
                                    if value:
                                        device_info[info_file] = value
                                        print(f"   {info_file}: {value}")
                    except:
                        pass
                    break
        except Exception as e:
            continue
    
    if not sysfs_found:
        print("❌ No encontrado en sysfs")
    
    # Método 3: Verificar symlink persistente
    print("\n🔗 Método 3: Symlink persistente")
    if os.path.exists(SECUGEN_CONFIG['persistent_symlink']):
        try:
            target = os.readlink(SECUGEN_CONFIG['persistent_symlink'])
            device_info['symlink_target'] = target
            device_info['methods']['symlink'] = target
            print(f"✅ Symlink: {SECUGEN_CONFIG['persistent_symlink']} -> {target}")
            
            # Verificar que el target existe
            if os.path.exists(target):
                print(f"✅ Target existe: {target}")
            else:
                print(f"⚠️ Target no existe: {target}")
                
        except Exception as e:
            print(f"❌ Error leyendo symlink: {e}")
    else:
        print(f"❌ Symlink no existe: {SECUGEN_CONFIG['persistent_symlink']}")
    
    return device_info

def check_udev_rules():
    """Verificar estado de las reglas udev"""
    print_section("⚙️ VERIFICACIÓN DE REGLAS UDEV")
    
    # Verificar archivo de reglas
    if os.path.exists(SECUGEN_CONFIG['udev_rules_path']):
        print(f"✅ Reglas udev instaladas: {SECUGEN_CONFIG['udev_rules_path']}")
        
        # Mostrar contenido
        try:
            with open(SECUGEN_CONFIG['udev_rules_path'], 'r') as f:
                content = f.read()
                print(f"📝 Contenido:")
                for line in content.strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
        except Exception as e:
            print(f"❌ Error leyendo reglas: {e}")
    else:
        print(f"❌ Reglas udev no instaladas: {SECUGEN_CONFIG['udev_rules_path']}")
        
        # Verificar si existe en el proyecto
        if os.path.exists(SECUGEN_CONFIG['project_rules_path']):
            print(f"✅ Reglas disponibles en proyecto: {SECUGEN_CONFIG['project_rules_path']}")
        else:
            print(f"❌ Reglas no encontradas en proyecto: {SECUGEN_CONFIG['project_rules_path']}")
    
    # Verificar permisos
    print(f"\n🔐 Verificando permisos...")
    if os.path.exists(SECUGEN_CONFIG['udev_rules_path']):
        stat_info = os.stat(SECUGEN_CONFIG['udev_rules_path'])
        permissions = oct(stat_info.st_mode)[-3:]
        print(f"   Permisos: {permissions} (debe ser 644)")
        
        if permissions != '644':
            print("⚠️ Permisos incorrectos")
        else:
            print("✅ Permisos correctos")

def install_udev_rules():
    """Instalar reglas udev"""
    print_section("🔧 INSTALACIÓN DE REGLAS UDEV")
    
    # Verificar permisos
    if os.geteuid() != 0:
        print("❌ Se requieren permisos de root")
        print("💡 Ejecute: sudo python3 identificar_dispositivo_persistente.py --install")
        return False
    
    # Verificar archivo fuente
    if not os.path.exists(SECUGEN_CONFIG['project_rules_path']):
        print(f"❌ Archivo de reglas no encontrado: {SECUGEN_CONFIG['project_rules_path']}")
        return False
    
    # Copiar archivo
    success, _, _ = run_command(f"cp {SECUGEN_CONFIG['project_rules_path']} {SECUGEN_CONFIG['udev_rules_path']}")
    if not success:
        print("❌ Error copiando archivo")
        return False
    
    # Configurar permisos
    run_command(f"chmod 644 {SECUGEN_CONFIG['udev_rules_path']}")
    run_command(f"chown root:root {SECUGEN_CONFIG['udev_rules_path']}")
    
    print("✅ Reglas udev instaladas")
    
    # Recargar reglas
    print("🔄 Recargando reglas udev...")
    run_command("udevadm control --reload-rules")
    run_command("udevadm trigger")
    
    print("⏳ Esperando que se apliquen las reglas...")
    time.sleep(3)
    
    # Verificar resultado
    if os.path.exists(SECUGEN_CONFIG['persistent_symlink']):
        print(f"✅ Symlink creado: {SECUGEN_CONFIG['persistent_symlink']}")
        return True
    else:
        print(f"❌ Symlink no creado: {SECUGEN_CONFIG['persistent_symlink']}")
        return False

def create_helper_scripts():
    """Crear scripts de ayuda"""
    print_section("📜 CREACIÓN DE SCRIPTS DE AYUDA")
    
    # Script 1: Configuración automática
    setup_script = """#!/bin/bash
# Script para configurar dispositivo SecuGen persistente

echo "🔧 Configurando dispositivo SecuGen persistente..."

# Verificar permisos
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script requiere permisos de root"
    echo "💡 Ejecute: sudo $0"
    exit 1
fi

# Verificar dispositivo
if ! lsusb | grep -q "1162:2201"; then
    echo "❌ Dispositivo SecuGen no encontrado"
    echo "💡 Conecte el dispositivo y vuelva a intentar"
    exit 1
fi

# Instalar reglas udev
echo "📋 Instalando reglas udev..."
if [ -f "docker/99SecuGen.rules" ]; then
    cp docker/99SecuGen.rules /etc/udev/rules.d/
    chmod 644 /etc/udev/rules.d/99SecuGen.rules
    chown root:root /etc/udev/rules.d/99SecuGen.rules
    echo "✅ Reglas instaladas"
else
    echo "❌ Archivo de reglas no encontrado"
    exit 1
fi

# Recargar reglas
echo "🔄 Recargando reglas udev..."
udevadm control --reload-rules
udevadm trigger

# Esperar
echo "⏳ Esperando que se apliquen las reglas..."
sleep 3

# Verificar
if [ -L "/dev/secugen_device" ]; then
    echo "✅ Dispositivo persistente configurado: /dev/secugen_device"
    ls -la /dev/secugen_device
    echo "🎉 ¡Configuración completada!"
else
    echo "❌ Error: Symlink no creado"
    exit 1
fi
"""
    
    with open('setup_persistent_device.sh', 'w') as f:
        f.write(setup_script)
    os.chmod('setup_persistent_device.sh', 0o755)
    print("✅ Script creado: setup_persistent_device.sh")
    
    # Script 2: Verificación
    check_script = """#!/bin/bash
# Script para verificar dispositivo SecuGen persistente

echo "🔍 Verificando dispositivo SecuGen persistente..."

# Verificar dispositivo USB
if lsusb | grep -q "1162:2201"; then
    echo "✅ Dispositivo USB detectado"
    lsusb | grep "1162:2201"
else
    echo "❌ Dispositivo USB no encontrado"
fi

# Verificar reglas udev
if [ -f "/etc/udev/rules.d/99SecuGen.rules" ]; then
    echo "✅ Reglas udev instaladas"
else
    echo "❌ Reglas udev no instaladas"
fi

# Verificar symlink
if [ -L "/dev/secugen_device" ]; then
    echo "✅ Symlink persistente funcional"
    ls -la /dev/secugen_device
else
    echo "❌ Symlink persistente no existe"
fi

# Verificar permisos
if [ -r "/dev/secugen_device" ]; then
    echo "✅ Permisos de lectura OK"
else
    echo "⚠️ Sin permisos de lectura"
fi

echo "🏁 Verificación completada"
"""
    
    with open('check_persistent_device.sh', 'w') as f:
        f.write(check_script)
    os.chmod('check_persistent_device.sh', 0o755)
    print("✅ Script creado: check_persistent_device.sh")

def test_persistent_device():
    """Probar acceso al dispositivo persistente"""
    print_section("🧪 PRUEBA DEL DISPOSITIVO PERSISTENTE")
    
    if not os.path.exists(SECUGEN_CONFIG['persistent_symlink']):
        print(f"❌ Symlink no existe: {SECUGEN_CONFIG['persistent_symlink']}")
        return False
    
    try:
        # Verificar que podemos leer el symlink
        target = os.readlink(SECUGEN_CONFIG['persistent_symlink'])
        print(f"✅ Symlink apunta a: {target}")
        
        # Verificar que el target existe
        if os.path.exists(target):
            print(f"✅ Target existe y es accesible")
            
            # Verificar permisos
            if os.access(target, os.R_OK):
                print("✅ Permisos de lectura OK")
            else:
                print("⚠️ Sin permisos de lectura")
                
            if os.access(target, os.W_OK):
                print("✅ Permisos de escritura OK")
            else:
                print("⚠️ Sin permisos de escritura")
            
            return True
        else:
            print(f"❌ Target no existe: {target}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print_header("IDENTIFICADOR PERSISTENTE PARA DISPOSITIVO SECUGEN")
    
    print(f"""
🎯 OBJETIVO: Configurar identificador persistente para lector SecuGen
🔧 SYMLINK: {SECUGEN_CONFIG['persistent_symlink']}
📋 BENEFICIOS:
   - ✅ Ruta fija independiente de /dev/bus/usb/XXX/YYY
   - ✅ Funciona después de desconectar/reconectar
   - ✅ Simplifica scripts y aplicaciones
   - ✅ Evita cambios en números de dispositivo
""")
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] == '--install':
            install_udev_rules()
            return
        elif sys.argv[1] == '--test':
            test_persistent_device()
            return
    
    # Análisis completo
    device_info = get_device_info()
    
    if not device_info['found']:
        print("\n❌ DISPOSITIVO SECUGEN NO ENCONTRADO")
        print("💡 SOLUCIONES:")
        print("   1. Conectar el dispositivo USB")
        print("   2. Verificar que es un SecuGen compatible")
        print("   3. Ejecutar: lsusb | grep SecuGen")
        return
    
    print(f"\n✅ DISPOSITIVO ENCONTRADO")
    print(f"📊 Métodos de identificación: {list(device_info['methods'].keys())}")
    
    # Verificar reglas udev
    check_udev_rules()
    
    # Crear scripts de ayuda
    create_helper_scripts()
    
    # Probar dispositivo persistente
    persistent_works = test_persistent_device()
    
    print(f"\n📋 RESUMEN:")
    print(f"   Dispositivo encontrado: ✅")
    print(f"   Symlink persistente: {'✅' if persistent_works else '❌'}")
    print(f"   Reglas udev: {'✅' if os.path.exists(SECUGEN_CONFIG['udev_rules_path']) else '❌'}")
    
    if not persistent_works:
        print(f"\n🔧 PASOS PARA CONFIGURAR:")
        print(f"   1. Ejecutar: sudo python3 {sys.argv[0]} --install")
        print(f"   2. O ejecutar: sudo ./setup_persistent_device.sh")
        print(f"   3. Verificar: python3 {sys.argv[0]} --test")
        print(f"   4. O ejecutar: ./check_persistent_device.sh")
    else:
        print(f"\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
        print(f"   Usar en aplicaciones: {SECUGEN_CONFIG['persistent_symlink']}")
        print(f"   Verificar estado: ./check_persistent_device.sh")

if __name__ == "__main__":
    main() 