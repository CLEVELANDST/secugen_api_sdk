# 🌩️ Thunder Client - Comandos cURL para Sistema de Huellas

> **Colección de comandos cURL para probar la API del sistema de huellas SecuGen**  
> **Compatible con Thunder Client para VS Code**

## 🚀 Inicio Rápido

### 1. Verificar que el servidor esté ejecutándose
```bash
curl -X GET http://localhost:5000/
```

---

## 🔧 Endpoints de Sistema

### 1. **Inicializar Dispositivo**
```bash
curl -X POST http://localhost:5000/initialize \
  -H "Content-Type: application/json" \
  -d "{}"
```

### 2. **Encender LED**
```bash
curl -X POST http://localhost:5000/led \
  -H "Content-Type: application/json" \
  -d "{\"state\": true}"
```

### 3. **Apagar LED**
```bash
curl -X POST http://localhost:5000/led \
  -H "Content-Type: application/json" \
  -d "{\"state\": false}"
```

---

## 👆 Endpoints de Captura de Huellas

### 1. **Capturar Huella (Simple)**
```bash
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{}"
```

### 2. **Capturar Huella y Guardar Imagen**
```bash
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{\"save_image\": true}"
```

### 3. **Capturar Huella y Crear Template con ID**
```bash
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{\"create_template\": true, \"template_id\": \"usuario_001\"}"
```

### 4. **Capturar Huella Completa (Imagen + Template + ID)**
```bash
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{\"save_image\": true, \"create_template\": true, \"template_id\": \"admin_001\"}"
```

---

## 🔍 Endpoints de Comparación

### 1. **Comparar Huellas por Templates Base64**
```bash
curl -X POST http://localhost:5000/comparar-huellas \
  -H "Content-Type: application/json" \
  -d "{
    \"template1_data\": \"TEMPLATE_BASE64_1\",
    \"template2_data\": \"TEMPLATE_BASE64_2\",
    \"security_level\": 1
  }"
```

### 2. **Comparar Huellas por ID de Template**
```bash
curl -X POST http://localhost:5000/comparar-huellas \
  -H "Content-Type: application/json" \
  -d "{
    \"template1_id\": \"usuario_001\",
    \"template2_id\": \"admin_001\",
    \"security_level\": 5
  }"
```

### 3. **Comparar Huella Nueva vs Template Almacenado**
```bash
curl -X POST http://localhost:5000/comparar-huellas \
  -H "Content-Type: application/json" \
  -d "{
    \"template1_id\": \"usuario_001\",
    \"template2_data\": \"TEMPLATE_BASE64_NUEVO\",
    \"security_level\": 3
  }"
```

### 4. **Comparar con Nivel de Seguridad Alto**
```bash
curl -X POST http://localhost:5000/comparar-huellas \
  -H "Content-Type: application/json" \
  -d "{
    \"template1_data\": \"TEMPLATE_BASE64_1\",
    \"template2_data\": \"TEMPLATE_BASE64_2\",
    \"security_level\": 9
  }"
```

---

## 📊 Endpoints de Gestión de Templates

### 1. **Listar Todos los Templates**
```bash
curl -X GET http://localhost:5000/templates \
  -H "Content-Type: application/json"
```

### 2. **Eliminar Template por ID**
```bash
curl -X DELETE http://localhost:5000/templates/usuario_001 \
  -H "Content-Type: application/json"
```

---

## 🧪 Comandos de Testing Completo

### 1. **Flujo Completo: Inicializar + Capturar + Comparar**
```bash
# Paso 1: Inicializar
curl -X POST http://localhost:5000/initialize \
  -H "Content-Type: application/json" \
  -d "{}"

# Paso 2: Capturar primera huella
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{\"template_id\": \"test_user_1\"}"

# Paso 3: Capturar segunda huella
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{\"template_id\": \"test_user_2\"}"

# Paso 4: Comparar huellas
curl -X POST http://localhost:5000/comparar-huellas \
  -H "Content-Type: application/json" \
  -d "{\"template1_id\": \"test_user_1\", \"template2_id\": \"test_user_2\", \"security_level\": 1}"
```

### 2. **Test de Verificación de Identidad**
```bash
# Registrar usuario
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{\"template_id\": \"john_doe\", \"create_template\": true}"

# Verificar identidad (simular login)
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{\"create_template\": true}" \
  | jq -r '.template' | \
  xargs -I {} curl -X POST http://localhost:5000/comparar-huellas \
    -H "Content-Type: application/json" \
    -d "{\"template1_id\": \"john_doe\", \"template2_data\": \"{}\"}"
```

---

## 🔧 Comandos de Diagnóstico

### 1. **Verificar Estado del Sistema**
```bash
curl -X POST http://localhost:5000/initialize \
  -H "Content-Type: application/json" \
  -d "{}" \
  | jq '{success: .success, message: .message}'
```

### 2. **Test de LED**
```bash
# Encender LED
curl -X POST http://localhost:5000/led \
  -H "Content-Type: application/json" \
  -d "{\"state\": true}"

# Esperar 2 segundos
sleep 2

# Apagar LED
curl -X POST http://localhost:5000/led \
  -H "Content-Type: application/json" \
  -d "{\"state\": false}"
```

### 3. **Verificar Templates Almacenados**
```bash
curl -X GET http://localhost:5000/templates \
  -H "Content-Type: application/json" \
  | jq '{template_count: .count, templates: [.templates[] | .id]}'
```

---

## 📝 Notas para Thunder Client

### **Importación a Thunder Client:**
1. Copia cualquiera de los comandos cURL anteriores
2. Ve a Thunder Client en VS Code
3. Click en "Import" → "Import from cURL"
4. Pega el comando cURL
5. Ejecuta el request

### **Variables de Entorno Sugeridas:**
```json
{
  "base_url": "http://localhost:5000",
  "security_level_low": "1",
  "security_level_normal": "5",
  "security_level_high": "9"
}
```

### **Headers Comunes:**
```json
{
  "Content-Type": "application/json"
}
```

---

## 🎯 Casos de Uso Prácticos

### **Caso 1: Registro de Usuario**
```bash
curl -X POST http://localhost:5000/capturar-huella \
  -H "Content-Type: application/json" \
  -d "{\"template_id\": \"empleado_123\", \"save_image\": true}"
```

### **Caso 2: Autenticación**
```bash
curl -X POST http://localhost:5000/comparar-huellas \
  -H "Content-Type: application/json" \
  -d "{\"template1_id\": \"empleado_123\", \"template2_data\": \"HUELLA_CAPTURADA_AHORA\", \"security_level\": 5}"
```

### **Caso 3: Limpieza de Sistema**
```bash
# Listar templates
curl -X GET http://localhost:5000/templates

# Eliminar template específico
curl -X DELETE http://localhost:5000/templates/test_user_1
```

---

## 📊 Respuestas Esperadas

### **Respuesta de Éxito:**
```json
{
  "success": true,
  "message": "Operación exitosa",
  "data": "..."
}
```

### **Respuesta de Error:**
```json
{
  "success": false,
  "error": "Descripción del error"
}
```

### **Respuesta de Comparación:**
```json
{
  "success": true,
  "matched": true,
  "score": 85,
  "message": "Comparación exitosa",
  "comparison_info": {
    "template1_source": "data",
    "template2_source": "usuario_001",
    "security_level": 5
  }
}
```

---

## 🚨 Troubleshooting

### **Si el servidor no responde:**
```bash
# Verificar que el servidor esté ejecutándose
ps aux | grep app.py

# Reiniciar el servidor
pkill -f "python.*app.py"
python3 app.py
```

### **Si hay errores de permisos USB:**
```bash
# Ejecutar script de configuración
./setup_production.sh

# Verificar permisos
ls -la /dev/bus/usb/
```

## Optimizaciones de Eficiencia

### ✅ **Sistema Optimizado (Nuevo)**
El sistema ahora usa **datos binarios internamente** y **base64 solo para comunicación API**:

- **Almacenamiento interno**: Formato binario (128 bytes)
- **Comparaciones**: Binario directo (1.3x más rápido)
- **API REST**: Base64 para compatibilidad JSON
- **Overhead reducido**: 34.4% menos uso de memoria

### 📊 **Verificar Eficiencia**
```bash
# Obtener información de rendimiento de templates
curl -X GET http://localhost:5000/templates/info

# Ejecutar benchmark de eficiencia
python3 benchmark_efficiency.py
```

### 🔬 **Comparación de Rendimiento**
```
📊 ANÁLISIS DE TAMAÑO:
   Templates binarios: 128,000 bytes
   Templates base64:   172,000 bytes
   Overhead base64:    34.4%

⚡ BENCHMARK DE COMPARACIÓN:
   Comparación binaria: 0.0527s (5,000 iteraciones)
   Comparación base64:  0.0680s (5,000 iteraciones)
   Base64 es 1.3x más lento
```

---

*Todos los comandos están listos para usar en Thunder Client. Simplemente copia y pega en la opción "Import from cURL".* 