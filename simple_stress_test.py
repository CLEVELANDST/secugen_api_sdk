#!/usr/bin/env python3
"""
Prueba de Stress Simple para API de Huellas Digitales
Versión robusta que maneja problemas de dispositivos USB
"""

import requests
import time
import json
import sys
from datetime import datetime

class SimpleStressTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        self.captured_templates = {}
        self.results = []
        
    def log(self, message):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_api_health(self):
        """Verificar que la API esté funcionando"""
        try:
            response = self.session.post(f"{self.base_url}/initialize")
            if response.status_code == 200:
                self.log("✅ API funcionando correctamente")
                return True
            else:
                self.log(f"❌ API con problemas: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ No se puede conectar a la API: {e}")
            return False
    
    def capture_fingerprint(self, template_id=None):
        """Capturar huella digital"""
        try:
            data = {
                "save_image": False,
                "create_template": False  # Deshabilitamos template por ahora
            }
            if template_id:
                data["template_id"] = template_id
            
            self.log(f"🔍 Capturando huella {template_id if template_id else 'sin ID'}...")
            
            response = self.session.post(f"{self.base_url}/capturar-huella", json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.log(f"✅ Huella capturada exitosamente")
                    return result
                else:
                    self.log(f"❌ Error en captura: {result.get('error', 'Unknown')}")
                    return None
            else:
                self.log(f"❌ Error HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            self.log(f"❌ Error capturando huella: {e}")
            return None
    
    def test_led_control(self):
        """Probar control del LED"""
        try:
            # Encender LED
            response = self.session.post(f"{self.base_url}/led", json={"state": True})
            if response.status_code == 200:
                self.log("✅ LED encendido")
                time.sleep(0.5)
                
                # Apagar LED
                response = self.session.post(f"{self.base_url}/led", json={"state": False})
                if response.status_code == 200:
                    self.log("✅ LED apagado")
                    return True
                    
            self.log("❌ Error controlando LED")
            return False
            
        except Exception as e:
            self.log(f"❌ Error en control LED: {e}")
            return False
    
    def run_capture_stress_test(self, num_tests=10):
        """Ejecutar prueba de stress de captura"""
        self.log(f"🚀 INICIANDO PRUEBA DE STRESS - {num_tests} capturas")
        self.log("=" * 50)
        
        success_count = 0
        failure_count = 0
        response_times = []
        
        for i in range(num_tests):
            self.log(f"\n--- Prueba {i+1}/{num_tests} ---")
            
            # Verificar salud de la API
            if not self.test_api_health():
                self.log("❌ API no disponible, saltando prueba")
                failure_count += 1
                time.sleep(2)
                continue
            
            # Probar control LED
            if not self.test_led_control():
                self.log("⚠️ LED con problemas, pero continuando...")
            
            # Capturar huella
            start_time = time.time()
            
            input(f"🖐️ Pon tu dedo en el sensor para la captura {i+1} y presiona Enter...")
            
            result = self.capture_fingerprint(f"stress_test_{i+1}")
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if result:
                success_count += 1
                self.log(f"✅ Prueba {i+1} exitosa ({response_time:.2f}s)")
            else:
                failure_count += 1
                self.log(f"❌ Prueba {i+1} falló ({response_time:.2f}s)")
                
                # Reintentar inicialización si falla
                self.log("🔄 Reintentando inicialización...")
                self.session.post(f"{self.base_url}/initialize")
                time.sleep(1)
            
            # Pausa entre pruebas
            if i < num_tests - 1:
                self.log("⏳ Esperando 3 segundos...")
                time.sleep(3)
        
        # Mostrar resultados
        self.show_results(success_count, failure_count, response_times)
        
    def run_api_stress_test(self, num_tests=20):
        """Ejecutar prueba de stress sin interacción manual"""
        self.log(f"🚀 INICIANDO PRUEBA DE STRESS API - {num_tests} llamadas")
        self.log("=" * 50)
        
        success_count = 0
        failure_count = 0
        response_times = []
        
        for i in range(num_tests):
            self.log(f"--- API Test {i+1}/{num_tests} ---")
            
            start_time = time.time()
            
            # Alternar entre diferentes endpoints
            if i % 3 == 0:
                # Test initialize
                response = self.session.post(f"{self.base_url}/initialize")
            elif i % 3 == 1:
                # Test LED
                response = self.session.post(f"{self.base_url}/led", json={"state": True})
            else:
                # Test LED off
                response = self.session.post(f"{self.base_url}/led", json={"state": False})
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                success_count += 1
                self.log(f"✅ API Test {i+1} exitoso ({response_time:.2f}s)")
            else:
                failure_count += 1
                self.log(f"❌ API Test {i+1} falló ({response_time:.2f}s)")
            
            # Pausa breve
            time.sleep(0.5)
        
        # Mostrar resultados
        self.show_results(success_count, failure_count, response_times)
    
    def show_results(self, success_count, failure_count, response_times):
        """Mostrar resultados de la prueba"""
        total_tests = success_count + failure_count
        success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        self.log("\n" + "=" * 50)
        self.log("📊 RESULTADOS DE LA PRUEBA DE STRESS")
        self.log("=" * 50)
        self.log(f"✅ Pruebas exitosas: {success_count}")
        self.log(f"❌ Pruebas fallidas: {failure_count}")
        self.log(f"📈 Tasa de éxito: {success_rate:.1f}%")
        self.log(f"⏱️ Tiempo promedio: {avg_response_time:.2f}s")
        self.log(f"⚡ Tiempo mínimo: {min_response_time:.2f}s")
        self.log(f"🐌 Tiempo máximo: {max_response_time:.2f}s")
        self.log("=" * 50)
        
        if success_rate >= 80:
            self.log("🎉 EXCELENTE: Sistema funcionando muy bien!")
        elif success_rate >= 60:
            self.log("👍 BUENO: Sistema funcionando aceptablemente")
        elif success_rate >= 40:
            self.log("⚠️ REGULAR: Sistema con algunos problemas")
        else:
            self.log("❌ MALO: Sistema con muchos problemas")

def main():
    print("🧪 PRUEBA DE STRESS SIMPLE PARA API DE HUELLAS")
    print("=" * 60)
    
    tester = SimpleStressTest()
    
    # Verificar que la API esté funcionando
    if not tester.test_api_health():
        print("❌ La API no está disponible. Verifica que esté ejecutándose.")
        sys.exit(1)
    
    print("\n🔧 OPCIONES DE PRUEBA:")
    print("1. Prueba de Captura (Manual) - Requiere interacción")
    print("2. Prueba de API (Automática) - Sin interacción")
    print("3. Prueba Rápida - Solo 5 llamadas API")
    
    try:
        choice = input("\nElige una opción (1-3): ").strip()
        
        if choice == "1":
            num_tests = int(input("¿Cuántas capturas quieres realizar? (5-20): ") or "5")
            tester.run_capture_stress_test(min(max(num_tests, 5), 20))
        elif choice == "2":
            num_tests = int(input("¿Cuántas llamadas API quieres realizar? (10-50): ") or "20")
            tester.run_api_stress_test(min(max(num_tests, 10), 50))
        elif choice == "3":
            tester.run_api_stress_test(5)
        else:
            print("❌ Opción inválida")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⛔ Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    main() 