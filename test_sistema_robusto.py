#!/usr/bin/env python3
"""
TEST SISTEMA ROBUSTO - Verificación Completa
===========================================
Este script prueba todas las funcionalidades del sistema robusto
y verifica que los problemas comunes se previenen correctamente.
"""

import requests
import time
import subprocess
import os
import sys
import json
from datetime import datetime

class TestSistemaRobusto:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name, passed, message=""):
        """Registrar resultado de prueba"""
        result = {
            'test': test_name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"{status} - {test_name}")
        if message:
            print(f"        {message}")
    
    def run_command(self, cmd, description=""):
        """Ejecutar comando y retornar resultado"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)
    
    def test_scripts_existence(self):
        """Probar que los scripts existen y son ejecutables"""
        scripts = [
            'iniciar_sistema_robusto.sh',
            'parar_sistema.sh',
            'reset_usb_device.py',
            'monitor_sistema_completo.py'
        ]
        
        for script in scripts:
            if os.path.exists(script):
                if os.access(script, os.X_OK):
                    self.log_test(f"Script ejecutable: {script}", True)
                else:
                    self.log_test(f"Script ejecutable: {script}", False, "No tiene permisos de ejecución")
            else:
                self.log_test(f"Script existe: {script}", False, "Archivo no encontrado")
    
    def test_python_syntax(self):
        """Probar sintaxis de Python"""
        files = ['app.py', 'reset_usb_device.py', 'monitor_sistema_completo.py']
        
        for file in files:
            if os.path.exists(file):
                success, _, error = self.run_command(f"python3 -m py_compile {file}")
                self.log_test(f"Sintaxis Python: {file}", success, error if not success else "")
            else:
                self.log_test(f"Archivo existe: {file}", False, "Archivo no encontrado")
    
    def test_usb_device(self):
        """Probar dispositivo USB SecuGen"""
        # Verificar por lsusb
        success, output, _ = self.run_command("lsusb | grep '1162:2201'")
        self.log_test("Dispositivo USB detectado", success, output.strip() if success else "Dispositivo no encontrado")
        
        # Verificar symlink persistente
        if os.path.exists('/dev/secugen_device'):
            self.log_test("Symlink persistente", True, "/dev/secugen_device existe")
        else:
            self.log_test("Symlink persistente", False, "/dev/secugen_device no existe")
    
    def test_flask_server(self):
        """Probar servidor Flask"""
        try:
            # Verificar que el servidor responde
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.log_test("Servidor Flask responde", response.status_code == 200 or response.status_code == 404, 
                         f"Status: {response.status_code}")
            
            # Probar endpoint de inicialización
            response = requests.post(f"{self.base_url}/initialize", timeout=10)
            self.log_test("Endpoint /initialize", response.status_code == 200, 
                         f"Status: {response.status_code}")
            
            # Probar endpoint de LED
            response = requests.post(f"{self.base_url}/led", 
                                   json={'state': True}, 
                                   headers={'Content-Type': 'application/json'}, 
                                   timeout=10)
            self.log_test("Endpoint /led", response.status_code == 200, 
                         f"Status: {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            self.log_test("Servidor Flask responde", False, "No se puede conectar al servidor")
        except requests.exceptions.Timeout:
            self.log_test("Servidor Flask responde", False, "Timeout de conexión")
        except Exception as e:
            self.log_test("Servidor Flask responde", False, str(e))
    
    def test_port_availability(self):
        """Probar disponibilidad del puerto"""
        success, output, _ = self.run_command("netstat -tuln | grep ':5000'")
        self.log_test("Puerto 5000 en uso", success, "Puerto ocupado correctamente" if success else "Puerto no ocupado")
    
    def test_logs_directory(self):
        """Probar directorio de logs"""
        if os.path.exists('logs'):
            self.log_test("Directorio logs existe", True)
            
            # Verificar archivos de log
            log_files = ['app.log', 'sistema_robusto.log', 'flask_output.log']
            for log_file in log_files:
                path = os.path.join('logs', log_file)
                if os.path.exists(path):
                    self.log_test(f"Log file: {log_file}", True)
                else:
                    self.log_test(f"Log file: {log_file}", False, "Archivo no encontrado")
        else:
            self.log_test("Directorio logs existe", False, "Directorio no encontrado")
    
    def test_backup_files(self):
        """Probar archivos de backup"""
        if os.path.exists('app_backup.py'):
            self.log_test("Archivo backup existe", True)
            
            # Verificar que el backup es válido
            success, _, error = self.run_command("python3 -m py_compile app_backup.py")
            self.log_test("Backup syntax válida", success, error if not success else "")
        else:
            self.log_test("Archivo backup existe", False, "app_backup.py no encontrado")
    
    def test_udev_rules(self):
        """Probar reglas udev"""
        if os.path.exists('/etc/udev/rules.d/99SecuGen.rules'):
            self.log_test("Reglas udev instaladas", True)
        else:
            self.log_test("Reglas udev instaladas", False, "Reglas no instaladas")
        
        # Verificar archivo fuente
        if os.path.exists('docker/99SecuGen.rules'):
            self.log_test("Archivo reglas udev fuente", True)
        else:
            self.log_test("Archivo reglas udev fuente", False, "docker/99SecuGen.rules no encontrado")
    
    def test_reset_usb_functionality(self):
        """Probar funcionalidad de reset USB"""
        # Verificar que el script existe y es ejecutable
        if os.path.exists('reset_usb_device.py'):
            # Probar información del dispositivo (sin reset real)
            success, output, error = self.run_command("python3 -c 'from reset_usb_device import get_device_persistent_info; print(get_device_persistent_info())'")
            self.log_test("Reset USB - Info dispositivo", success, 
                         "Información obtenida correctamente" if success else error)
        else:
            self.log_test("Reset USB script existe", False, "reset_usb_device.py no encontrado")
    
    def test_process_management(self):
        """Probar gestión de procesos"""
        # Verificar procesos Flask
        success, output, _ = self.run_command("ps aux | grep '[p]ython3.*app.py'")
        self.log_test("Proceso Flask activo", success, "Proceso encontrado" if success else "Proceso no encontrado")
        
        # Verificar archivos PID
        if os.path.exists('logs/flask.pid'):
            self.log_test("Archivo PID Flask", True)
        else:
            self.log_test("Archivo PID Flask", False, "logs/flask.pid no encontrado")
    
    def test_dependencies(self):
        """Probar dependencias Python"""
        dependencies = ['flask', 'flask_cors', 'numpy', 'requests']
        
        for dep in dependencies:
            success, _, error = self.run_command(f"python3 -c 'import {dep}'")
            self.log_test(f"Dependencia: {dep}", success, error if not success else "")
    
    def test_sdk_functionality(self):
        """Probar funcionalidad del SDK"""
        try:
            # Probar importación del SDK
            success, output, error = self.run_command("python3 -c 'from sdk import PYSGFPLib; print(\"SDK importado correctamente\")'")
            self.log_test("SDK importación", success, error if not success else "")
            
            if success:
                # Probar creación de instancia
                success, output, error = self.run_command("python3 -c 'from sdk import PYSGFPLib; sgfp = PYSGFPLib(); print(\"Instancia creada\")'")
                self.log_test("SDK instancia", success, error if not success else "")
                
        except Exception as e:
            self.log_test("SDK funcionalidad", False, str(e))
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🧪 INICIANDO PRUEBAS DEL SISTEMA ROBUSTO")
        print("=" * 50)
        
        test_methods = [
            self.test_scripts_existence,
            self.test_python_syntax,
            self.test_usb_device,
            self.test_flask_server,
            self.test_port_availability,
            self.test_logs_directory,
            self.test_backup_files,
            self.test_udev_rules,
            self.test_reset_usb_functionality,
            self.test_process_management,
            self.test_dependencies,
            self.test_sdk_functionality
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(f"Error en {test_method.__name__}", False, str(e))
            print("-" * 30)
    
    def generate_report(self):
        """Generar reporte de pruebas"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        passed = sum(1 for result in self.test_results if result['passed'])
        failed = len(self.test_results) - passed
        
        print("\n" + "=" * 50)
        print("📊 REPORTE DE PRUEBAS")
        print("=" * 50)
        print(f"⏱️  Duración: {duration.total_seconds():.2f} segundos")
        print(f"✅ Pruebas pasadas: {passed}")
        print(f"❌ Pruebas fallidas: {failed}")
        print(f"📈 Porcentaje de éxito: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n🚨 PRUEBAS FALLIDAS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        # Guardar reporte en archivo
        report_file = f"logs/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('logs', exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': self.start_time.isoformat(),
                'duration': duration.total_seconds(),
                'passed': passed,
                'failed': failed,
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Reporte guardado en: {report_file}")
        
        return failed == 0

def main():
    """Función principal"""
    tester = TestSistemaRobusto()
    
    # Ejecutar pruebas
    tester.run_all_tests()
    
    # Generar reporte
    success = tester.generate_report()
    
    if success:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema robusto está funcionando correctamente")
        sys.exit(0)
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisa los errores arriba y ejecuta:")
        print("   ./parar_sistema.sh")
        print("   ./iniciar_sistema_robusto.sh")
        sys.exit(1)

if __name__ == "__main__":
    main() 