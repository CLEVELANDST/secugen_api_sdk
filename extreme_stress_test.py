#!/usr/bin/env python3
"""
Prueba de Stress Extrema para API de Huellas Digitales
Incluye captura de huellas, control de LED y pruebas de resistencia
"""

import requests
import time
import json
import threading
import sys
from datetime import datetime
import concurrent.futures

class ExtremeStressTest:
    def __init__(self, base_url="http://localhost:5500"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 15
        self.results = []
        self.lock = threading.Lock()
        
    def log(self, message):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_api_health(self):
        """Verificar salud de la API"""
        try:
            response = self.session.post(f"{self.base_url}/initialize")
            return response.status_code == 200
        except:
            return False
    
    def capture_fingerprint_stress(self, test_id):
        """Capturar huella con stress"""
        try:
            data = {"save_image": False, "create_template": False}
            response = self.session.post(f"{self.base_url}/capturar-huella", json=data)
            
            with self.lock:
                result = {
                    'test_id': test_id,
                    'timestamp': datetime.now(),
                    'success': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds(),
                    'endpoint': 'capturar-huella'
                }
                self.results.append(result)
                
            return response.status_code == 200
        except Exception as e:
            with self.lock:
                result = {
                    'test_id': test_id,
                    'timestamp': datetime.now(),
                    'success': False,
                    'error': str(e),
                    'endpoint': 'capturar-huella'
                }
                self.results.append(result)
            return False
    
    def led_control_stress(self, test_id, state):
        """Control de LED con stress"""
        try:
            data = {"state": state}
            response = self.session.post(f"{self.base_url}/led", json=data)
            
            with self.lock:
                result = {
                    'test_id': test_id,
                    'timestamp': datetime.now(),
                    'success': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds(),
                    'endpoint': 'led'
                }
                self.results.append(result)
                
            return response.status_code == 200
        except Exception as e:
            with self.lock:
                result = {
                    'test_id': test_id,
                    'timestamp': datetime.now(),
                    'success': False,
                    'error': str(e),
                    'endpoint': 'led'
                }
                self.results.append(result)
            return False
    
    def initialize_stress(self, test_id):
        """Inicialización con stress"""
        try:
            response = self.session.post(f"{self.base_url}/initialize")
            
            with self.lock:
                result = {
                    'test_id': test_id,
                    'timestamp': datetime.now(),
                    'success': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds(),
                    'endpoint': 'initialize'
                }
                self.results.append(result)
                
            return response.status_code == 200
        except Exception as e:
            with self.lock:
                result = {
                    'test_id': test_id,
                    'timestamp': datetime.now(),
                    'success': False,
                    'error': str(e),
                    'endpoint': 'initialize'
                }
                self.results.append(result)
            return False
    
    def run_massive_api_stress(self, num_tests=100):
        """Prueba masiva de API con múltiples hilos"""
        self.log(f"🚀 INICIANDO PRUEBA DE STRESS EXTREMA - {num_tests} pruebas")
        self.log("=" * 60)
        
        # Verificar que la API esté funcionando
        if not self.test_api_health():
            self.log("❌ La API no está disponible")
            return
        
        # Ejecutar pruebas con ThreadPoolExecutor para concurrencia
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for i in range(num_tests):
                # Alternar entre diferentes tipos de pruebas
                if i % 4 == 0:
                    future = executor.submit(self.initialize_stress, i)
                elif i % 4 == 1:
                    future = executor.submit(self.led_control_stress, i, True)
                elif i % 4 == 2:
                    future = executor.submit(self.led_control_stress, i, False)
                else:
                    # Captura de huella solo ocasionalmente para no saturar el sensor
                    if i % 10 == 0:
                        future = executor.submit(self.capture_fingerprint_stress, i)
                    else:
                        future = executor.submit(self.initialize_stress, i)
                
                futures.append(future)
                
                # Mostrar progreso cada 10 pruebas
                if (i + 1) % 10 == 0:
                    self.log(f"📊 Enviadas {i + 1}/{num_tests} pruebas...")
            
            # Esperar a que todas las pruebas terminen
            self.log("⏳ Esperando que terminen todas las pruebas...")
            concurrent.futures.wait(futures)
        
        # Mostrar resultados
        self.show_detailed_results()
    
    def run_endurance_test(self, duration_minutes=5):
        """Prueba de resistencia por tiempo"""
        self.log(f"🏃 INICIANDO PRUEBA DE RESISTENCIA - {duration_minutes} minutos")
        self.log("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        test_count = 0
        
        while time.time() < end_time:
            test_count += 1
            
            # Alternar entre diferentes pruebas
            if test_count % 3 == 0:
                success = self.initialize_stress(test_count)
            elif test_count % 3 == 1:
                success = self.led_control_stress(test_count, True)
            else:
                success = self.led_control_stress(test_count, False)
            
            # Mostrar progreso cada 20 pruebas
            if test_count % 20 == 0:
                elapsed = time.time() - start_time
                remaining = (end_time - time.time()) / 60
                self.log(f"📊 Prueba {test_count} - {elapsed:.1f}s transcurridos - {remaining:.1f}m restantes")
            
            # Pausa pequeña para no saturar completamente
            time.sleep(0.1)
        
        self.log(f"✅ Prueba de resistencia completada: {test_count} pruebas en {duration_minutes} minutos")
        self.show_detailed_results()
    
    def show_detailed_results(self):
        """Mostrar resultados detallados"""
        if not self.results:
            self.log("❌ No hay resultados para mostrar")
            return
        
        # Estadísticas generales
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100
        
        # Estadísticas por endpoint
        endpoints = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = {'total': 0, 'success': 0, 'times': []}
            endpoints[endpoint]['total'] += 1
            if result['success']:
                endpoints[endpoint]['success'] += 1
            if 'response_time' in result:
                endpoints[endpoint]['times'].append(result['response_time'])
        
        # Mostrar resultados
        self.log("\n" + "=" * 60)
        self.log("📊 RESULTADOS DETALLADOS DE PRUEBA DE STRESS")
        self.log("=" * 60)
        self.log(f"🎯 Total de pruebas: {total_tests}")
        self.log(f"✅ Pruebas exitosas: {successful_tests}")
        self.log(f"❌ Pruebas fallidas: {failed_tests}")
        self.log(f"📈 Tasa de éxito: {success_rate:.1f}%")
        
        self.log("\n📋 ESTADÍSTICAS POR ENDPOINT:")
        for endpoint, stats in endpoints.items():
            endpoint_success_rate = (stats['success'] / stats['total']) * 100
            avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
            min_time = min(stats['times']) if stats['times'] else 0
            max_time = max(stats['times']) if stats['times'] else 0
            
            self.log(f"  🔧 {endpoint}:")
            self.log(f"    - Total: {stats['total']}")
            self.log(f"    - Éxito: {stats['success']} ({endpoint_success_rate:.1f}%)")
            self.log(f"    - Tiempo promedio: {avg_time:.3f}s")
            self.log(f"    - Tiempo min/max: {min_time:.3f}s / {max_time:.3f}s")
        
        self.log("\n🎭 EVALUACIÓN GENERAL:")
        if success_rate >= 95:
            self.log("🌟 EXCELENTE: Sistema extremadamente robusto!")
        elif success_rate >= 85:
            self.log("🎉 MUY BUENO: Sistema muy estable bajo stress!")
        elif success_rate >= 70:
            self.log("👍 BUENO: Sistema estable con stress moderado")
        elif success_rate >= 50:
            self.log("⚠️ REGULAR: Sistema tiene dificultades bajo stress")
        else:
            self.log("❌ CRÍTICO: Sistema no soporta bien el stress")
        
        self.log("=" * 60)

def main():
    print("🔥 PRUEBA DE STRESS EXTREMA PARA API DE HUELLAS")
    print("=" * 70)
    
    tester = ExtremeStressTest()
    
    # Verificar que la API esté funcionando
    if not tester.test_api_health():
        print("❌ La API no está disponible. Verifica que esté ejecutándose.")
        sys.exit(1)
    
    print("\n🔧 OPCIONES DE PRUEBA EXTREMA:")
    print("1. Prueba Masiva (100 pruebas concurrentes)")
    print("2. Prueba Masiva Extrema (250 pruebas concurrentes)")
    print("3. Prueba de Resistencia (5 minutos)")
    print("4. Prueba de Resistencia Extrema (10 minutos)")
    print("5. Prueba Rápida (50 pruebas)")
    
    try:
        choice = input("\nElige una opción (1-5): ").strip()
        
        if choice == "1":
            tester.run_massive_api_stress(100)
        elif choice == "2":
            tester.run_massive_api_stress(250)
        elif choice == "3":
            tester.run_endurance_test(5)
        elif choice == "4":
            tester.run_endurance_test(10)
        elif choice == "5":
            tester.run_massive_api_stress(50)
        else:
            print("❌ Opción inválida")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⛔ Prueba interrumpida por el usuario")
        if tester.results:
            tester.show_detailed_results()
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")

if __name__ == "__main__":
    main() 