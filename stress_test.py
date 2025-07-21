#!/usr/bin/env python3
"""
Script de Stress Test para API de Comparación de Huellas Digitales
Realiza múltiples comparaciones de huellas para probar rendimiento y estabilidad
"""

import requests
import time
import json
import concurrent.futures
import statistics
from datetime import datetime
import threading
import argparse
import sys

class FingerprintStressTest:
    def __init__(self, base_url="http://localhost:5500"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        self.lock = threading.Lock()
        self.templates = {}
        
    def check_api_health(self):
        """Verificar que la API esté funcionando"""
        try:
            response = self.session.post(f"{self.base_url}/initialize")
            if response.status_code == 200:
                print("✅ API funcionando correctamente")
                return True
            else:
                print(f"❌ API no responde correctamente: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error al conectar con API: {e}")
            return False
    
    def capture_reference_fingerprints(self, num_references=3):
        """Capturar huellas de referencia para las pruebas"""
        print(f"\n📸 Capturando {num_references} huellas de referencia...")
        
        for i in range(num_references):
            print(f"\n🔍 Capturando huella de referencia {i+1}/{num_references}")
            input("Presiona ENTER cuando tengas el dedo en el sensor...")
            
            try:
                response = self.session.post(f"{self.base_url}/capturar-huella", json={
                    "save_image": False,
                    "create_template": True,
                    "template_id": f"ref_{i+1}"
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data', {}).get('template'):
                        self.templates[f"ref_{i+1}"] = data['data']['template']
                        print(f"✅ Huella de referencia {i+1} capturada y almacenada")
                    else:
                        print(f"❌ Error al capturar huella {i+1}: {data.get('error', 'Error desconocido')}")
                        return False
                else:
                    print(f"❌ Error HTTP {response.status_code} al capturar huella {i+1}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error al capturar huella {i+1}: {e}")
                return False
        
        print(f"\n✅ {len(self.templates)} huellas de referencia capturadas exitosamente")
        return True
    
    def single_comparison_test(self, template1_id, template2_id, test_id, security_level=1):
        """Realizar una única comparación de huellas"""
        start_time = time.time()
        
        try:
            response = self.session.post(f"{self.base_url}/comparar-huellas", json={
                "template1_id": template1_id,
                "template2_id": template2_id,
                "security_level": security_level
            })
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # ms
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'test_id': test_id,
                    'success': True,
                    'matched': data.get('matched', False),
                    'score': data.get('score', 0),
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat(),
                    'template1': template1_id,
                    'template2': template2_id
                }
            else:
                result = {
                    'test_id': test_id,
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'response_time': response_time,
                    'timestamp': datetime.now().isoformat(),
                    'template1': template1_id,
                    'template2': template2_id
                }
                
        except Exception as e:
            end_time = time.time()
            result = {
                'test_id': test_id,
                'success': False,
                'error': str(e),
                'response_time': (end_time - start_time) * 1000,
                'timestamp': datetime.now().isoformat(),
                'template1': template1_id,
                'template2': template2_id
            }
        
        with self.lock:
            self.results.append(result)
        
        return result
    
    def run_concurrent_tests(self, num_tests=100, num_threads=10):
        """Ejecutar pruebas concurrentes"""
        print(f"\n🚀 Iniciando prueba de stress: {num_tests} comparaciones con {num_threads} threads")
        
        template_ids = list(self.templates.keys())
        if len(template_ids) < 2:
            print("❌ Se necesitan al menos 2 templates para las pruebas")
            return False
        
        # Crear combinaciones de templates para probar
        test_combinations = []
        for i in range(num_tests):
            # Alternar entre comparaciones positivas (mismo template) y negativas (diferentes templates)
            if i % 2 == 0:
                # Comparación positiva (mismo template consigo mismo)
                template1 = template_ids[i % len(template_ids)]
                template2 = template1
            else:
                # Comparación negativa (diferentes templates)
                template1 = template_ids[i % len(template_ids)]
                template2 = template_ids[(i + 1) % len(template_ids)]
            
            test_combinations.append((template1, template2, i + 1))
        
        start_time = time.time()
        
        # Ejecutar pruebas concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for template1, template2, test_id in test_combinations:
                future = executor.submit(self.single_comparison_test, template1, template2, test_id)
                futures.append(future)
            
            # Mostrar progreso
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                completed += 1
                if completed % 10 == 0:
                    print(f"✅ Completadas {completed}/{num_tests} comparaciones")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n🎉 Prueba de stress completada en {total_time:.2f} segundos")
        return True
    
    def run_sequential_tests(self, num_tests=50):
        """Ejecutar pruebas secuenciales"""
        print(f"\n📊 Iniciando prueba secuencial: {num_tests} comparaciones")
        
        template_ids = list(self.templates.keys())
        if len(template_ids) < 2:
            print("❌ Se necesitan al menos 2 templates para las pruebas")
            return False
        
        start_time = time.time()
        
        for i in range(num_tests):
            # Alternar entre comparaciones positivas y negativas
            if i % 2 == 0:
                template1 = template_ids[i % len(template_ids)]
                template2 = template1
            else:
                template1 = template_ids[i % len(template_ids)]
                template2 = template_ids[(i + 1) % len(template_ids)]
            
            result = self.single_comparison_test(template1, template2, i + 1)
            
            if (i + 1) % 10 == 0:
                print(f"✅ Completadas {i + 1}/{num_tests} comparaciones")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n🎉 Prueba secuencial completada en {total_time:.2f} segundos")
        return True
    
    def analyze_results(self):
        """Analizar resultados de las pruebas"""
        if not self.results:
            print("❌ No hay resultados para analizar")
            return
        
        print(f"\n📊 ANÁLISIS DE RESULTADOS")
        print("=" * 50)
        
        # Estadísticas básicas
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - successful_tests
        
        print(f"📈 Total de pruebas: {total_tests}")
        print(f"✅ Exitosas: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"❌ Fallidas: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        # Análisis de tiempos de respuesta
        response_times = [r['response_time'] for r in self.results]
        if response_times:
            print(f"\n⏱️  TIEMPOS DE RESPUESTA (ms):")
            print(f"   Promedio: {statistics.mean(response_times):.2f}")
            print(f"   Mediana: {statistics.median(response_times):.2f}")
            print(f"   Mínimo: {min(response_times):.2f}")
            print(f"   Máximo: {max(response_times):.2f}")
            print(f"   Desviación estándar: {statistics.stdev(response_times):.2f}")
        
        # Análisis de coincidencias
        successful_results = [r for r in self.results if r['success']]
        if successful_results:
            matches = len([r for r in successful_results if r.get('matched', False)])
            no_matches = len(successful_results) - matches
            
            print(f"\n🎯 RESULTADOS DE COMPARACIÓN:")
            print(f"   Coincidencias (MATCH): {matches}")
            print(f"   No coincidencias (NO MATCH): {no_matches}")
            
            # Análisis de scores
            scores = [r.get('score', 0) for r in successful_results if r.get('score') is not None]
            if scores:
                print(f"\n📊 SCORES DE COMPARACIÓN:")
                print(f"   Promedio: {statistics.mean(scores):.2f}")
                print(f"   Mediana: {statistics.median(scores):.2f}")
                print(f"   Mínimo: {min(scores)}")
                print(f"   Máximo: {max(scores)}")
        
        # Análisis de errores
        if failed_tests > 0:
            print(f"\n❌ ANÁLISIS DE ERRORES:")
            error_types = {}
            for result in self.results:
                if not result['success']:
                    error = result.get('error', 'Error desconocido')
                    error_types[error] = error_types.get(error, 0) + 1
            
            for error, count in error_types.items():
                print(f"   {error}: {count} veces")
        
        # Calcular throughput
        if response_times:
            avg_response_time = statistics.mean(response_times) / 1000  # segundos
            throughput = 1 / avg_response_time if avg_response_time > 0 else 0
            print(f"\n🚀 RENDIMIENTO:")
            print(f"   Throughput: {throughput:.2f} comparaciones/segundo")
            print(f"   Tiempo promedio por comparación: {avg_response_time*1000:.2f}ms")
    
    def save_results(self, filename=None):
        """Guardar resultados en archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stress_test_results_{timestamp}.json"
        
        results_data = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.results),
                'base_url': self.base_url,
                'templates_used': list(self.templates.keys())
            },
            'results': self.results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            print(f"📁 Resultados guardados en: {filename}")
        except Exception as e:
            print(f"❌ Error al guardar resultados: {e}")

def main():
    parser = argparse.ArgumentParser(description='Stress Test para API de Huellas Digitales')
    parser.add_argument('--url', default='http://localhost:5500', help='URL base de la API')
    parser.add_argument('--concurrent-tests', type=int, default=100, help='Número de pruebas concurrentes')
    parser.add_argument('--sequential-tests', type=int, default=50, help='Número de pruebas secuenciales')
    parser.add_argument('--threads', type=int, default=10, help='Número de threads para pruebas concurrentes')
    parser.add_argument('--references', type=int, default=3, help='Número de huellas de referencia')
    parser.add_argument('--save-results', action='store_true', help='Guardar resultados en archivo JSON')
    parser.add_argument('--mode', choices=['concurrent', 'sequential', 'both'], default='both', 
                        help='Modo de ejecución de las pruebas')
    
    args = parser.parse_args()
    
    # Crear instancia del test
    stress_test = FingerprintStressTest(args.url)
    
    print("🧪 STRESS TEST - API DE COMPARACIÓN DE HUELLAS DIGITALES")
    print("=" * 60)
    
    # Verificar salud de la API
    if not stress_test.check_api_health():
        print("❌ La API no está disponible. Verifica que esté ejecutándose.")
        sys.exit(1)
    
    # Capturar huellas de referencia
    if not stress_test.capture_reference_fingerprints(args.references):
        print("❌ No se pudieron capturar las huellas de referencia")
        sys.exit(1)
    
    # Ejecutar pruebas según el modo seleccionado
    if args.mode in ['concurrent', 'both']:
        if not stress_test.run_concurrent_tests(args.concurrent_tests, args.threads):
            print("❌ Error en pruebas concurrentes")
            sys.exit(1)
    
    if args.mode in ['sequential', 'both']:
        if not stress_test.run_sequential_tests(args.sequential_tests):
            print("❌ Error en pruebas secuenciales")
            sys.exit(1)
    
    # Analizar resultados
    stress_test.analyze_results()
    
    # Guardar resultados si se solicita
    if args.save_results:
        stress_test.save_results()
    
    print("\n🎉 Stress test completado exitosamente!")

if __name__ == "__main__":
    main() 