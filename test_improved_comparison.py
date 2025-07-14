#!/usr/bin/env python3

import requests
import json
import base64
import hashlib
import struct

def simulate_fingerprint_image(base_data, variation_level=0.1):
    """Simular variaciones menores en una imagen de huella"""
    # Crear datos base
    base_size = 258 * 336  # Tamaño típico del sensor
    base_image = bytearray(base_size)
    
    # Llenar con patrón base
    for i in range(base_size):
        base_image[i] = (hash(base_data + str(i)) % 256)
    
    # Agregar variaciones menores
    if variation_level > 0:
        for i in range(0, base_size, 100):  # Cada 100 bytes
            if i < len(base_image):
                # Pequeña variación aleatoria
                variation = int((hash(base_data + str(i) + "var") % 20) * variation_level)
                base_image[i] = (base_image[i] + variation) % 256
    
    return bytes(base_image)

def test_improved_comparison():
    """Probar la comparación mejorada con templates del mismo dedo"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Probando comparación mejorada con templates del mismo dedo simulado...")
    
    # Simular dos imágenes del mismo dedo con pequeñas variaciones
    same_finger_data = "mismo_dedo_test_123"
    
    # Imagen 1: sin variaciones
    image1 = simulate_fingerprint_image(same_finger_data, 0.0)
    print(f"Imagen 1 generada: {len(image1)} bytes")
    
    # Imagen 2: con pequeñas variaciones (simulando posición ligeramente diferente)
    image2 = simulate_fingerprint_image(same_finger_data, 0.1)
    print(f"Imagen 2 generada: {len(image2)} bytes")
    
    # Capturar primera "huella" (simulada)
    print("\n📡 Capturando primera huella simulada...")
    
    # En lugar de usar el endpoint real, vamos a simular los templates
    # usando la lógica del algoritmo mejorado
    
    template1_data = create_improved_template(image1)
    template2_data = create_improved_template(image2)
    
    template1_b64 = base64.b64encode(template1_data).decode('utf-8')
    template2_b64 = base64.b64encode(template2_data).decode('utf-8')
    
    print(f"Template 1: {len(template1_b64)} caracteres")
    print(f"Template 2: {len(template2_b64)} caracteres")
    
    # Probar diferentes niveles de seguridad
    security_levels = [1, 2, 3, 4, 5]
    
    for level in security_levels:
        print(f"\n🔒 Probando security_level {level}...")
        
        comparison_data = {
            "template1_data": template1_b64,
            "template2_data": template2_b64,
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
                print(f"  ✅ Match: {result.get('matched')} | Score: {result.get('score')}% | {result.get('message')}")
            else:
                print(f"  ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    # Probar con un dedo completamente diferente
    print(f"\n🧪 Probando con dedo diferente...")
    
    different_finger_data = "dedo_diferente_xyz_789"
    image3 = simulate_fingerprint_image(different_finger_data, 0.0)
    template3_data = create_improved_template(image3)
    template3_b64 = base64.b64encode(template3_data).decode('utf-8')
    
    comparison_data = {
        "template1_data": template1_b64,
        "template2_data": template3_b64,
        "security_level": 4
    }
    
    try:
        response = requests.post(
            f"{base_url}/comparar-huellas",
            json=comparison_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Match: {result.get('matched')} | Score: {result.get('score')}% | {result.get('message')}")
        else:
            print(f"  ❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")

def create_improved_template(image_data):
    """Recrear la lógica del template mejorado"""
    data = bytes(image_data)
    template = bytearray(128)
    
    # 1. Crear hash de la imagen completa
    full_hash = hashlib.sha256(data).digest()
    
    # 2. Crear hash de bloques para tolerancia a variaciones menores
    block_size = len(data) // 8  # Dividir en 8 bloques
    block_hashes = []
    
    for i in range(8):
        start = i * block_size
        end = min((i + 1) * block_size, len(data))
        if start < len(data):
            block_data = data[start:end]
            block_hash = hashlib.md5(block_data).digest()[:4]  # Solo 4 bytes por bloque
            block_hashes.append(block_hash)
    
    # 3. Crear características estadísticas básicas
    if len(data) > 0:
        avg_value = sum(data) // len(data)
        std_approx = int(((sum((x - avg_value) ** 2 for x in data[::100])) / max(1, len(data[::100]))) ** 0.5)
        stats = struct.pack('<BB', avg_value % 256, std_approx % 256)
    else:
        stats = b'\x00\x00'
    
    # Combinar características en el template
    template[0:4] = struct.pack('<I', len(template))  # Header
    template[4:8] = b'SGFP'  # Identificador
    template[8:10] = stats  # Estadísticas
    
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

if __name__ == "__main__":
    test_improved_comparison() 