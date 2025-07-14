#!/usr/bin/env python3

import requests
import json
import base64
import time

# URL del servidor
BASE_URL = "http://localhost:5000"

def test_biometric_comparison():
    print("=== Test de Comparación Biométrica ===")
    
    # 1. Capturar primera huella
    print("\n1. Capturando primera huella...")
    print("   Por favor, coloque su dedo en el sensor...")
    
    try:
        response = requests.post(f"{BASE_URL}/capturar-huella", json={})
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                template1 = data['template']
                print(f"   ✓ Primera huella capturada (longitud: {len(template1)} caracteres)")
            else:
                print(f"   ✗ Error: {data['error']}")
                return
        else:
            print(f"   ✗ Error HTTP: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return
    
    # 2. Esperar un momento
    print("\n2. Esperando 2 segundos...")
    time.sleep(2)
    
    # 3. Capturar segunda huella
    print("\n3. Capturando segunda huella...")
    print("   Por favor, coloque el MISMO dedo en el sensor...")
    
    try:
        response = requests.post(f"{BASE_URL}/capturar-huella", json={})
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                template2 = data['template']
                print(f"   ✓ Segunda huella capturada (longitud: {len(template2)} caracteres)")
            else:
                print(f"   ✗ Error: {data['error']}")
                return
        else:
            print(f"   ✗ Error HTTP: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return
    
    # 4. Comparar huellas
    print("\n4. Comparando huellas...")
    
    try:
        comparison_data = {
            "template1": template1,
            "template2": template2,
            "security_level": 1  # Nivel más bajo para testing
        }
        
        response = requests.post(f"{BASE_URL}/comparar-huellas", json=comparison_data)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"   ✓ Comparación exitosa:")
                print(f"     - Matched: {data['matched']}")
                print(f"     - Score: {data['score']}")
                print(f"     - Message: {data['message']}")
                
                comparison_info = data.get('comparison_info', {})
                print(f"     - Security Level: {comparison_info.get('security_level', 'N/A')}")
                print(f"     - Template1 Source: {comparison_info.get('template1_source', 'N/A')}")
                print(f"     - Template2 Source: {comparison_info.get('template2_source', 'N/A')}")
                
                # Resultado esperado
                if data['matched']:
                    print("\n   🎉 ÉXITO: El mismo dedo fue reconocido correctamente!")
                else:
                    print("\n   ⚠️  ADVERTENCIA: El mismo dedo no fue reconocido.")
                    print("       Esto puede deberse a:")
                    print("       - Diferencias en la posición del dedo")
                    print("       - Diferencias en la presión aplicada")
                    print("       - Condiciones del sensor")
                    print("       - Nivel de seguridad muy alto")
                    
            else:
                print(f"   ✗ Error en comparación: {data['error']}")
        else:
            print(f"   ✗ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")

def test_different_levels():
    print("\n=== Test de Diferentes Niveles de Seguridad ===")
    
    # Capturar una huella para comparar consigo misma
    print("\n1. Capturando huella de referencia...")
    
    try:
        response = requests.post(f"{BASE_URL}/capturar-huella", json={})
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                template = data['template']
                print(f"   ✓ Huella capturada (longitud: {len(template)} caracteres)")
            else:
                print(f"   ✗ Error: {data['error']}")
                return
        else:
            print(f"   ✗ Error HTTP: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
        return
    
    # Probar diferentes niveles de seguridad
    print("\n2. Probando diferentes niveles de seguridad...")
    
    for level in range(1, 10):
        level_names = {
            1: "SL_LOWEST",
            2: "SL_LOWER", 
            3: "SL_LOW",
            4: "SL_BELOW_NORMAL",
            5: "SL_NORMAL",
            6: "SL_ABOVE_NORMAL",
            7: "SL_HIGH",
            8: "SL_HIGHER",
            9: "SL_HIGHEST"
        }
        
        try:
            comparison_data = {
                "template1": template,
                "template2": template,  # Mismo template
                "security_level": level
            }
            
            response = requests.post(f"{BASE_URL}/comparar-huellas", json=comparison_data)
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    status = "✓ MATCH" if data['matched'] else "✗ NO MATCH"
                    print(f"   Nivel {level} ({level_names[level]}): {status} - Score: {data['score']}")
                else:
                    print(f"   Nivel {level}: Error - {data['error']}")
            else:
                print(f"   Nivel {level}: Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   Nivel {level}: Error de conexión - {e}")

if __name__ == "__main__":
    print("Testing Biometric Comparison System")
    print("==================================")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/templates")
        if response.status_code == 200:
            print("✓ Servidor conectado correctamente")
        else:
            print(f"✗ Error de conexión al servidor: {response.status_code}")
            exit(1)
    except Exception as e:
        print(f"✗ No se puede conectar al servidor: {e}")
        print("   Asegúrese de que el servidor Flask esté ejecutándose en el puerto 5000")
        exit(1)
    
    # Ejecutar tests
    test_biometric_comparison()
    
    input("\nPresione Enter para probar diferentes niveles de seguridad...")
    test_different_levels()
    
    print("\n=== Test Completado ===") 