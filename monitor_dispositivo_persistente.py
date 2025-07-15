#!/usr/bin/env python3
"""
MONITOR DISPOSITIVO PERSISTENTE - SecuGen
========================================
Script para monitorear el lector SecuGen usando identificadores persistentes
y reiniciarlo automáticamente cuando sea necesario.
"""

import os
import time
import subprocess
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configuración
CONFIG = {
    'persistent_device': '/dev/secugen_device',
    'vendor_id': '1162',
    'product_id': '2201',
    'check_interval': 10,  # segundos
    'max_retries': 3,
    'log_file': 'logs/monitor_dispositivo.log',
    'reset_script': 'reset_usb_device.py'
}

# Configurar logging
def setup_logging():
    """Configurar el sistema de logging"""
    log_dir = Path(CONFIG['log_file']).parent
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(CONFIG['log_file']),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def run_command(cmd, timeout=10):
    """Ejecutar comando y retornar resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_persistent_device():
    """Verificar que el dispositivo persistente esté funcionando"""
    logger = logging.getLogger(__name__)
    
    # Verificar que el symlink existe
    if not os.path.exists(CONFIG['persistent_device']):
        logger.error(f"Symlink persistente no existe: {CONFIG['persistent_device']}")
        return False
    
    # Verificar que el symlink apunta a un dispositivo válido
    try:
        target = os.readlink(CONFIG['persistent_device'])
        if not os.path.exists(target):
            logger.error(f"Target del symlink no existe: {target}")
            return False
    except Exception as e:
        logger.error(f"Error leyendo symlink: {e}")
        return False
    
    # Verificar que el dispositivo está en lsusb
    success, output, _ = run_command(f"lsusb | grep '{CONFIG['vendor_id']}:{CONFIG['product_id']}'")
    if not success or not output:
        logger.error("Dispositivo no encontrado en lsusb")
        return False
    
    # Verificar permisos de acceso
    if not (os.access(CONFIG['persistent_device'], os.R_OK) and 
            os.access(CONFIG['persistent_device'], os.W_OK)):
        logger.warning("Permisos de acceso insuficientes")
        return False
    
    return True

def check_sdk_connection():
    """Verificar que el SDK puede conectarse al dispositivo"""
    logger = logging.getLogger(__name__)
    
    try:
        # Importar SDK
        from sdk import PYSGFPLib
        from python.sgfdxerrorcode import SGFDxErrorCode
        
        sgfp = PYSGFPLib()
        
        # Create y Init
        err = sgfp.Create()
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            logger.error(f"SDK Create() falló: {err}")
            return False
            
        err = sgfp.Init(1)
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            logger.error(f"SDK Init() falló: {err}")
            return False
            
        # Probar OpenDevice
        for device_id in range(4):
            err = sgfp.OpenDevice(device_id)
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                logger.info(f"SDK OpenDevice({device_id}) exitoso")
                sgfp.CloseDevice()
                return True
            
        logger.error("SDK no puede abrir el dispositivo")
        return False
        
    except Exception as e:
        logger.error(f"Error probando SDK: {e}")
        return False

def reset_device():
    """Reiniciar el dispositivo usando el script de reset"""
    logger = logging.getLogger(__name__)
    
    if not os.path.exists(CONFIG['reset_script']):
        logger.error(f"Script de reset no encontrado: {CONFIG['reset_script']}")
        return False
    
    logger.info("Iniciando reset del dispositivo...")
    
    # Ejecutar script de reset
    success, output, error = run_command(f"sudo python3 {CONFIG['reset_script']}", timeout=30)
    
    if success:
        logger.info("Reset del dispositivo completado exitosamente")
        return True
    else:
        logger.error(f"Error en reset del dispositivo: {error}")
        return False

def recreate_persistent_device():
    """Recrear el dispositivo persistente si es necesario"""
    logger = logging.getLogger(__name__)
    
    if os.path.exists('crear_symlink_persistente.sh'):
        logger.info("Recreando dispositivo persistente...")
        success, output, error = run_command("sudo ./crear_symlink_persistente.sh", timeout=20)
        
        if success:
            logger.info("Dispositivo persistente recreado exitosamente")
            return True
        else:
            logger.error(f"Error recreando dispositivo persistente: {error}")
            return False
    else:
        logger.error("Script de creación de symlink no encontrado")
        return False

def monitor_device():
    """Función principal de monitoreo"""
    logger = logging.getLogger(__name__)
    
    logger.info("🔍 Iniciando monitoreo del dispositivo SecuGen persistente")
    logger.info(f"📍 Dispositivo: {CONFIG['persistent_device']}")
    logger.info(f"⏰ Intervalo: {CONFIG['check_interval']} segundos")
    
    consecutive_failures = 0
    last_check_time = time.time()
    
    while True:
        try:
            current_time = time.time()
            
            # Verificar dispositivo persistente
            device_ok = check_persistent_device()
            
            if device_ok:
                # Verificar conexión SDK
                sdk_ok = check_sdk_connection()
                
                if sdk_ok:
                    if consecutive_failures > 0:
                        logger.info("✅ Dispositivo recuperado exitosamente")
                        consecutive_failures = 0
                    
                    # Log de estado cada 10 minutos
                    if current_time - last_check_time > 600:  # 10 minutos
                        logger.info(f"✅ Estado OK - Dispositivo: {CONFIG['persistent_device']}")
                        last_check_time = current_time
                else:
                    consecutive_failures += 1
                    logger.warning(f"⚠️ SDK no puede conectarse (intento {consecutive_failures}/{CONFIG['max_retries']})")
                    
                    if consecutive_failures >= CONFIG['max_retries']:
                        logger.error("❌ Múltiples fallos de SDK, iniciando reset...")
                        
                        if reset_device():
                            consecutive_failures = 0
                        else:
                            logger.error("❌ Reset falló, intentando recrear dispositivo persistente...")
                            if recreate_persistent_device():
                                consecutive_failures = 0
                            else:
                                logger.error("❌ No se pudo recuperar el dispositivo")
            else:
                consecutive_failures += 1
                logger.warning(f"⚠️ Dispositivo persistente no funciona (intento {consecutive_failures}/{CONFIG['max_retries']})")
                
                if consecutive_failures >= CONFIG['max_retries']:
                    logger.error("❌ Múltiples fallos de dispositivo, recreando...")
                    
                    if recreate_persistent_device():
                        consecutive_failures = 0
                    else:
                        logger.error("❌ No se pudo recrear el dispositivo persistente")
            
            # Esperar antes de la siguiente verificación
            time.sleep(CONFIG['check_interval'])
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitoreo interrumpido por el usuario")
            break
        except Exception as e:
            logger.error(f"❌ Error inesperado en monitoreo: {e}")
            time.sleep(CONFIG['check_interval'])

def show_status():
    """Mostrar estado actual del dispositivo"""
    logger = logging.getLogger(__name__)
    
    print("🔍 ESTADO DEL DISPOSITIVO SECUGEN PERSISTENTE")
    print("=" * 50)
    
    # Verificar dispositivo persistente
    device_ok = check_persistent_device()
    print(f"📍 Dispositivo persistente: {'✅' if device_ok else '❌'}")
    
    if device_ok:
        try:
            target = os.readlink(CONFIG['persistent_device'])
            print(f"🔗 Apunta a: {target}")
        except:
            print("🔗 Error leyendo symlink")
    
    # Verificar SDK
    sdk_ok = check_sdk_connection()
    print(f"🔌 Conexión SDK: {'✅' if sdk_ok else '❌'}")
    
    # Verificar lsusb
    success, output, _ = run_command(f"lsusb | grep '{CONFIG['vendor_id']}:{CONFIG['product_id']}'")
    print(f"📋 Dispositivo USB: {'✅' if success else '❌'}")
    if success:
        print(f"   {output.strip()}")
    
    # Estado general
    overall_status = device_ok and sdk_ok
    print(f"\n🎯 Estado general: {'✅ FUNCIONAL' if overall_status else '❌ PROBLEMAS'}")

def main():
    """Función principal"""
    logger = setup_logging()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--status':
            show_status()
            return
        elif command == '--reset':
            if reset_device():
                print("✅ Reset completado")
            else:
                print("❌ Reset falló")
            return
        elif command == '--recreate':
            if recreate_persistent_device():
                print("✅ Dispositivo persistente recreado")
            else:
                print("❌ Error recreando dispositivo")
            return
        elif command == '--help':
            print("📋 USO:")
            print("  python3 monitor_dispositivo_persistente.py          # Monitoreo continuo")
            print("  python3 monitor_dispositivo_persistente.py --status # Mostrar estado")
            print("  python3 monitor_dispositivo_persistente.py --reset  # Reset manual")
            print("  python3 monitor_dispositivo_persistente.py --recreate # Recrear symlink")
            return
    
    # Monitoreo continuo por defecto
    monitor_device()

if __name__ == "__main__":
    main() 