#!/usr/bin/env python3
"""
DIAGNÓSTICO: "El lector se cae" - Problema de estabilidad del dispositivo SecuGen
=============================================================================
Este script diagnostica específicamente por qué el dispositivo SecuGen se desconecta
y el SDK no puede abrirlo, basándose en los logs del sistema que mostraron:
- Desconexiones frecuentes del USB
- Errores de segmentación en libsgfdu06.so
- OpenDevice() falla consistentemente con Error 2
"""

import subprocess
import os
import time
import sys
from ctypes import c_long, byref

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n{step} {description}")
    print("-" * 40)

def run_command(cmd, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"💻 Ejecutando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"✅ Exit code: {result.returncode}")
        if result.stdout:
            print(f"📝 Output:\n{result.stdout}")
        if result.stderr:
            print(f"⚠️ Errors:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout - comando tardó más de 10 segundos")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def check_usb_stability():
    """Verificar estabilidad del dispositivo USB"""
    print_step("1️⃣", "VERIFICANDO ESTABILIDAD DEL DISPOSITIVO USB")
    
    # Verificar dispositivo actual
    print("🔍 Dispositivo SecuGen actual:")
    run_command("lsusb | grep -i secugen", "Listar dispositivo SecuGen")
    
    # Verificar mensajes del kernel sobre desconexiones
    print("\n🔍 Últimas desconexiones/reconexiones:")
    run_command("dmesg | grep -i '1162:2201\\|secugen' | tail -10", "Mensajes del kernel")
    
    # Verificar errores de segmentación
    print("\n🔍 Errores de segmentación en libsgfdu06.so:")
    run_command("dmesg | grep -i 'libsgfdu06.so\\|segfault' | tail -5", "Segfaults")
    
    # Verificar estado del archivo del dispositivo
    print("\n🔍 Estado del archivo del dispositivo:")
    run_command("ls -la /dev/bus/usb/002/006", "Permisos del dispositivo")
    run_command("ls -la /dev/secugen_device", "Symlink del dispositivo")

def check_sdk_initialization():
    """Verificar inicialización del SDK paso a paso"""
    print_step("2️⃣", "DIAGNÓSTICO DEL SDK NATIVO")
    
    try:
        # Importar SDK
        print("📦 Importando SDK...")
        from sdk import PYSGFPLib
        from python.sgfdxerrorcode import SGFDxErrorCode
        print("✅ SDK importado correctamente")
        
        # Crear instancia
        print("\n🏗️ Creando instancia del SDK...")
        sgfp = PYSGFPLib()
        
        # Paso 1: Create()
        print("\n🔧 Ejecutando Create()...")
        err = sgfp.Create()
        print(f"📊 Create() resultado: {err}")
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"❌ Create() falló: {err}")
            return False
        print("✅ Create() exitoso")
        
        # Paso 2: Init()
        print("\n🔧 Ejecutando Init(1)...")
        err = sgfp.Init(1)
        print(f"📊 Init() resultado: {err}")
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"❌ Init() falló: {err}")
            return False
        print("✅ Init() exitoso")
        
        # Paso 3: OpenDevice() - Aquí es donde falla
        print("\n🔧 Ejecutando OpenDevice()...")
        device_ids = [0, 1, 2, 3, 4, 5]  # Probar más IDs
        
        for device_id in device_ids:
            print(f"\n   🔍 Probando Device ID: {device_id}")
            err = sgfp.OpenDevice(device_id)
            print(f"   📊 OpenDevice({device_id}) resultado: {err}")
            
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"   ✅ Device ID {device_id} abierto exitosamente")
                
                # Probar operación básica
                print(f"   🔍 Probando operación básica...")
                width = c_long(0)
                height = c_long(0)
                info_err = sgfp.GetDeviceInfo(width, height)
                print(f"   📊 GetDeviceInfo() resultado: {info_err}")
                if info_err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                    print(f"   ✅ Dimensiones: {width.value}x{height.value}")
                else:
                    print(f"   ❌ GetDeviceInfo() falló: {info_err}")
                
                # Cerrar dispositivo
                sgfp.CloseDevice()
                return True
            else:
                error_messages = {
                    1: "SGFDX_ERROR_CREATION_FAILED",
                    2: "SGFDX_ERROR_FUNCTION_FAILED", 
                    3: "SGFDX_ERROR_INVALID_PARAM",
                    4: "SGFDX_ERROR_NOT_USED",
                    5: "SGFDX_ERROR_DLLLOAD_FAILED",
                    6: "SGFDX_ERROR_WRONG_IMAGE",
                    7: "SGFDX_ERROR_LACK_OF_BANDWIDTH",
                    8: "SGFDX_ERROR_DEV_ALREADY_OPEN",
                    9: "SGFDX_ERROR_GETSN_FAILED",
                    10: "SGFDX_ERROR_UNSUPPORTED_DEV",
                    11: "SGFDX_ERROR_INVALID_BRIGHTNESS",
                    12: "SGFDX_ERROR_INVALID_CONTRAST",
                    13: "SGFDX_ERROR_INVALID_GAIN",
                    14: "SGFDX_ERROR_INVALID_TEMPLATE_TYPE"
                }
                error_desc = error_messages.get(err, f"Error desconocido: {err}")
                print(f"   ❌ Device ID {device_id} falló: {error_desc}")
        
        print(f"\n🚨 CRÍTICO: No se pudo abrir el dispositivo con ningún ID")
        return False
        
    except Exception as e:
        print(f"❌ Error en diagnóstico del SDK: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_process_conflicts():
    """Verificar conflictos de procesos"""
    print_step("3️⃣", "VERIFICANDO CONFLICTOS DE PROCESOS")
    
    # Verificar procesos usando el dispositivo
    print("🔍 Procesos usando libsgfdu06.so:")
    run_command("lsof | grep -i libsgfdu06 | head -10", "Procesos con SDK")
    
    # Verificar procesos Python
    print("\n🔍 Procesos Python activos:")
    run_command("ps aux | grep python | grep -v grep", "Procesos Python")
    
    # Verificar archivos abiertos del dispositivo
    print("\n🔍 Archivos abiertos del dispositivo:")
    run_command("lsof /dev/bus/usb/002/006 2>/dev/null", "Archivos del dispositivo")

def check_system_resources():
    """Verificar recursos del sistema"""
    print_step("4️⃣", "VERIFICANDO RECURSOS DEL SISTEMA")
    
    # Verificar memoria
    print("🔍 Memoria disponible:")
    run_command("free -h", "Memoria del sistema")
    
    # Verificar carga del sistema
    print("\n🔍 Carga del sistema:")
    run_command("uptime", "Carga del sistema")
    
    # Verificar errores del kernel
    print("\n🔍 Errores recientes del kernel:")
    run_command("dmesg | tail -20 | grep -i 'error\\|fail\\|segfault'", "Errores del kernel")

def recommend_solutions():
    """Recomendar soluciones basadas en el diagnóstico"""
    print_step("5️⃣", "RECOMENDACIONES DE SOLUCIÓN")
    
    print("""
🔧 SOLUCIONES RECOMENDADAS PARA "EL LECTOR SE CAE":

1️⃣ PROBLEMA: Segmentación en libsgfdu06.so
   💡 Solución: Reinstalar SDK o usar versión compatible
   🔧 Comando: Verificar versión del SDK

2️⃣ PROBLEMA: Error 2 (SGFDX_ERROR_FUNCTION_FAILED) en OpenDevice()
   💡 Solución: Problema de permisos o driver
   🔧 Comando: sudo chmod 666 /dev/bus/usb/002/006

3️⃣ PROBLEMA: Desconexiones frecuentes del USB
   💡 Solución: Deshabilitar power management
   🔧 Comando: echo 'auto' | sudo tee /sys/bus/usb/devices/2-2/power/control

4️⃣ PROBLEMA: Múltiples procesos usando el dispositivo
   💡 Solución: Asegurar acceso exclusivo
   🔧 Comando: pkill -f "python.*app.py"

5️⃣ PROBLEMA: Inestabilidad del cable/puerto USB
   💡 Solución: Cambiar puerto USB o cable
   🔧 Acción: Conectar en otro puerto USB

6️⃣ PROBLEMA: Conflicto con otros drivers USB
   💡 Solución: Desvincular de HID genérico
   🔧 Comando: sudo modprobe -r usbhid; sudo modprobe usbhid
""")

def main():
    print_header("DIAGNÓSTICO: EL LECTOR SE CAE")
    
    print("""
Este diagnóstico investigará por qué el dispositivo SecuGen se desconecta
y el SDK no puede abrirlo. Basado en los logs del sistema que mostraron:
- Desconexiones frecuentes del USB  
- Errores de segmentación en libsgfdu06.so
- OpenDevice() falla con Error 2
""")
    
    # Ejecutar diagnósticos
    try:
        check_usb_stability()
        sdk_ok = check_sdk_initialization()
        check_process_conflicts()
        check_system_resources()
        recommend_solutions()
        
        # Resumen final
        print_step("📊", "RESUMEN DEL DIAGNÓSTICO")
        if sdk_ok:
            print("✅ SDK funciona correctamente")
        else:
            print("❌ SDK no puede abrir el dispositivo")
            print("🔧 Problema principal: Error 2 en OpenDevice()")
            print("📝 Revisar recomendaciones arriba")
            
    except KeyboardInterrupt:
        print("\n⏹️ Diagnóstico interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 