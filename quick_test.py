#!/usr/bin/env python3
"""
Script de Prueba Rápida para API de Comparación de Huellas Digitales
"""

import requests
import time
import json

def test_api():
    base_url = "http://localhost:5000"
    
    print("🧪 PRUEBA RÁPIDA - API DE HUELLAS DIGITALES")
    print("=" * 50)
    
    # 1. Verificar que la API esté funcionando
    print("1. Verificando API...")
    try:
        response = requests.post(f"{base_url}/initialize")
        if response.status_code == 200:
            print("✅ API funcionando")
        else:
            print("❌ Error en API")
            return
    except Exception as e:
        print(f"❌ No se puede conectar a la API: {e}")
        return
    
    # 2. Capturar primera huella
    print("\n2. Capturando primera huella...")
    input("Pon tu dedo en el sensor y presiona ENTER...")
    
    try:
        response = requests.post(f"{base_url}/capturar-huella", json={
            "save_image": False,
            "create_template": True,
            "template_id": "test1"
        })
        
        if response.status_code == 200:
            data = response.json()
            template1 = data.get('data', {}).get('template')
            if template1:
                print("✅ Primera huella capturada")
            else:
                print("❌ Error al capturar primera huella")
                return
        else:
            print("❌ Error HTTP al capturar primera huella")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 3. Capturar segunda huella
    print("\n3. Capturando segunda huella...")
    input("Pon tu dedo en el sensor nuevamente y presiona ENTER...")
    
    try:
        response = requests.post(f"{base_url}/capturar-huella", json={
            "save_image": False,
            "create_template": True,
            "template_id": "test2"
        })
        
        if response.status_code == 200:
            data = response.json()
            template2 = data.get('data', {}).get('template')
            if template2:
                print("✅ Segunda huella capturada")
            else:
                print("❌ Error al capturar segunda huella")
                return
        else:
            print("❌ Error HTTP al capturar segunda huella")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 4. Comparar huellas
    print("\n4. Comparando huellas...")
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/comparar-huellas", json={
            "template1_id": "test1",
            "template2_id": "test2",
            "security_level": 1
        })
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            matched = data.get('matched', False)
            score = data.get('score', 0)
            response_time = (end_time - start_time) * 1000
            
            print(f"✅ Comparación completada en {response_time:.2f}ms")
            print(f"🎯 Resultado: {'COINCIDEN' if matched else 'NO COINCIDEN'}")
            print(f"📊 Score: {score}")
            
            if matched:
                print("🎉 ¡Las huellas coinciden!")
            else:
                print("⚠️  Las huellas no coinciden")
        else:
            print("❌ Error HTTP al comparar huellas")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 5. Prueba de stress rápida
    print("\n5. Prueba de stress rápida (10 comparaciones)...")
    
    success_count = 0
    total_time = 0
    
    for i in range(10):
        try:
            start_time = time.time()
            response = requests.post(f"{base_url}/comparar-huellas", json={
                "template1_id": "test1",
                "template2_id": "test2",
                "security_level": 1
            })
            end_time = time.time()
            
            if response.status_code == 200:
                success_count += 1
                total_time += (end_time - start_time)
                
        except Exception as e:
            print(f"❌ Error en comparación {i+1}: {e}")
    
    if success_count > 0:
        avg_time = (total_time / success_count) * 1000
        print(f"✅ {success_count}/10 comparaciones exitosas")
        print(f"⏱️  Tiempo promedio: {avg_time:.2f}ms")
        print(f"🚀 Throughput: {success_count/total_time:.2f} comparaciones/segundo")
    
    # 6. Listar templates
    print("\n6. Templates almacenados:")
    try:
        response = requests.get(f"{base_url}/templates")
        if response.status_code == 200:
            data = response.json()
            templates = data.get('templates', [])
            print(f"📁 Templates: {templates}")
        else:
            print("❌ Error al obtener templates")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Prueba rápida completada!")

if __name__ == "__main__":
    test_api() 