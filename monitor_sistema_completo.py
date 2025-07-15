#!/usr/bin/env python3
"""
MONITOR SISTEMA COMPLETO - Prevención y Solución Automática
==========================================================
Este script previene y soluciona automáticamente todos los problemas comunes:
- Errores de sintaxis en Python
- Error 2 del SDK SecuGen
- Puertos ocupados
- Dispositivos USB inconsistentes
- Procesos colgados

Ejecutar como servicio para monitoreo continuo.
"""

import subprocess
import os
import time
import sys
import signal
import psutil
import ast
import py_compile
from pathlib import Path
import threading
import json
import logging
from datetime import datetime

# Configuración
CONFIG = {
    'app_file': 'app.py',
    'flask_port': 5000,
    'check_interval': 30,  # segundos
    'max_retries': 3,
    'log_file': 'logs/monitor_sistema.log',
    'secugen_vendor_id': '1162',
    'secugen_product_id': '2201',
    'persistent_symlink': '/dev/secugen_device'
}

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG['log_file']),
        logging.StreamHandler()
    ]
)

class SistemaMonitor:
    def __init__(self):
        self.running = False
        self.flask_process = None
        self.stats = {
            'errores_sintaxis': 0,
            'errores_sdk': 0,
            'puertos_ocupados': 0,
            'resets_usb': 0,
            'ultimo_check': None
        }
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
        
    def run_command(self, cmd, description="", timeout=10):
        """Ejecutar comando con timeout y logging"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, 
                text=True, timeout=timeout
            )
            
            if result.returncode == 0:
                logging.info(f"✅ {description}: {cmd}")
                return True, result.stdout, result.stderr
            else:
                logging.warning(f"⚠️ {description} falló: {cmd}")
                return False, result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            logging.error(f"⏱️ Timeout en {description}: {cmd}")
            return False, "", "Timeout"
        except Exception as e:
            logging.error(f"❌ Error en {description}: {e}")
            return False, "", str(e)
    
    def check_python_syntax(self):
        """Verificar sintaxis de Python en app.py"""
        self.print_header("VERIFICACIÓN DE SINTAXIS PYTHON")
        
        try:
            # Verificar sintaxis compilando
            py_compile.compile(CONFIG['app_file'], doraise=True)
            
            # Verificar AST
            with open(CONFIG['app_file'], 'r') as f:
                code = f.read()
                ast.parse(code)
                
            print("✅ Sintaxis Python correcta")
            return True
            
        except py_compile.PyCompileError as e:
            print(f"❌ Error de compilación: {e}")
            self.stats['errores_sintaxis'] += 1
            return False
            
        except SyntaxError as e:
            print(f"❌ Error de sintaxis: {e}")
            self.stats['errores_sintaxis'] += 1
            return False
            
        except Exception as e:
            print(f"❌ Error verificando sintaxis: {e}")
            return False
    
    def fix_syntax_errors(self):
        """Intentar corregir errores de sintaxis comunes"""
        print("🔧 Intentando corregir errores de sintaxis...")
        
        # Restaurar desde backup si existe
        backup_file = 'app_backup.py'
        if os.path.exists(backup_file):
            print(f"📁 Restaurando desde backup: {backup_file}")
            success, _, _ = self.run_command(
                f"cp {backup_file} {CONFIG['app_file']}", 
                "Restaurar backup"
            )
            if success:
                return self.check_python_syntax()
        
        return False
    
    def check_flask_port(self):
        """Verificar si el puerto Flask está disponible"""
        self.print_header("VERIFICACIÓN DE PUERTO FLASK")
        
        try:
            # Buscar procesos usando el puerto
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python3' and proc.info['cmdline']:
                        if 'app.py' in ' '.join(proc.info['cmdline']):
                            print(f"⚠️ Proceso Flask encontrado: PID {proc.info['pid']}")
                            return False, proc.info['pid']
                except:
                    continue
                    
            # Verificar puerto con netstat
            success, output, _ = self.run_command(
                f"netstat -tuln | grep ':{CONFIG['flask_port']}'", 
                "Verificar puerto", 
                show_output=False
            )
            
            if success and output:
                print(f"❌ Puerto {CONFIG['flask_port']} ocupado")
                self.stats['puertos_ocupados'] += 1
                return False, None
            else:
                print(f"✅ Puerto {CONFIG['flask_port']} disponible")
                return True, None
                
        except Exception as e:
            print(f"❌ Error verificando puerto: {e}")
            return False, None
    
    def kill_flask_processes(self, target_pid=None):
        """Terminar procesos Flask colgados"""
        print("🔪 Terminando procesos Flask...")
        
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python3' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'app.py' in cmdline or (target_pid and proc.info['pid'] == target_pid):
                        print(f"🔪 Terminando proceso: PID {proc.info['pid']}")
                        proc.terminate()
                        killed_count += 1
                        
                        # Esperar y forzar si es necesario
                        time.sleep(2)
                        if proc.is_running():
                            proc.kill()
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        print(f"✅ {killed_count} procesos terminados")
        return killed_count > 0
    
    def check_secugen_device(self):
        """Verificar estado del dispositivo SecuGen"""
        self.print_header("VERIFICACIÓN DISPOSITIVO SECUGEN")
        
        # Verificar por lsusb
        success, output, _ = self.run_command(
            f"lsusb | grep '{CONFIG['secugen_vendor_id']}:{CONFIG['secugen_product_id']}'", 
            "Buscar dispositivo SecuGen",
            show_output=False
        )
        
        if not success or not output:
            print("❌ Dispositivo SecuGen no detectado")
            return False
            
        print(f"✅ Dispositivo encontrado: {output.strip()}")
        
        # Verificar symlink persistente
        if os.path.exists(CONFIG['persistent_symlink']):
            print(f"✅ Symlink persistente: {CONFIG['persistent_symlink']}")
        else:
            print("⚠️ Symlink persistente no encontrado")
            
        return True
    
    def reset_secugen_device(self):
        """Resetear dispositivo SecuGen usando métodos del script existente"""
        print("🔄 Reseteando dispositivo SecuGen...")
        
        try:
            # Ejecutar script de reset
            success, output, error = self.run_command(
                "python3 reset_usb_device.py", 
                "Reset dispositivo USB",
                timeout=30
            )
            
            if success:
                print("✅ Reset USB completado")
                self.stats['resets_usb'] += 1
                return True
            else:
                print(f"❌ Reset USB falló: {error}")
                return False
                
        except Exception as e:
            print(f"❌ Error en reset USB: {e}")
            return False
    
    def test_sdk_connection(self):
        """Probar conexión del SDK"""
        print("🔌 Probando conexión SDK...")
        
        try:
            # Importar SDK
            from sdk import PYSGFPLib
            from python.sgfdxerrorcode import SGFDxErrorCode
            
            sgfp = PYSGFPLib()
            
            # Crear instancia
            err = sgfp.Create()
            if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"❌ Create() falló: {err}")
                return False
                
            # Inicializar
            err = sgfp.Init(1)
            if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"❌ Init() falló: {err}")
                return False
                
            # Probar abrir dispositivo
            err = sgfp.OpenDevice(0)
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print("✅ OpenDevice() exitoso")
                sgfp.CloseDevice()
                return True
            else:
                print(f"❌ OpenDevice() falló: {err}")
                return False
                
        except Exception as e:
            print(f"❌ Error probando SDK: {e}")
            return False
    
    def start_flask_app(self):
        """Iniciar aplicación Flask"""
        print("🚀 Iniciando aplicación Flask...")
        
        try:
            # Verificar sintaxis primero
            if not self.check_python_syntax():
                if not self.fix_syntax_errors():
                    print("❌ No se pudo corregir errores de sintaxis")
                    return False
            
            # Iniciar Flask en background
            self.flask_process = subprocess.Popen(
                ['python3', CONFIG['app_file']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Esperar inicio
            time.sleep(5)
            
            # Verificar que está corriendo
            if self.flask_process.poll() is None:
                print("✅ Flask iniciado correctamente")
                return True
            else:
                stdout, stderr = self.flask_process.communicate()
                print(f"❌ Flask falló al iniciar: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando Flask: {e}")
            return False
    
    def full_system_check(self):
        """Verificación completa del sistema"""
        self.print_header("VERIFICACIÓN COMPLETA DEL SISTEMA")
        
        issues_found = []
        
        # 1. Verificar sintaxis Python
        if not self.check_python_syntax():
            issues_found.append("syntax")
            
        # 2. Verificar puerto Flask
        port_available, pid = self.check_flask_port()
        if not port_available:
            issues_found.append("port")
            
        # 3. Verificar dispositivo SecuGen
        if not self.check_secugen_device():
            issues_found.append("device")
            
        # 4. Probar SDK si dispositivo está disponible
        if "device" not in issues_found:
            if not self.test_sdk_connection():
                issues_found.append("sdk")
        
        return issues_found
    
    def auto_fix_issues(self, issues):
        """Corregir problemas automáticamente"""
        self.print_header("CORRECCIÓN AUTOMÁTICA DE PROBLEMAS")
        
        fixed = []
        
        for issue in issues:
            if issue == "syntax":
                if self.fix_syntax_errors():
                    fixed.append("syntax")
                    
            elif issue == "port":
                if self.kill_flask_processes():
                    fixed.append("port")
                    
            elif issue == "device" or issue == "sdk":
                if self.reset_secugen_device():
                    fixed.append("device")
                    fixed.append("sdk")
        
        return fixed
    
    def monitor_loop(self):
        """Bucle principal de monitoreo"""
        print("🔄 Iniciando monitoreo del sistema...")
        
        while self.running:
            try:
                # Verificar sistema
                issues = self.full_system_check()
                
                if issues:
                    print(f"⚠️ Problemas detectados: {', '.join(issues)}")
                    
                    # Intentar corregir
                    fixed = self.auto_fix_issues(issues)
                    
                    if fixed:
                        print(f"✅ Problemas corregidos: {', '.join(fixed)}")
                    else:
                        print("❌ No se pudieron corregir algunos problemas")
                else:
                    print("✅ Sistema funcionando correctamente")
                
                self.stats['ultimo_check'] = datetime.now().isoformat()
                
                # Esperar antes del siguiente check
                time.sleep(CONFIG['check_interval'])
                
            except KeyboardInterrupt:
                print("\n⏹️ Monitoreo detenido por el usuario")
                break
            except Exception as e:
                logging.error(f"❌ Error en monitoreo: {e}")
                time.sleep(CONFIG['check_interval'])
    
    def start_monitor(self):
        """Iniciar monitoreo"""
        self.running = True
        
        # Crear directorio de logs
        os.makedirs(os.path.dirname(CONFIG['log_file']), exist_ok=True)
        
        # Verificación inicial
        print("🔍 Verificación inicial del sistema...")
        issues = self.full_system_check()
        
        if issues:
            print("🔧 Corrigiendo problemas iniciales...")
            self.auto_fix_issues(issues)
        
        # Iniciar Flask si no está corriendo
        port_available, _ = self.check_flask_port()
        if port_available:
            self.start_flask_app()
        
        # Iniciar monitoreo
        self.monitor_loop()
    
    def stop_monitor(self):
        """Detener monitoreo"""
        self.running = False
        
        if self.flask_process:
            self.flask_process.terminate()
            
    def show_stats(self):
        """Mostrar estadísticas"""
        print("\n📊 ESTADÍSTICAS DEL SISTEMA:")
        print(f"   Errores de sintaxis corregidos: {self.stats['errores_sintaxis']}")
        print(f"   Errores de SDK corregidos: {self.stats['errores_sdk']}")
        print(f"   Puertos liberados: {self.stats['puertos_ocupados']}")
        print(f"   Resets USB realizados: {self.stats['resets_usb']}")
        print(f"   Último check: {self.stats['ultimo_check']}")

def main():
    monitor = SistemaMonitor()
    
    def signal_handler(signum, frame):
        print("\n🛑 Deteniendo monitor...")
        monitor.stop_monitor()
        monitor.show_stats()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        monitor.start_monitor()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        monitor.show_stats()
        sys.exit(1)

if __name__ == "__main__":
    main() 