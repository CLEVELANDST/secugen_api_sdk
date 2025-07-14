# 🔍 Formato de Templates para Comparación de Huellas

## 📋 Descripción General
Los templates son representaciones digitales de las huellas dactilares que permiten comparaciones rápidas y eficientes. En el sistema SecuGen, los templates pueden manejarse de dos formas:

1. **Templates por Referencia** (ID almacenado)
2. **Templates por Datos** (Base64 directo)

## 🏗️ Estructura del Template

### 1. **Template por Referencia (ID)**
```json
{
  "template1_id": "usuario_123",
  "template2_id": "usuario_456",
  "security_level": 1
}
```

### 2. **Template por Datos (Base64)**
```json
{
  "template1_data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "template2_data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "security_level": 1
}
```

### 3. **Template Mixto**
```json
{
  "template1_id": "usuario_123",
  "template2_data": "iVBORw0KGgoAAAANSUhEUgAA...",
  "security_level": 1
}
```

## 📡 APIs Disponibles

### 1. **Capturar Huella y Crear Template**
```bash
curl -X POST http://localhost:5000/capturar-huella \
-H "Content-Type: application/json" \
-d '{
  "create_template": true,
  "template_id": "usuario_123",
  "save_image": false
}'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "imagen": "iVBORw0KGgoAAAANSUhEUgAA...",
    "template": "VGVtcGxhdGUgZGF0YSBhcXXDrA==",
    "width": 258,
    "height": 336,
    "mensaje": "Huella capturada exitosamente",
    "template_stored": "usuario_123"
  }
}
```

### 2. **Comparar Huellas por ID**
```bash
curl -X POST http://localhost:5000/comparar-huellas \
-H "Content-Type: application/json" \
-d '{
  "template1_id": "usuario_123",
  "template2_id": "usuario_456",
  "security_level": 1
}'
```

### 3. **Comparar Huellas por Datos**
```bash
curl -X POST http://localhost:5000/comparar-huellas \
-H "Content-Type: application/json" \
-d '{
  "template1_data": "VGVtcGxhdGUgZGF0YSBhcXXDrA==",
  "template2_data": "VGVtcGxhdGUgZGF0YSBhcXXDrA==",
  "security_level": 1
}'
```

### 4. **Listar Templates Almacenados**
```bash
curl -X GET http://localhost:5000/templates
```

### 5. **Eliminar Template**
```bash
curl -X DELETE http://localhost:5000/templates/usuario_123
```

## 🔧 Formato de Datos

### **Template Data Format**
- **Formato**: Base64 encoding de datos binarios
- **Origen**: Generado desde imagen de huella capturada
- **Tamaño**: Variable (depende del algoritmo de template)
- **Codificación**: UTF-8

### **Ejemplo de Datos Válidos**
```json
{
  "template1_data": "iVBORw0KGgoAAAANSUhEUgAAAPIAAAFQCAYAAACZvQrwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAABHdSURBVHhe7d0JrFTHdQdwOyAIGGODwTYYGxuDwQYbGxs=",
  "template2_data": "iVBORw0KGgoAAAANSUhEUgAAAPIAAAFQCAYAAACZvQrwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAABHdSURBVHhe7d0JrFTHdQdwOyAIGGODwTYYGxuDwQYbGxs="
}
```

## 🔐 Niveles de Seguridad

| Nivel | Descripción | Sensibilidad |
|-------|-------------|--------------|
| 1     | Bajo        | Comparación flexible |
| 2     | Medio       | Comparación estándar |
| 3     | Alto        | Comparación estricta |

## 📊 Respuesta de Comparación

```json
{
  "success": true,
  "matched": true,
  "score": 95,
  "message": "Comparación exitosa",
  "comparison_info": {
    "template1_source": "usuario_123",
    "template2_source": "data",
    "security_level": 1
  }
}
```

### **Campos de Respuesta:**
- **success**: Boolean - Estado de la operación
- **matched**: Boolean - Si las huellas coinciden
- **score**: Number (0-100) - Puntuación de similitud
- **message**: String - Mensaje descriptivo
- **comparison_info**: Object - Información adicional

## ⚠️ Limitaciones Actuales

### **Funcionalidad Deshabilitada**
- La función `create_template` está temporalmente deshabilitada
- La comparación actual es simplificada (usa hash MD5)
- No hay algoritmo real de comparación biométrica

### **Para Reactivar Funcionalidad Completa:**
1. Habilitar función `create_template` en el código
2. Implementar algoritmo de comparación biométrica real
3. Manejar correctamente los tipos de datos ctypes

## 🚀 Flujo de Trabajo Recomendado

### **1. Registro de Usuario**
```bash
# Paso 1: Capturar huella y crear template
curl -X POST http://localhost:5000/capturar-huella \
-H "Content-Type: application/json" \
-d '{
  "create_template": true,
  "template_id": "usuario_123"
}'
```

### **2. Verificación de Usuario**
```bash
# Paso 2: Capturar huella nueva
curl -X POST http://localhost:5000/capturar-huella \
-H "Content-Type: application/json" \
-d '{
  "create_template": true
}'

# Paso 3: Comparar con template almacenado
curl -X POST http://localhost:5000/comparar-huellas \
-H "Content-Type: application/json" \
-d '{
  "template1_id": "usuario_123",
  "template2_data": "[template_de_respuesta_anterior]"
}'
```

## 🔍 Solución de Problemas

### **Errores Comunes:**
1. **"No se proporcionó template1 válido"**
   - Verificar que `template1_id` existe o `template1_data` sea válido
   - Asegurar que el Base64 sea válido

2. **"Template no encontrado"**
   - Verificar que el ID existe en templates almacenados
   - Listar templates disponibles con GET /templates

3. **"Error al crear template"**
   - Función create_template está deshabilitada
   - Usar imagen capturada directamente como "template"

### **Verificación de Templates:**
```bash
# Listar templates almacenados
curl -X GET http://localhost:5000/templates

# Respuesta esperada:
{
  "success": true,
  "templates": ["usuario_123", "usuario_456"],
  "count": 2
}
```

## 💡 Notas Importantes

1. **Base64 Encoding**: Los templates deben estar codificados en Base64 válido
2. **Almacenamiento**: Los templates se almacenan en memoria (se pierden al reiniciar)
3. **Tamaño**: No hay límite específico para el tamaño del template
4. **Compatibilidad**: Los templates son compatibles entre diferentes sesiones mientras la aplicación esté corriendo

## 🎯 Ejemplo Completo de Uso

```python
import requests
import base64
import json

# 1. Capturar primera huella
response1 = requests.post('http://localhost:5000/capturar-huella', 
                         json={'create_template': True, 'template_id': 'usuario_test'})
template1_data = response1.json()['data']['template']

# 2. Capturar segunda huella
response2 = requests.post('http://localhost:5000/capturar-huella', 
                         json={'create_template': True})
template2_data = response2.json()['data']['template']

# 3. Comparar huellas
comparison = requests.post('http://localhost:5000/comparar-huellas', 
                          json={
                              'template1_id': 'usuario_test',
                              'template2_data': template2_data,
                              'security_level': 1
                          })

# 4. Resultado
result = comparison.json()
print(f"Coincidencia: {result['matched']}")
print(f"Puntuación: {result['score']}")
```

---

**📞 Soporte**: Para más información, consulte la documentación completa en `PRODUCTION_SETUP.md` 