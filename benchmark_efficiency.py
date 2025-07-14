#!/usr/bin/env python3
"""
Benchmark de eficiencia: Base64 vs Binario para comparación de templates
"""
import base64
import time
import random
import hashlib
import struct

def create_mock_template(size=128):
    """Crear un template simulado de tamaño específico"""
    return bytes([random.randint(0, 255) for _ in range(size)])

def benchmark_comparison():
    """Comparar eficiencia entre base64 y binario"""
    print("🔬 BENCHMARK: Base64 vs Binario para Templates de Huellas")
    print("=" * 60)
    
    # Crear templates de prueba
    num_templates = 1000
    templates_binary = [create_mock_template() for _ in range(num_templates)]
    templates_base64 = [base64.b64encode(t).decode() for t in templates_binary]
    
    # Análisis de tamaño
    binary_size = sum(len(t) for t in templates_binary)
    base64_size = sum(len(t) for t in templates_base64)
    
    print(f"📊 ANÁLISIS DE TAMAÑO:")
    print(f"   Templates binarios: {binary_size:,} bytes")
    print(f"   Templates base64:   {base64_size:,} bytes")
    print(f"   Overhead base64:    {((base64_size - binary_size) / binary_size * 100):.1f}%")
    print()
    
    # Benchmark de comparación directa
    print("⚡ BENCHMARK DE COMPARACIÓN:")
    iterations = 5000
    
    # Comparación binaria
    template1_bin = templates_binary[0]
    template2_bin = templates_binary[1]
    
    start = time.time()
    for _ in range(iterations):
        # Simulación de comparación binaria simple
        result = template1_bin == template2_bin
        if not result:
            # Comparación más compleja
            matches = sum(1 for a, b in zip(template1_bin, template2_bin) if a == b)
            similarity = matches / len(template1_bin)
    end = time.time()
    time_binary = end - start
    
    # Comparación base64 (requiere decodificación)
    template1_b64 = templates_base64[0]
    template2_b64 = templates_base64[1]
    
    start = time.time()
    for _ in range(iterations):
        # Decodificar antes de comparar
        t1_decoded = base64.b64decode(template1_b64)
        t2_decoded = base64.b64decode(template2_b64)
        result = t1_decoded == t2_decoded
        if not result:
            matches = sum(1 for a, b in zip(t1_decoded, t2_decoded) if a == b)
            similarity = matches / len(t1_decoded)
    end = time.time()
    time_base64 = end - start
    
    print(f"   Comparación binaria: {time_binary:.4f}s ({iterations:,} iteraciones)")
    print(f"   Comparación base64:  {time_base64:.4f}s ({iterations:,} iteraciones)")
    print(f"   Base64 es {time_base64/time_binary:.1f}x más lento")
    print()
    
    # Benchmark de almacenamiento
    print("💾 BENCHMARK DE ALMACENAMIENTO:")
    
    # Simular almacenamiento en memoria
    start = time.time()
    storage_binary = {}
    for i, template in enumerate(templates_binary):
        storage_binary[f"template_{i}"] = template
    end = time.time()
    time_store_binary = end - start
    
    start = time.time()
    storage_base64 = {}
    for i, template in enumerate(templates_base64):
        storage_base64[f"template_{i}"] = template
    end = time.time()
    time_store_base64 = end - start
    
    print(f"   Almacenamiento binario: {time_store_binary:.4f}s")
    print(f"   Almacenamiento base64:  {time_store_base64:.4f}s")
    print(f"   Diferencia: {((time_store_base64 - time_store_binary) / time_store_binary * 100):.1f}%")
    print()
    
    # Recomendaciones
    print("💡 RECOMENDACIONES DE EFICIENCIA:")
    print("   ✅ Usar binario para:")
    print("      - Almacenamiento interno")
    print("      - Comparaciones algorítmicas")
    print("      - Procesamiento de templates")
    print()
    print("   📤 Usar base64 para:")
    print("      - Transmisión HTTP/JSON")
    print("      - Almacenamiento en texto")
    print("      - APIs REST")
    print()
    
    print("🎯 CONCLUSIÓN:")
    print(f"   El sistema optimizado ahora usa binario internamente")
    print(f"   y base64 solo para comunicación API, mejorando")
    print(f"   el rendimiento en {time_base64/time_binary:.1f}x")

if __name__ == "__main__":
    benchmark_comparison() 