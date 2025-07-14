#!/usr/bin/env python3
"""
Script de ejemplo para demostrar el uso de templates en el sistema SecuGen
"""

import requests
import json
import base64
import sys

BASE_URL = "http://localhost:5000"

def test_template_workflow():
    """Ejemplo completo de flujo de trabajo con templates"""
    print("🧪 Iniciando prueba de templates...")
    
    # 1. Inicializar dispositivo
    print("\n1. Inicializando dispositivo...")
    init_response = requests.post(f"{BASE_URL}/initialize")
    print(f"   Estado: {init_response.json()}")
    
    # 2. Capturar primera huella y crear template
    print("\n2. Capturando primera huella...")
    capture1_data = {
        "create_template": True,
        "template_id": "usuario_test_1",
        "save_image": False
    }
    
    capture1_response = requests.post(f"{BASE_URL}/capturar-huella", json=capture1_data)
    if capture1_response.status_code == 200:
        result1 = capture1_response.json()
        print(f"   ✅ Primera huella capturada")
        print(f"   Template ID: {result1['data'].get('template_stored')}")
        template1_data = result1['data'].get('template')
        print(f"   Template Base64: {template1_data[:50]}..." if template1_data else "   Sin template generado")
    else:
        print(f"   ❌ Error: {capture1_response.json()}")
        return False
    
    # 3. Capturar segunda huella
    print("\n3. Capturando segunda huella...")
    capture2_data = {
        "create_template": True,
        "save_image": False
    }
    
    capture2_response = requests.post(f"{BASE_URL}/capturar-huella", json=capture2_data)
    if capture2_response.status_code == 200:
        result2 = capture2_response.json()
        print(f"   ✅ Segunda huella capturada")
        template2_data = result2['data'].get('template')
        print(f"   Template Base64: {template2_data[:50]}..." if template2_data else "   Sin template generado")
    else:
        print(f"   ❌ Error: {capture2_response.json()}")
        return False
    
    # 4. Comparar usando ID vs Data
    print("\n4. Comparando huellas (ID vs Data)...")
    if template2_data:
        comparison_data = {
            "template1_id": "usuario_test_1",
            "template2_data": template2_data,
            "security_level": 1
        }
        
        comparison_response = requests.post(f"{BASE_URL}/comparar-huellas", json=comparison_data)
        if comparison_response.status_code == 200:
            result = comparison_response.json()
            print(f"   ✅ Comparación exitosa")
            print(f"   Coincidencia: {result['matched']}")
            print(f"   Puntuación: {result['score']}")
            print(f"   Mensaje: {result['message']}")
        else:
            print(f"   ❌ Error en comparación: {comparison_response.json()}")
    else:
        print("   ⚠️  No se puede comparar sin template válido")
    
    # 5. Listar templates almacenados
    print("\n5. Listando templates almacenados...")
    templates_response = requests.get(f"{BASE_URL}/templates")
    if templates_response.status_code == 200:
        templates = templates_response.json()
        print(f"   ✅ Templates encontrados: {templates['templates']}")
        print(f"   Total: {templates['count']}")
    else:
        print(f"   ❌ Error: {templates_response.json()}")
    
    return True

def test_template_formats():
    """Ejemplo de diferentes formatos de templates"""
    print("\n🔍 Probando diferentes formatos de templates...")
    
    # Ejemplo 1: Template por referencia (ID)
    print("\n📋 Ejemplo 1: Comparación por ID")
    format1 = {
        "template1_id": "usuario_test_1",
        "template2_id": "usuario_test_2",
        "security_level": 1
    }
    print(f"   Formato: {json.dumps(format1, indent=2)}")
    
    # Ejemplo 2: Template por datos (Base64)
    print("\n📋 Ejemplo 2: Comparación por datos Base64")
    format2 = {
        "template1_data": "iVBORw0KGgoAAAANSUhEUgAAAPIAAAFQCAYAAACZvQrwAAAAAXNSR0IArs4c6Q==",
        "template2_data": "iVBORw0KGgoAAAANSUhEUgAAAPIAAAFQCAYAAACZvQrwAAAAAXNSR0IArs4c6Q==",
        "security_level": 1
    }
    print(f"   Formato: {json.dumps(format2, indent=2)}")
    
    # Ejemplo 3: Template mixto
    print("\n📋 Ejemplo 3: Comparación mixta (ID + Data)")
    format3 = {
        "template1_id": "usuario_test_1",
        "template2_data": "iVBORw0KGgoAAAANSUhEUgAAAPIAAAFQCAYAAACZvQrwAAAAAXNSR0IArs4c6Q==",
        "security_level": 2
    }
    print(f"   Formato: {json.dumps(format3, indent=2)}")

def test_error_cases():
    """Ejemplo de casos de error comunes"""
    print("\n⚠️ Probando casos de error...")
    
    # Error 1: Template inexistente
    print("\n❌ Error 1: Template ID inexistente")
    error1 = {
        "template1_id": "inexistente_123",
        "template2_id": "usuario_test_1",
        "security_level": 1
    }
    response1 = requests.post(f"{BASE_URL}/comparar-huellas", json=error1)
    print(f"   Respuesta: {response1.status_code} - {response1.json()}")
    
    # Error 2: Base64 inválido
    print("\n❌ Error 2: Base64 inválido")
    error2 = {
        "template1_data": "datos_invalidos_no_base64",
        "template2_data": "iVBORw0KGgoAAAANSUhEUgAAAPIAAAFQCAYAAACZvQrwAAAAAXNSR0IArs4c6Q==",
        "security_level": 1
    }
    response2 = requests.post(f"{BASE_URL}/comparar-huellas", json=error2)
    print(f"   Respuesta: {response2.status_code} - {response2.json()}")
    
    # Error 3: Sin templates
    print("\n❌ Error 3: Sin templates proporcionados")
    error3 = {
        "security_level": 1
    }
    response3 = requests.post(f"{BASE_URL}/comparar-huellas", json=error3)
    print(f"   Respuesta: {response3.status_code} - {response3.json()}")

if __name__ == "__main__":
    print("🔬 PRUEBA DE TEMPLATES - Sistema SecuGen")
    print("=" * 50)
    
    try:
        # Verificar si la API está disponible
        health_check = requests.get(f"{BASE_URL}/initialize")
        if health_check.status_code != 405:  # 405 = Method Not Allowed (pero API responde)
            print("❌ API no disponible. Asegúrese de que el servidor esté corriendo.")
            sys.exit(1)
        
        # Ejecutar pruebas
        print("\n🧪 Ejecutando flujo de trabajo completo...")
        test_template_workflow()
        
        print("\n🔍 Mostrando formatos de templates...")
        test_template_formats()
        
        print("\n⚠️ Probando casos de error...")
        test_error_cases()
        
        print("\n✅ Pruebas completadas")
        
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API. Verifique:")
        print("   1. El servidor está corriendo: ./start_production.sh")
        print("   2. La URL es correcta: http://localhost:5000")
        print("   3. No hay firewall bloqueando el puerto 5000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1) 