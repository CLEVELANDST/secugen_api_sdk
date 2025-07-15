#!/usr/bin/env python3
"""
RESET USB DEVICE - Solución para equipos con lector instalado permanentemente
===========================================================================
Este script simula una desconexión/reconexión del dispositivo USB SecuGen
sin necesidad de tocar físicamente el cable. Útil para equipos donde el
lector está instalado permanentemente.

ACTUALIZACIÓN: Ahora incluye identificadores persistentes para el dispositivo USB.
"""

import subprocess
import os
import time
import sys
import glob
from pathlib import Path

# Configuración del dispositivo SecuGen
SECUGEN_CONFIG = {
    'vendor_id': '1162',
    'product_id': '2201',
    'device_name': 'SecuGen',
    'persistent_symlink': '/dev/secugen_device',
    'udev_rules_path': '/etc/udev/rules.d/99SecuGen.rules'
}

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔄 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n{step} {description}")
    print("-" * 40)

def run_command(cmd, description, show_output=True):
    """Ejecutar comando del sistema"""
    if show_output:
        print(f"💻 Ejecutando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if show_output:
            print(f"📊 Exit code: {result.returncode}")
            if result.stdout:
                print(f"📝 Output: {result.stdout.strip()}")
            if result.stderr and result.returncode != 0:
                print(f"⚠️ Error: {result.stderr.strip()}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout - comando tardó más de 10 segundos")
        return False, "", ""
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, "", ""

def get_device_persistent_info():
    """Obtener información persistente del dispositivo usando múltiples métodos"""
    print_step("1️⃣", "IDENTIFICACIÓN PERSISTENTE DEL DISPOSITIVO")
    
    device_info = {
        'vendor_id': SECUGEN_CONFIG['vendor_id'],
        'product_id': SECUGEN_CONFIG['product_id'],
        'persistent_symlink': SECUGEN_CONFIG['persistent_symlink'],
        'found': False
    }
    
    # Método 1: Verificar symlink persistente
    print("🔗 Verificando symlink persistente...")
    if os.path.exists(SECUGEN_CONFIG['persistent_symlink']):
        try:
            real_path = os.readlink(SECUGEN_CONFIG['persistent_symlink'])
            print(f"✅ Symlink encontrado: {SECUGEN_CONFIG['persistent_symlink']} -> {real_path}")
            device_info['symlink_target'] = real_path
            device_info['found'] = True
            
            # Extraer información del path real
            if '/dev/bus/usb/' in real_path:
                parts = real_path.split('/')
                device_info['bus'] = parts[-2]
                device_info['device'] = parts[-1]
                device_info['usb_path'] = real_path
        except Exception as e:
            print(f"⚠️ Error leyendo symlink: {e}")
    else:
        print("❌ Symlink persistente no encontrado")
    
    # Método 2: Buscar por lsusb
    print("\n🔍 Buscando dispositivo por lsusb...")
    success, output, _ = run_command(f"lsusb | grep -i {SECUGEN_CONFIG['device_name']}", 
                                    "Buscar por nombre", show_output=False)
    
    if not success:
        # Intentar con vendor:product ID
        success, output, _ = run_command(f"lsusb | grep '{SECUGEN_CONFIG['vendor_id']}:{SECUGEN_CONFIG['product_id']}'", 
                                        "Buscar por ID", show_output=False)
    
    if success and output:
        print(f"✅ Dispositivo encontrado: {output.strip()}")
        
        # Extraer información del lsusb
        parts = output.strip().split()
        if len(parts) >= 4:
            device_info['lsusb_bus'] = parts[1]
            device_info['lsusb_device'] = parts[3].rstrip(':')
            device_info['lsusb_path'] = f"/dev/bus/usb/{parts[1]}/{parts[3].rstrip(':')}"
            device_info['found'] = True
    else:
        print("❌ Dispositivo no encontrado por lsusb")
    
    # Método 3: Buscar en sysfs
    print("\n🗂️ Buscando en sysfs...")
    sysfs_devices = glob.glob('/sys/bus/usb/devices/*')
    
    for device_path in sysfs_devices:
        try:
            vendor_file = os.path.join(device_path, 'idVendor')
            product_file = os.path.join(device_path, 'idProduct')
            
            if os.path.exists(vendor_file) and os.path.exists(product_file):
                with open(vendor_file, 'r') as f:
                    vendor = f.read().strip()
                with open(product_file, 'r') as f:
                    product = f.read().strip()
                
                if vendor == SECUGEN_CONFIG['vendor_id'] and product == SECUGEN_CONFIG['product_id']:
                    print(f"✅ Dispositivo encontrado en sysfs: {device_path}")
                    device_info['sysfs_path'] = device_path
                    device_info['found'] = True
                    
                    # Obtener información adicional
                    try:
                        with open(os.path.join(device_path, 'busnum'), 'r') as f:
                            device_info['sysfs_bus'] = f.read().strip().zfill(3)
                        with open(os.path.join(device_path, 'devnum'), 'r') as f:
                            device_info['sysfs_device'] = f.read().strip().zfill(3)
                    except:
                        pass
                    break
        except Exception as e:
            continue
    
    # Método 4: Buscar por número de serie (si disponible)
    print("\n🔢 Buscando por número de serie...")
    if 'sysfs_path' in device_info:
        try:
            serial_file = os.path.join(device_info['sysfs_path'], 'serial')
            if os.path.exists(serial_file):
                with open(serial_file, 'r') as f:
                    serial = f.read().strip()
                    if serial:
                        device_info['serial'] = serial
                        print(f"✅ Número de serie: {serial}")
                    else:
                        print("⚠️ Número de serie vacío")
            else:
                print("⚠️ Archivo de serial no encontrado")
        except Exception as e:
            print(f"⚠️ Error leyendo serial: {e}")
    
    return device_info

def find_secugen_device():
    """Wrapper para mantener compatibilidad con versión anterior"""
    device_info = get_device_persistent_info()
    
    if not device_info['found']:
        print("❌ Dispositivo SecuGen no encontrado")
        return None
    
    # Determinar el mejor path para usar
    if 'symlink_target' in device_info:
        device_info['usb_device'] = device_info['symlink_target']
        device_info['path'] = device_info.get('sysfs_path', '')
    elif 'lsusb_path' in device_info:
        device_info['usb_device'] = device_info['lsusb_path']
        device_info['bus'] = device_info.get('lsusb_bus', '')
        device_info['device'] = device_info.get('lsusb_device', '')
        device_info['path'] = device_info.get('sysfs_path', '')
    elif 'sysfs_path' in device_info:
        device_info['path'] = device_info['sysfs_path']
        if 'sysfs_bus' in device_info and 'sysfs_device' in device_info:
            device_info['usb_device'] = f"/dev/bus/usb/{device_info['sysfs_bus']}/{device_info['sysfs_device']}"
    
    return device_info

def ensure_persistent_device():
    """Asegurar que el dispositivo persistente esté configurado"""
    print_step("🔧", "CONFIGURACIÓN DE DISPOSITIVO PERSISTENTE")
    
    # Verificar si las reglas udev están instaladas
    if not os.path.exists(SECUGEN_CONFIG['udev_rules_path']):
        print("⚠️ Reglas udev no encontradas, instalando...")
        
        # Verificar si existe el archivo en el proyecto
        project_rules = 'docker/99SecuGen.rules'
        if os.path.exists(project_rules):
            success, _, _ = run_command(f"sudo cp {project_rules} {SECUGEN_CONFIG['udev_rules_path']}", 
                                      "Copiar reglas udev")
            if success:
                run_command(f"sudo chmod 644 {SECUGEN_CONFIG['udev_rules_path']}", 
                          "Configurar permisos")
                run_command(f"sudo chown root:root {SECUGEN_CONFIG['udev_rules_path']}", 
                          "Configurar propietario")
                print("✅ Reglas udev instaladas")
            else:
                print("❌ Error instalando reglas udev")
                return False
        else:
            print("❌ Archivo de reglas udev no encontrado en el proyecto")
            return False
    else:
        print("✅ Reglas udev ya están instaladas")
    
    # Recargar reglas udev
    print("🔄 Recargando reglas udev...")
    run_command("sudo udevadm control --reload-rules", "Recargar reglas")
    run_command("sudo udevadm trigger", "Activar reglas")
    
    # Esperar un momento para que se apliquen
    time.sleep(2)
    
    # Verificar que el symlink se creó
    if os.path.exists(SECUGEN_CONFIG['persistent_symlink']):
        print(f"✅ Symlink persistente creado: {SECUGEN_CONFIG['persistent_symlink']}")
        return True
    else:
        print("⚠️ Symlink persistente no se creó automáticamente")
        return False

def method_1_unbind_rebind(device_info):
    """Método 1: Desvincular y reenlazar el driver"""
    print_step("2️⃣", "MÉTODO 1: UNBIND/REBIND DRIVER")
    
    try:
        # Usar diferentes paths según lo disponible
        if 'sysfs_path' in device_info:
            device_path = device_info['sysfs_path']
        elif 'path' in device_info:
            device_path = device_info['path']
        else:
            print("❌ No se encontró path del dispositivo para unbind/rebind")
            return False
        
        # Desvincular el dispositivo
        print("🔌 Desvinculando dispositivo del driver...")
        unbind_path = "/sys/bus/usb/drivers/usb/unbind"
        device_name = os.path.basename(device_path)
        
        success, _, _ = run_command(f"echo '{device_name}' | sudo tee {unbind_path}", 
                                   "Unbind device")
        
        if success:
            print("✅ Dispositivo desvinculado")
        else:
            print("⚠️ Error al desvincular (puede ser normal)")
        
        # Esperar
        time.sleep(2)
        
        # Reenlazar el dispositivo
        print("🔗 Reenlazando dispositivo al driver...")
        rebind_path = "/sys/bus/usb/drivers/usb/bind"
        
        success, _, _ = run_command(f"echo '{device_name}' | sudo tee {rebind_path}", 
                                   "Rebind device")
        
        if success:
            print("✅ Dispositivo reenlazado")
            return True
        else:
            print("⚠️ Error al reenlazar")
            return False
            
    except Exception as e:
        print(f"❌ Error en método 1: {e}")
        return False

def method_2_reset_port(device_info):
    """Método 2: Reset del puerto USB específico"""
    print_step("3️⃣", "MÉTODO 2: RESET PUERTO USB")
    
    try:
        # Determinar el dispositivo USB a usar
        usb_device = None
        
        # Prioridad: symlink persistente > path calculado > fallback
        if 'symlink_target' in device_info:
            usb_device = device_info['symlink_target']
        elif 'usb_device' in device_info:
            usb_device = device_info['usb_device']
        elif 'lsusb_path' in device_info:
            usb_device = device_info['lsusb_path']
        else:
            print("❌ No se pudo determinar el dispositivo USB")
            return False
        
        print(f"🎯 Usando dispositivo: {usb_device}")
        
        # Método usando usbreset (si está disponible)
        success, _, _ = run_command("which usbreset", "Verificar usbreset", show_output=False)
        
        if success:
            print("🔧 Usando usbreset...")
            success, _, _ = run_command(f"sudo usbreset {usb_device}", "Reset USB device")
            if success:
                print("✅ Puerto USB reseteado con usbreset")
                return True
        
        # Método alternativo: reset via sysfs
        print("🔧 Usando reset via sysfs...")
        if 'sysfs_path' in device_info:
            reset_path = os.path.join(device_info['sysfs_path'], 'reset')
            
            if os.path.exists(reset_path):
                success, _, _ = run_command(f"echo 1 | sudo tee {reset_path}", "Reset via sysfs")
                if success:
                    print("✅ Dispositivo reseteado via sysfs")
                    return True
        
        print("⚠️ No se pudo resetear el puerto USB")
        return False
        
    except Exception as e:
        print(f"❌ Error en método 2: {e}")
        return False

def method_3_power_cycle(device_info):
    """Método 3: Ciclo de energía del puerto USB"""
    print_step("4️⃣", "MÉTODO 3: CICLO DE ENERGÍA USB")
    
    try:
        if 'sysfs_path' not in device_info:
            print("❌ Path sysfs no disponible para ciclo de energía")
            return False
            
        device_path = device_info['sysfs_path']
        
        # Deshabilitar autosuspend
        print("🔋 Configurando power management...")
        power_path = os.path.join(device_path, 'power')
        
        if os.path.exists(power_path):
            # Desactivar autosuspend
            success, _, _ = run_command(f"echo 'on' | sudo tee {power_path}/control", 
                                       "Deshabilitar autosuspend")
            
            time.sleep(1)
            
            # Reactivar autosuspend
            success, _, _ = run_command(f"echo 'auto' | sudo tee {power_path}/control", 
                                       "Reactivar autosuspend")
            
            if success:
                print("✅ Ciclo de energía completado")
                return True
        
        print("⚠️ No se pudo realizar ciclo de energía")
        return False
        
    except Exception as e:
        print(f"❌ Error en método 3: {e}")
        return False

def method_4_module_reload():
    """Método 4: Recargar módulos USB"""
    print_step("5️⃣", "MÉTODO 4: RECARGAR MÓDULOS USB")
    
    try:
        print("🔄 Recargando módulos USB...")
        
        # Remover módulos
        modules_to_reload = ['usbhid', 'usb_storage', 'usb_common']
        
        for module in modules_to_reload:
            print(f"📤 Removiendo módulo {module}...")
            run_command(f"sudo modprobe -r {module}", f"Remove {module}", show_output=False)
            
        time.sleep(2)
        
        # Recargar módulos
        for module in reversed(modules_to_reload):
            print(f"📥 Cargando módulo {module}...")
            run_command(f"sudo modprobe {module}", f"Load {module}", show_output=False)
            
        print("✅ Módulos USB recargados")
        return True
        
    except Exception as e:
        print(f"❌ Error en método 4: {e}")
        return False

def verify_device_recovery():
    """Verificar que el dispositivo se recuperó correctamente"""
    print_step("6️⃣", "VERIFICACIÓN DE RECUPERACIÓN")
    
    print("🔍 Esperando estabilización del dispositivo...")
    time.sleep(3)
    
    # Verificar que el dispositivo está presente
    success, output, _ = run_command(f"lsusb | grep -i {SECUGEN_CONFIG['device_name']}", 
                                    "Verificar dispositivo")
    if not success:
        success, output, _ = run_command(f"lsusb | grep '{SECUGEN_CONFIG['vendor_id']}:{SECUGEN_CONFIG['product_id']}'", 
                                        "Verificar por ID")
    
    if success and output:
        print(f"✅ Dispositivo detectado: {output.strip()}")
        
        # Verificar symlink persistente
        if os.path.exists(SECUGEN_CONFIG['persistent_symlink']):
            print(f"✅ Symlink persistente funcional: {SECUGEN_CONFIG['persistent_symlink']}")
        else:
            print("⚠️ Symlink persistente no disponible")
        
        # Verificar permisos
        device_info = get_device_persistent_info()
        if device_info['found'] and 'usb_device' in device_info:
            success, output, _ = run_command(f"ls -la {device_info['usb_device']}", 
                                           "Verificar permisos", show_output=False)
            if success:
                print("✅ Permisos verificados")
            
        return True
    else:
        print("❌ Dispositivo no detectado después del reset")
        return False

def test_sdk_connection():
    """Probar la conexión del SDK después del reset"""
    print_step("7️⃣", "PRUEBA DE CONEXIÓN SDK")
    
    try:
        print("🔌 Probando conexión con SDK...")
        
        # Importar SDK
        from sdk import PYSGFPLib
        from python.sgfdxerrorcode import SGFDxErrorCode
        
        sgfp = PYSGFPLib()
        
        # Create y Init
        err = sgfp.Create()
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"❌ Create() falló: {err}")
            return False
            
        err = sgfp.Init(1)
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"❌ Init() falló: {err}")
            return False
            
        # Probar OpenDevice
        for device_id in range(4):
            err = sgfp.OpenDevice(device_id)
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"✅ OpenDevice({device_id}) exitoso!")
                sgfp.CloseDevice()
                return True
            else:
                print(f"⚠️ OpenDevice({device_id}) falló: {err}")
                
        print("❌ No se pudo abrir el dispositivo con ningún ID")
        return False
        
    except Exception as e:
        print(f"❌ Error probando SDK: {e}")
        return False

def create_persistent_device_script():
    """Crear script para configurar dispositivo persistente"""
    script_content = f"""#!/bin/bash
# Script para configurar dispositivo SecuGen persistente

# Verificar permisos
if [ "$EUID" -ne 0 ]; then
    echo "Por favor ejecute como root: sudo $0"
    exit 1
fi

# Instalar reglas udev
if [ ! -f "{SECUGEN_CONFIG['udev_rules_path']}" ]; then
    echo "Instalando reglas udev..."
    cp docker/99SecuGen.rules {SECUGEN_CONFIG['udev_rules_path']}
    chmod 644 {SECUGEN_CONFIG['udev_rules_path']}
    chown root:root {SECUGEN_CONFIG['udev_rules_path']}
fi

# Recargar reglas
echo "Recargando reglas udev..."
udevadm control --reload-rules
udevadm trigger

# Esperar
sleep 2

# Verificar
if [ -L "{SECUGEN_CONFIG['persistent_symlink']}" ]; then
    echo "✅ Dispositivo persistente configurado: {SECUGEN_CONFIG['persistent_symlink']}"
    ls -la {SECUGEN_CONFIG['persistent_symlink']}
else
    echo "❌ Error: Symlink persistente no creado"
    exit 1
fi

echo "✅ Configuración completada"
"""
    
    with open('setup_persistent_device.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('setup_persistent_device.sh', 0o755)
    print("✅ Script de configuración creado: setup_persistent_device.sh")

def main():
    print_header("RESET USB DEVICE - SOLUCIÓN CON IDENTIFICADORES PERSISTENTES")
    
    print(f"""
🎯 OBJETIVO: Simular desconexión/reconexión USB por software
📋 CARACTERÍSTICAS NUEVAS:
   - ✅ Identificadores persistentes (symlink: {SECUGEN_CONFIG['persistent_symlink']})
   - ✅ Múltiples métodos de identificación del dispositivo
   - ✅ Búsqueda robusta por vendor/product ID
   - ✅ Configuración automática de reglas udev
   - ✅ Compatibilidad con equipos permanentes

📱 CASOS DE USO:
   - Lector instalado permanentemente
   - Error 2 (SGFDX_ERROR_FUNCTION_FAILED) persistente
   - Dispositivo detectado pero SDK no puede abrirlo
   - Alternativa a desconectar físicamente el cable USB
""")
    
    # Verificar permisos de sudo
    if os.geteuid() != 0:
        print("⚠️ Este script requiere permisos de superusuario para algunas operaciones")
        print("💡 Ejecute: sudo python3 reset_usb_device.py")
    
    try:
        # Configurar dispositivo persistente
        ensure_persistent_device()
        
        # Crear script de configuración
        create_persistent_device_script()
        
        # Buscar dispositivo con identificadores persistentes
        device_info = find_secugen_device()
        if not device_info:
            print("❌ No se puede continuar sin el dispositivo SecuGen")
            return
        
        # Mostrar información del dispositivo encontrado
        print(f"\n📱 INFORMACIÓN DEL DISPOSITIVO:")
        print(f"   Vendor ID: {device_info.get('vendor_id', 'N/A')}")
        print(f"   Product ID: {device_info.get('product_id', 'N/A')}")
        if 'serial' in device_info:
            print(f"   Serial: {device_info['serial']}")
        if 'persistent_symlink' in device_info:
            print(f"   Symlink persistente: {device_info['persistent_symlink']}")
        if 'usb_device' in device_info:
            print(f"   Dispositivo USB: {device_info['usb_device']}")
        
        # Intentar diferentes métodos de reset
        methods = [
            ("Unbind/Rebind Driver", method_1_unbind_rebind),
            ("Reset Puerto USB", method_2_reset_port),
            ("Ciclo de Energía", method_3_power_cycle),
            ("Recargar Módulos", method_4_module_reload)
        ]
        
        for method_name, method_func in methods:
            print(f"\n🔄 Probando: {method_name}")
            success = method_func(device_info)
            
            if success:
                # Verificar recuperación
                if verify_device_recovery():
                    # Probar SDK
                    if test_sdk_connection():
                        print(f"\n🎉 ¡ÉXITO! Método '{method_name}' funcionó correctamente")
                        print(f"\n📋 RECOMENDACIONES:")
                        print(f"   - Usar método '{method_name}' para futuros resets")
                        print(f"   - Dispositivo persistente: {SECUGEN_CONFIG['persistent_symlink']}")
                        print(f"   - Implementar en script de monitoreo automático")
                        print(f"   - Ejecutar cuando se detecte Error 2")
                        print(f"   - Script de configuración: ./setup_persistent_device.sh")
                        return
                    else:
                        print(f"⚠️ Método '{method_name}' parcialmente exitoso - dispositivo detectado pero SDK falla")
                else:
                    print(f"❌ Método '{method_name}' falló - dispositivo no se recuperó")
            else:
                print(f"❌ Método '{method_name}' falló")
                
            # Esperar antes del siguiente método
            time.sleep(2)
        
        print("\n🚨 TODOS LOS MÉTODOS FALLARON")
        print("💡 RECOMENDACIONES ADICIONALES:")
        print("   1. Verificar que el dispositivo no esté dañado")
        print("   2. Ejecutar: sudo ./setup_persistent_device.sh")
        print("   3. Verificar reglas udev: ls -la /etc/udev/rules.d/99SecuGen.rules")
        print("   4. Verificar symlink: ls -la /dev/secugen_device")
        print("   5. Probar en otro puerto USB")
        print("   6. Verificar compatibilidad del SDK")
        print("   7. Contactar soporte técnico de SecuGen")
        
    except KeyboardInterrupt:
        print("\n⏹️ Reset interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 