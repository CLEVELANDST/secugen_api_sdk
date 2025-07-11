# 🔬 Comandos Curl para Pruebas de Comparación de Huellas

## 📋 Endpoints Disponibles

### 1. Inicializar Dispositivo
```bash
curl -X POST -H "Content-Type: application/json" http://localhost:5000/initialize
```

### 2. Controlar LED
```bash
# Encender LED
curl -X POST -H "Content-Type: application/json" -d '{"state": true}' http://localhost:5000/led

# Apagar LED
curl -X POST -H "Content-Type: application/json" -d '{"state": false}' http://localhost:5000/led
```

### 3. Capturar Huella (sin template)
```bash
curl -X POST -H "Content-Type: application/json" -d '{"save_image": false}' http://localhost:5000/capturar-huella
```

### 4. Capturar Huella y Crear Template
```bash
curl -X POST -H "Content-Type: application/json" -d '{"save_image": false, "create_template": true}' http://localhost:5000/capturar-huella
```

### 5. Capturar Huella y Almacenar Template
```bash
curl -X POST -H "Content-Type: application/json" -d '{"save_image": false, "create_template": true, "template_id": "huella_1"}' http://localhost:5000/capturar-huella
```

### 6. Listar Templates Almacenados
```bash
curl -X GET http://localhost:5000/templates
```

### 7. Comparar Huellas por ID
```bash
curl -X POST -H "Content-Type: application/json" -d '{"template1_id": "huella_1", "template2_id": "huella_2", "security_level": 1}' http://localhost:5000/comparar-huellas
```

### 8. Comparar Huellas por Datos Base64
```bash
curl -X POST -H "Content-Type: application/json" -d '{"template1_data": "BASE64_TEMPLATE_1", "template2_data": "BASE64_TEMPLATE_2", "security_level": 1}' http://localhost:5000/comparar-huellas
```

### 9. Eliminar Template
```bash
curl -X DELETE http://localhost:5000/templates/huella_1
```

---

## 🧪 Secuencia de Pruebas Completa

### Paso 1: Inicializar sistema
```bash
curl -X POST -H "Content-Type: application/json" http://localhost:5000/initialize
```

### Paso 2: Capturar primera huella
```bash
curl -X POST -H "Content-Type: application/json" -d '{"save_image": false, "create_template": true, "template_id": "test1"}' http://localhost:5000/capturar-huella
```

### Paso 3: Capturar segunda huella
```bash
curl -X POST -H "Content-Type: application/json" -d '{"save_image": false, "create_template": true, "template_id": "test2"}' http://localhost:5000/capturar-huella
```

### Paso 4: Comparar huellas
```bash
curl -X POST -H "Content-Type: application/json" -d '{"template1_id": "test1", "template2_id": "test2", "security_level": 1}' http://localhost:5000/comparar-huellas
```

### Paso 5: Verificar templates
```bash
curl -X GET http://localhost:5000/templates
```

---

## 🚀 Pruebas de Stress

### Prueba Rápida (Script Python)
```bash
python3 quick_test.py
```

### Prueba de Stress Completa (Script Python)
```bash
# Prueba con configuración por defecto
python3 stress_test.py

# Prueba personalizada
python3 stress_test.py --concurrent-tests 200 --threads 20 --references 5 --save-results
```

### Prueba de Stress con Curl (Loop)
```bash
# Hacer 50 comparaciones en loop
for i in {1..50}; do
    echo "Comparación $i"
    curl -s -X POST -H "Content-Type: application/json" -d '{"template1_id": "test1", "template2_id": "test2"}' http://localhost:5000/comparar-huellas | jq .
    sleep 0.1
done
```

### Prueba de Stress Concurrente (Background)
```bash
# Lanzar 10 comparaciones en paralelo
for i in {1..10}; do
    curl -s -X POST -H "Content-Type: application/json" -d '{"template1_id": "test1", "template2_id": "test2"}' http://localhost:5000/comparar-huellas &
done
wait
```

---

## 📊 Análisis de Resultados

### Respuesta de Captura Exitosa
```json
{
  "success": true,
  "data": {
    "imagen": "BASE64_IMAGE_DATA",
    "template": "BASE64_TEMPLATE_DATA",
    "width": 258,
    "height": 336,
    "mensaje": "Huella capturada exitosamente",
    "template_stored": "test1"
  }
}
```

### Respuesta de Comparación Exitosa
```json
{
  "success": true,
  "matched": true,
  "score": 85,
  "message": "Comparación exitosa",
  "comparison_info": {
    "template1_source": "test1",
    "template2_source": "test2",
    "security_level": 1
  }
}
```

### Respuesta de Templates
```json
{
  "success": true,
  "templates": ["test1", "test2", "huella_1"],
  "count": 3
}
```

---

## 🎯 Casos de Uso

### 1. Registro de Usuario
```bash
# Capturar huella del usuario
curl -X POST -H "Content-Type: application/json" -d '{"save_image": true, "create_template": true, "template_id": "user_123"}' http://localhost:5000/capturar-huella
```

### 2. Verificación de Identidad
```bash
# Capturar huella temporal
curl -X POST -H "Content-Type: application/json" -d '{"save_image": false, "create_template": true, "template_id": "temp_verify"}' http://localhost:5000/capturar-huella

# Comparar con huella registrada
curl -X POST -H "Content-Type: application/json" -d '{"template1_id": "user_123", "template2_id": "temp_verify", "security_level": 2}' http://localhost:5000/comparar-huellas
```

### 3. Comparación 1:N (Uno contra Muchos)
```bash
# Comparar una huella contra múltiples templates
for template in "user_1" "user_2" "user_3"; do
    echo "Comparando contra $template"
    curl -s -X POST -H "Content-Type: application/json" -d "{\"template1_id\": \"temp_verify\", \"template2_id\": \"$template\"}" http://localhost:5000/comparar-huellas | jq .
done
```

---

## 🔧 Configuración de Seguridad

### Niveles de Seguridad Disponibles
- **Nivel 1**: Baja seguridad, mayor tolerancia
- **Nivel 2**: Seguridad media (recomendado)
- **Nivel 3**: Alta seguridad, menor tolerancia

### Ejemplo con Diferentes Niveles
```bash
# Nivel bajo
curl -X POST -H "Content-Type: application/json" -d '{"template1_id": "test1", "template2_id": "test2", "security_level": 1}' http://localhost:5000/comparar-huellas

# Nivel medio
curl -X POST -H "Content-Type: application/json" -d '{"template1_id": "test1", "template2_id": "test2", "security_level": 2}' http://localhost:5000/comparar-huellas

# Nivel alto
curl -X POST -H "Content-Type: application/json" -d '{"template1_id": "test1", "template2_id": "test2", "security_level": 3}' http://localhost:5000/comparar-huellas
```

---

## 📈 Métricas de Rendimiento

Para medir el rendimiento, usar el comando `time`:

```bash
# Medir tiempo de captura
time curl -X POST -H "Content-Type: application/json" -d '{"create_template": true}' http://localhost:5000/capturar-huella

# Medir tiempo de comparación
time curl -X POST -H "Content-Type: application/json" -d '{"template1_id": "test1", "template2_id": "test2"}' http://localhost:5000/comparar-huellas
```

---

## 🛠️ Troubleshooting

### Error: "Template no encontrado"
```bash
# Verificar templates disponibles
curl -X GET http://localhost:5000/templates
```

### Error: "Dispositivo no inicializado"
```bash
# Reinicializar dispositivo
curl -X POST -H "Content-Type: application/json" http://localhost:5000/initialize
```

### Error de Conexión
```bash
# Verificar que la aplicación esté ejecutándose
curl -X GET http://localhost:5000/templates
``` 