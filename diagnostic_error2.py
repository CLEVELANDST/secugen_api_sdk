#!/usr/bin/env python3
"""
Diagnóstico profundo del Error 2 (SGFDX_ERROR_FUNCTION_FAILED)
"""

import sys
import os
import time
from ctypes import c_int, c_long, byref

# Importar SDK SecuGen
try:
    from sdk import PYSGFPLib
    from python.sgfdxerrorcode import SGFDxErrorCode
    SDK_AVAILABLE = True
except ImportError as e:
    print(f"❌ ERROR: SDK SecuGen no disponible: {e}")
    sys.exit(1)

def diagnose_error2():
    print("🔍 DIAGNÓSTICO PROFUNDO ERROR 2")
    print("=" * 50)
    
    # Paso 1: Verificar instancia del SDK
    print("\n1️⃣ CREANDO INSTANCIA DEL SDK...")
    try:
        sgfp = PYSGFPLib()
        print("✅ Instancia del SDK creada exitosamente")
    except Exception as e:
        print(f"❌ ERROR al crear instancia: {e}")
        return
    
    # Paso 2: Intentar Create()
    print("\n2️⃣ EJECUTANDO sgfp.Create()...")
    try:
        err = sgfp.Create()
        print(f"📊 Resultado Create(): {err}")
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"❌ ERROR en Create(): {err}")
            return
        else:
            print("✅ Create() exitoso")
    except Exception as e:
        print(f"❌ EXCEPCIÓN en Create(): {e}")
        return
    
    # Paso 3: Intentar Init()
    print("\n3️⃣ EJECUTANDO sgfp.Init(1)...")
    try:
        err = sgfp.Init(1)
        print(f"📊 Resultado Init(1): {err}")
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"❌ ERROR en Init(1): {err}")
            return
        else:
            print("✅ Init(1) exitoso")
    except Exception as e:
        print(f"❌ EXCEPCIÓN en Init(1): {e}")
        return
    
    # Paso 4: Probar OpenDevice con cada ID
    print("\n4️⃣ PROBANDO OpenDevice() CON CADA ID...")
    device_opened = False
    working_device_id = None
    
    for device_id in range(10):  # Probar más IDs
        print(f"\n   🔍 Probando dispositivo ID: {device_id}")
        
        try:
            # Obtener información del dispositivo si es posible
            width = c_long(0)
            height = c_long(0)
            
            err = sgfp.OpenDevice(device_id)
            print(f"   📊 OpenDevice({device_id}): {err}")
            
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"   ✅ Dispositivo {device_id} abierto exitosamente!")
                device_opened = True
                working_device_id = device_id
                
                # Intentar obtener información del dispositivo
                info_err = sgfp.GetDeviceInfo(width, height)
                print(f"   📊 GetDeviceInfo(): {info_err}")
                if info_err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                    print(f"   📏 Dimensiones: {width.value}x{height.value}")
                else:
                    print(f"   ⚠️ Error en GetDeviceInfo: {info_err}")
                
                # Intentar SetLedOn
                led_err = sgfp.SetLedOn(True)
                print(f"   📊 SetLedOn(True): {led_err}")
                if led_err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                    print("   💡 LED encendido exitosamente")
                    time.sleep(1)
                    sgfp.SetLedOn(False)
                    print("   💡 LED apagado")
                else:
                    print(f"   ⚠️ Error en SetLedOn: {led_err}")
                
                break
                
            elif err == 2:  # SGFDX_ERROR_FUNCTION_FAILED
                print(f"   ❌ ID {device_id}: Error 2 (SGFDX_ERROR_FUNCTION_FAILED)")
            elif err == 3:  # SGFDX_ERROR_INVALID_PARAM
                print(f"   ❌ ID {device_id}: Error 3 (SGFDX_ERROR_INVALID_PARAM)")
            elif err == 4:  # SGFDX_ERROR_DEVICE_NOT_FOUND
                print(f"   ❌ ID {device_id}: Error 4 (SGFDX_ERROR_DEVICE_NOT_FOUND)")
            else:
                print(f"   ❌ ID {device_id}: Error desconocido {err}")
                
        except Exception as e:
            print(f"   ❌ EXCEPCIÓN con ID {device_id}: {e}")
    
    # Paso 5: Resultados
    print("\n5️⃣ RESULTADOS DEL DIAGNÓSTICO")
    print("=" * 30)
    
    if device_opened:
        print(f"✅ ÉXITO: Dispositivo funcional encontrado en ID {working_device_id}")
        print("🎉 El SDK SecuGen está funcionando correctamente")
        
        # Cerrar dispositivo
        try:
            sgfp.CloseDevice()
            print("✅ Dispositivo cerrado correctamente")
        except Exception as e:
            print(f"⚠️ Error al cerrar dispositivo: {e}")
    else:
        print("❌ FALLO: No se pudo abrir ningún dispositivo")
        print("\n🔍 POSIBLES CAUSAS:")
        print("   • Dispositivo no conectado físicamente")
        print("   • Conflicto con driver del sistema")
        print("   • Permisos insuficientes")
        print("   • Dispositivo en uso por otro proceso")
        print("   • Problema de firmware del dispositivo")
        print("   • Incompatibilidad de versión del SDK")

def check_system_info():
    print("\n🖥️ INFORMACIÓN DEL SISTEMA")
    print("=" * 30)
    
    # Verificar dispositivo USB
    import subprocess
    try:
        result = subprocess.run(['lsusb', '-d', '1162:2201'], capture_output=True, text=True)
        if result.stdout:
            print(f"📱 Dispositivo USB: {result.stdout.strip()}")
        else:
            print("❌ Dispositivo USB no encontrado")
    except Exception as e:
        print(f"⚠️ Error al verificar USB: {e}")
    
    # Verificar permisos
    import glob
    usb_devices = glob.glob('/dev/bus/usb/*/???')
    secugen_devices = []
    
    for device in usb_devices:
        try:
            with open(f'{device}/../idVendor', 'r') as f:
                vendor = f.read().strip()
            with open(f'{device}/../idProduct', 'r') as f:
                product = f.read().strip()
            
            if vendor == '1162' and product == '2201':
                secugen_devices.append(device)
                import stat
                st = os.stat(device)
                perms = stat.filemode(st.st_mode)
                print(f"📁 Permisos {device}: {perms}")
        except:
            continue
    
    if not secugen_devices:
        print("❌ No se encontraron dispositivos SecuGen en /dev/bus/usb/")

if __name__ == "__main__":
    check_system_info()
    diagnose_error2() 