#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'sdk'))

from sdk import PYSGFPLib
from sdk.sgfdxerrorcode import SGFDxErrorCode
from ctypes import c_int, byref, c_long, c_ubyte, POINTER, c_bool
import time

def diagnosticar_captura():
    print("🔧 Diagnóstico de Captura de Huella SecuGen")
    print("=" * 50)
    
    try:
        # Paso 1: Crear instancia
        print("1. Creando instancia del SDK...")
        sgfp = PYSGFPLib()
        print("   ✅ Instancia creada exitosamente")
        
        # Paso 2: Crear dispositivo
        print("\n2. Inicializando dispositivo...")
        err = sgfp.Create()
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"   ❌ Error en Create(): {err}")
            return
        print("   ✅ Create() exitoso")
        
        # Paso 3: Inicializar
        print("\n3. Ejecutando Init()...")
        err = sgfp.Init(1)
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"   ❌ Error en Init(): {err}")
            return
        print("   ✅ Init() exitoso")
        
        # Paso 4: Abrir dispositivo
        print("\n4. Abriendo dispositivo...")
        device_opened = False
        for device_id in [0, 1]:
            print(f"   Probando dispositivo ID: {device_id}")
            err = sgfp.OpenDevice(device_id)
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"   ✅ Dispositivo abierto con ID: {device_id}")
                device_opened = True
                break
            else:
                print(f"   ⚠️ Error con dispositivo {device_id}: {err}")
        
        if not device_opened:
            print("   ❌ No se pudo abrir ningún dispositivo")
            return
        
        # Paso 5: Obtener información del dispositivo
        print("\n5. Obteniendo información del dispositivo...")
        width = c_long(0)
        height = c_long(0)
        err = sgfp.GetDeviceInfo(width, height)
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"   ❌ Error en GetDeviceInfo(): {err}")
            print("   💡 Código de error 2 = SGFDX_ERROR_FUNCTION_FAILED")
            print("   💡 Esto puede significar:")
            print("      - El dispositivo no responde")
            print("      - Driver no instalado correctamente")
            print("      - Dispositivo ocupado por otro proceso")
            return
        
        print(f"   ✅ Dimensiones obtenidas: {width.value}x{height.value}")
        
        # Paso 6: Control de LED
        print("\n6. Probando control de LED...")
        try:
            err = sgfp.SetLedOn(True)
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print("   ✅ LED encendido")
                time.sleep(1)
                err = sgfp.SetLedOn(False)
                if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                    print("   ✅ LED apagado")
                else:
                    print(f"   ⚠️ Error al apagar LED: {err}")
            else:
                print(f"   ⚠️ Error al encender LED: {err}")
        except Exception as e:
            print(f"   ⚠️ Error en control de LED: {e}")
        
        # Paso 7: Preparar captura
        print("\n7. Preparando captura de imagen...")
        buffer_size = width.value * height.value
        imageBuffer = bytearray(buffer_size)
        print(f"   ✅ Buffer creado: {buffer_size} bytes")
        
        # Paso 8: Intentar captura
        print("\n8. Intentando captura de imagen...")
        print("   💡 Coloque el dedo en el sensor ahora...")
        
        # Encender LED
        sgfp.SetLedOn(True)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            print(f"   Intento {attempt + 1}/{max_attempts}")
            err = sgfp.GetImage(imageBuffer)
            
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print("   ✅ ¡Imagen capturada exitosamente!")
                break
            elif err == 2:  # SGFDX_ERROR_FUNCTION_FAILED
                print(f"   ❌ Error de función (código 2)")
                print("   💡 Posibles causas:")
                print("      - No hay dedo en el sensor")
                print("      - Dedo mal posicionado")
                print("      - Sensor sucio")
                print("      - Presión insuficiente")
            else:
                print(f"   ❌ Error inesperado: {err}")
            
            if attempt < max_attempts - 1:
                print("   ⏳ Esperando 2 segundos...")
                time.sleep(2)
        
        # Apagar LED
        sgfp.SetLedOn(False)
        
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"\n❌ Captura falló después de {max_attempts} intentos")
            print("\n🔧 SOLUCIONES SUGERIDAS:")
            print("1. Asegúrese de que su dedo esté limpio y seco")
            print("2. Presione firmemente el dedo en el centro del sensor")
            print("3. Mantenga el dedo inmóvil durante la captura")
            print("4. Verifique que el sensor esté limpio")
            print("5. Intente con un dedo diferente")
        else:
            print(f"\n✅ ¡DIAGNÓSTICO EXITOSO!")
            print(f"   Imagen capturada: {len(imageBuffer)} bytes")
        
        # Paso 9: Limpiar
        print("\n9. Limpiando recursos...")
        try:
            sgfp.CloseDevice()
            print("   ✅ Dispositivo cerrado")
        except:
            print("   ⚠️ Error al cerrar dispositivo")
            
    except Exception as e:
        print(f"\n❌ Error crítico: {str(e)}")
        print(f"   Tipo: {type(e).__name__}")
    
    print("\n🏁 Diagnóstico completado")

if __name__ == "__main__":
    diagnosticar_captura() 