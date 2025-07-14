#!/usr/bin/env python3

import requests
import json
import base64
import hashlib
import struct
import random

def create_completely_different_template(seed):
    """Crear un template completamente diferente usando una semilla única"""
    # Crear datos completamente diferentes basados en la semilla
    random.seed(seed)
    data = bytearray(86688)  # Tamaño típico de imagen
    
    # Llenar con datos completamente aleatorios
    for i in range(len(data)):
        data[i] = random.randint(0, 255)
    
    # Crear template usando la misma lógica que el algoritmo original
    template = bytearray(128)
    
    # 1. Crear hash de la imagen completa
    full_hash = hashlib.sha256(data).digest()
    
    # 2. Crear hash de bloques
    block_size = len(data) // 8
    block_hashes = []
    
    for i in range(8):
        start = i * block_size
        end = min((i + 1) * block_size, len(data))
        if start < len(data):
            block_data = data[start:end]
            block_hash = hashlib.md5(block_data).digest()[:4]
            block_hashes.append(block_hash)
    
    # 3. Crear características estadísticas básicas
    if len(data) > 0:
        avg_value = sum(data) // len(data)
        std_approx = int(((sum((x - avg_value) ** 2 for x in data[::100])) / max(1, len(data[::100]))) ** 0.5)
        stats = struct.pack('<BB', avg_value % 256, std_approx % 256)
    else:
        stats = b'\x00\x00'
    
    # Combinar características en el template
    template[0:4] = struct.pack('<I', len(template))
    template[4:8] = b'SGFP'
    template[8:10] = stats
    
    # Llenar con hash completo
    for i in range(10, min(42, len(template))):
        template[i] = full_hash[(i - 10) % len(full_hash)]
    
    # Llenar con hashes de bloques
    offset = 42
    for block_hash in block_hashes:
        for j, byte in enumerate(block_hash):
            if offset + j < len(template):
                template[offset + j] = byte
        offset += len(block_hash)
    
    return bytes(template)

def test_false_positives():
    """Probar que huellas completamente diferentes NO den match"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 PROBANDO FALSOS POSITIVOS")
    print("=" * 50)
    
    # Crear 5 templates completamente diferentes
    templates = []
    for i in range(5):
        template = create_completely_different_template(f"huella_diferente_{i}_12345")
        template_b64 = base64.b64encode(template).decode('utf-8')
        templates.append(template_b64)
        print(f"Template {i+1} creado: {len(template_b64)} caracteres")
    
    print(f"\n🔍 Comparando templates DIFERENTES (NO deberían hacer match)")
    
    # Probar diferentes niveles de seguridad
    security_levels = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    total_tests = 0
    false_positives = 0
    
    for level in security_levels:
        print(f"\n🔒 Security Level {level}:")
        level_false_positives = 0
        level_tests = 0
        
        # Comparar template 0 con los otros 4
        for i in range(1, 5):
            comparison_data = {
                "template1_data": templates[0],
                "template2_data": templates[i],
                "security_level": level
            }
            
            try:
                response = requests.post(
                    f"{base_url}/comparar-huellas",
                    json=comparison_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    matched = result.get('matched')
                    score = result.get('score')
                    
                    total_tests += 1
                    level_tests += 1
                    
                    if matched:
                        false_positives += 1
                        level_false_positives += 1
                        print(f"  ❌ FALSO POSITIVO Template 0 vs {i}: Match={matched}, Score={score}%")
                    else:
                        print(f"  ✅ CORRECTO Template 0 vs {i}: Match={matched}, Score={score}%")
                else:
                    print(f"  ❌ Error HTTP: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {str(e)}")
        
        print(f"  📊 Level {level}: {level_false_positives}/{level_tests} falsos positivos")
    
    print(f"\n📈 RESUMEN FINAL:")
    print(f"Total pruebas: {total_tests}")
    print(f"Falsos positivos: {false_positives}")
    print(f"Tasa de falsos positivos: {(false_positives/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    if false_positives > 0:
        print(f"⚠️  PROBLEMA: Se detectaron {false_positives} falsos positivos")
        print(f"💡 RECOMENDACIÓN: Aumentar thresholds o mejorar algoritmo")
    else:
        print(f"✅ PERFECTO: No se detectaron falsos positivos")

def test_same_fingerprint():
    """Probar que la misma huella SÍ dé match"""
    base_url = "http://localhost:5000"
    
    print(f"\n🧪 PROBANDO MISMO DEDO")
    print("=" * 30)
    
    # Crear template base
    base_template = create_completely_different_template("mismo_dedo_base_seed")
    template_b64 = base64.b64encode(base_template).decode('utf-8')
    
    # Probar con el mismo template
    comparison_data = {
        "template1_data": template_b64,
        "template2_data": template_b64,  # Exactamente el mismo
        "security_level": 5
    }
    
    try:
        response = requests.post(
            f"{base_url}/comparar-huellas",
            json=comparison_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            matched = result.get('matched')
            score = result.get('score')
            print(f"✅ Mismo template: Match={matched}, Score={score}%")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_false_positives()
    test_same_fingerprint() 