#!/usr/bin/env python3
"""
Script para ejecutar directamente una prueba de stress intensa
"""

from simple_stress_test import SimpleStressTest
import sys

def main():
    print("🚀 EJECUTANDO PRUEBA DE STRESS INTENSA")
    print("=" * 50)
    
    tester = SimpleStressTest()
    
    # Verificar que la API esté funcionando
    if not tester.test_api_health():
        print("❌ La API no está disponible. Verifica que esté ejecutándose.")
        sys.exit(1)
    
    # Ejecutar prueba de 25 llamadas API
    tester.run_api_stress_test(25)

if __name__ == "__main__":
    main() 