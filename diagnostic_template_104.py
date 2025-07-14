#!/usr/bin/env python3
"""
Diagnóstico para Error 104 (SGFDX_ERROR_INVALID_TEMPLATE2)
Este script diagnostica problemas con templates inválidos en SecuGen SDK
"""

import requests
import json
import base64
import sys
import time

# Configuración del servidor Flask
SERVER_URL = "http://localhost:5000"

def test_server_connection():
    """Verificar conectividad con el servidor"""
    try:
        response = requests.get(f"{SERVER_URL}/templates")
        if response.status_code == 200:
            print("✅ Servidor Flask conectado")
            return True
        else:
            print(f"❌ Servidor responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def get_templates_info():
    """Obtener información detallada de todos los templates"""
    try:
        response = requests.get(f"{SERVER_URL}/templates/info")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['info']
            else:
                print(f"❌ Error obteniendo info: {data.get('error', 'Desconocido')}")
                return None
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error en get_templates_info: {e}")
        return None

def validate_template_format(template_data):
    """Validar formato y estructura del template"""
    try:
        if isinstance(template_data, str):
            # Decodificar base64
            try:
                template_bytes = base64.b64decode(template_data)
            except Exception as e:
                return {"valid": False, "error": f"Error decodificando base64: {e}"}
        else:
            template_bytes = template_data
            
        # Verificar tamaño
        expected_size = 400  # SG400 template size
        actual_size = len(template_bytes)
        
        if actual_size != expected_size:
            return {
                "valid": False, 
                "error": f"Tamaño incorrecto: esperado {expected_size}, actual {actual_size}"
            }
        
        # Verificar que no sean todos zeros
        if all(b == 0 for b in template_bytes):
            return {"valid": False, "error": "Template vacío (todos zeros)"}
        
        # Verificar que haya suficiente variabilidad
        unique_bytes = len(set(template_bytes))
        if unique_bytes < 10:  # Muy poca variabilidad
            return {
                "valid": False, 
                "error": f"Template sospechoso: solo {unique_bytes} bytes únicos"
            }
        
        return {
            "valid": True,
            "size": actual_size,
            "unique_bytes": unique_bytes,
            "first_10_bytes": list(template_bytes[:10]),
            "last_10_bytes": list(template_bytes[-10:])
        }
        
    except Exception as e:
        return {"valid": False, "error": f"Error validando: {e}"}

def capture_new_template(template_id="test_diagnostic"):
    """Capturar nueva huella para diagnóstico"""
    try:
        print(f"🔄 Capturando nueva huella con ID: {template_id}")
        print("⚠️  Coloque el dedo en el sensor cuando se encienda el LED...")
        
        payload = {
            "save_image": False,
            "create_template": True,
            "template_id": template_id
        }
        
        response = requests.post(f"{SERVER_URL}/capturar-huella", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Huella capturada exitosamente")
                print(f"📦 Template ID: {data.get('template_stored', 'N/A')}")
                
                # Validar el template capturado
                template_data = data.get('template')
                if template_data:
                    validation = validate_template_format(template_data)
                    if validation['valid']:
                        print(f"✅ Template válido: {validation['size']} bytes, {validation['unique_bytes']} bytes únicos")
                        return template_data
                    else:
                        print(f"❌ Template inválido: {validation['error']}")
                        return None
                else:
                    print("❌ No se recibió template en la respuesta")
                    return None
            else:
                print(f"❌ Error capturando: {data.get('error', 'Desconocido')}")
                return None
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en capture_new_template: {e}")
        return None

def test_template_comparison(template1_id, template2_id):
    """Probar comparación entre dos templates con diagnóstico detallado"""
    try:
        print(f"🔍 Probando comparación: {template1_id} vs {template2_id}")
        
        payload = {
            "template1_id": template1_id,
            "template2_id": template2_id,
            "security_level": 5  # Nivel medio para pruebas
        }
        
        response = requests.post(f"{SERVER_URL}/comparar-huellas", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Comparación exitosa:")
                print(f"   Match: {data['matched']}")
                print(f"   Score: {data['score']}")
                print(f"   Mensaje: {data['message']}")
                return True
            else:
                error_msg = data.get('error', 'Error desconocido')
                print(f"❌ Error en comparación: {error_msg}")
                
                # Análisis específico del error 104
                if "código 104" in error_msg:
                    print("🔍 ERROR 104 DETECTADO - Análisis específico:")
                    print("   • Error: SGFDX_ERROR_INVALID_TEMPLATE2")
                    print("   • Causa: El segundo template es inválido o corrupto")
                    print("   • Solución: Verificar formato y regenerar template")
                    
                    # Diagnosticar el template2 específicamente
                    print(f"🔧 Diagnosticando template2 ({template2_id})...")
                    return diagnose_specific_template(template2_id)
                    
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en test_template_comparison: {e}")
        return False

def diagnose_specific_template(template_id):
    """Diagnosticar un template específico"""
    try:
        # Obtener info del template
        info = get_templates_info()
        if not info or template_id not in info['templates']:
            print(f"❌ Template {template_id} no encontrado")
            return False
            
        template_info = info['templates'][template_id]
        print(f"📊 Info del template {template_id}:")
        print(f"   • Tamaño: {template_info['size_bytes']} bytes")
        print(f"   • Formato: {template_info['format']}")
        print(f"   • Base64 size: {template_info['base64_size']}")
        
        # Sugerir regeneración
        print(f"💡 Sugerencia: Regenerar template {template_id}")
        regenerate = input("¿Desea regenerar el template? (s/n): ").lower().strip()
        
        if regenerate == 's':
            new_template = capture_new_template(template_id)
            if new_template:
                print(f"✅ Template {template_id} regenerado exitosamente")
                return True
            else:
                print(f"❌ Error regenerando template {template_id}")
                return False
        else:
            print("⚠️  Template no regenerado")
            return False
            
    except Exception as e:
        print(f"❌ Error en diagnose_specific_template: {e}")
        return False

def main():
    print("🔍 DIAGNÓSTICO ERROR 104 - TEMPLATE INVÁLIDO")
    print("=" * 50)
    
    # 1. Verificar conexión
    if not test_server_connection():
        print("❌ No se puede conectar al servidor Flask")
        sys.exit(1)
    
    # 2. Obtener información de templates
    print("\n📋 TEMPLATES ALMACENADOS:")
    info = get_templates_info()
    if not info:
        print("❌ No se pudo obtener información de templates")
        sys.exit(1)
    
    print(f"   • Total templates: {info['count']}")
    print(f"   • Tamaño total: {info['total_size_bytes']} bytes")
    print(f"   • Tamaño promedio: {info['avg_size_bytes']:.1f} bytes")
    
    # 3. Validar cada template
    print("\n🔍 VALIDANDO TEMPLATES:")
    for template_id, template_info in info['templates'].items():
        print(f"\n📝 Template: {template_id}")
        print(f"   • Tamaño: {template_info['size_bytes']} bytes")
        
        # Validar formato (necesitaríamos obtener el contenido real)
        if template_info['size_bytes'] != 400:
            print(f"   ⚠️  Tamaño incorrecto: esperado 400, actual {template_info['size_bytes']}")
        else:
            print(f"   ✅ Tamaño correcto")
    
    # 4. Probar comparaciones si hay templates
    template_list = list(info['templates'].keys())
    if len(template_list) >= 2:
        print("\n🔍 PROBANDO COMPARACIONES:")
        
        # Probar primera comparación
        template1 = template_list[0]
        template2 = template_list[1]
        
        print(f"\n🔄 Comparación 1: {template1} vs {template2}")
        test_template_comparison(template1, template2)
        
        # Si hay más templates, probar otras combinaciones
        if len(template_list) > 2:
            template3 = template_list[2]
            print(f"\n🔄 Comparación 2: {template1} vs {template3}")
            test_template_comparison(template1, template3)
    
    # 5. Capturar nueva huella para pruebas
    print("\n🆕 CAPTURA DE NUEVA HUELLA:")
    capture_choice = input("¿Desea capturar una nueva huella para pruebas? (s/n): ").lower().strip()
    
    if capture_choice == 's':
        new_template = capture_new_template("test_diagnostic_new")
        if new_template and template_list:
            print(f"\n🔄 Comparando nueva huella con {template_list[0]}")
            test_template_comparison("test_diagnostic_new", template_list[0])
    
    print("\n✅ Diagnóstico completado")
    print("\n💡 RECOMENDACIONES:")
    print("   • Si persiste error 104, regenerar templates corruptos")
    print("   • Verificar estabilidad del dispositivo")
    print("   • Capturar huellas con buena calidad")
    print("   • Usar nivel de seguridad apropiado (4-6)")

if __name__ == "__main__":
    main() 