# 🔧 Guía de Instalación - Sistema de Captura de Huellas Digitales SecuGen

## 📋 Prerrequisitos del Sistema

### Sistema Operativo
- **Linux Ubuntu/Debian** (Recomendado: Ubuntu 20.04 LTS o superior)
- **Arquitectura**: x64 (64-bit)

### Hardware Requerido
- **Lector de huellas SecuGen** (Modelos compatibles: Hamster Pro 20, U20, etc.)
- **Puerto USB** disponible
- **Memoria RAM**: Mínimo 2GB
- **Espacio en disco**: Mínimo 500MB libres

---

## 🚀 Instalación Paso a Paso

### 1. Actualización del Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalación de Dependencias Base

```bash
# Instalar Python 3 y herramientas de desarrollo
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Instalar bibliotecas USB necesarias
sudo apt install -y libusb-0.1-4 libusb-dev

# Instalar Docker y Docker Compose (opcional para desarrollo)
sudo apt install -y docker.io docker-compose

# Instalar herramientas de desarrollo
sudo apt install -y build-essential cmake pkg-config
```

### 3. Configuración de Permisos USB

#### 3.1 Configurar reglas udev para el dispositivo SecuGen

```bash
# Copiar las reglas udev incluidas en el repositorio
sudo cp docker/99SecuGen.rules /etc/udev/rules.d/

# Recargar las reglas udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 3.2 Agregar usuario al grupo plugdev

```bash
# Agregar el usuario actual al grupo plugdev
sudo usermod -a -G plugdev $USER

# Cerrar sesión y volver a iniciar para que los cambios surtan efecto
# O ejecutar: newgrp plugdev
```

### 4. Preparación del Entorno Python

#### 4.1 Crear entorno virtual

```bash
# Navegar al directorio del proyecto
cd /ruta/al/proyecto/driver-bloqueo-digital-huella-main

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

#### 4.2 Instalar dependencias Python

```bash
# Instalar dependencias mínimas (sin PostgreSQL)
pip install -r requirements-minimal.txt

# O instalar dependencias completas (con PostgreSQL)
pip install -r requirements.txt
```

**Contenido de `requirements-minimal.txt`:**
```txt
flask==2.0.1
werkzeug==2.0.1
flask-cors==3.0.10
python-dotenv==0.19.0
pyusb
```

### 5. Configuración del SDK SecuGen

#### 5.1 Verificar estructura del SDK

```bash
# Verificar que existan los archivos del SDK
ls -la sdk/
ls -la lib/linux3/
```

#### 5.2 Configurar variables de entorno

```bash
# Agregar al archivo ~/.bashrc o ejecutar cada vez
export LD_LIBRARY_PATH=$PWD/lib/linux3:$LD_LIBRARY_PATH
export PYTHONPATH=$PWD:$PYTHONPATH
```

### 6. Verificación del Dispositivo USB

#### 6.1 Conectar y verificar el dispositivo

```bash
# Conectar el lector SecuGen por USB
# Verificar que el dispositivo sea detectado
lsusb | grep -i secugen

# Verificar permisos del dispositivo
ls -la /dev/bus/usb/*/
```

**Salida esperada:**
```
Bus 002 Device 007: ID 1162:2201 SecuGen Corp Hamster Pro 20
```

#### 6.2 Verificar permisos

```bash
# Verificar que el dispositivo tenga permisos correctos
ls -la /dev/bus/usb/002/007  # Ajustar números según lsusb
```

**Permisos correctos:**
```
crw-rw-rw- 1 root plugdev 189, 134 Jul 10 22:30 /dev/bus/usb/002/007
```

---

## 🔄 Ejecución de la Aplicación

### 1. Activar entorno y configurar variables

```bash
# Activar entorno virtual
source venv/bin/activate

# Configurar variables de entorno
export LD_LIBRARY_PATH=$PWD/lib/linux3:$LD_LIBRARY_PATH
export PYTHONPATH=$PWD:$PYTHONPATH
```

### 2. Ejecutar la aplicación

```bash
# Ejecutar la aplicación Flask
python3 app.py
```

**Salida esperada:**
```
Iniciando dispositivo...
Inicializando...
Abriendo dispositivo...
Intentando abrir dispositivo con ID: 0
Dispositivo abierto exitosamente con ID: 0
Dispositivo inicializado correctamente
 * Running on all addresses.
 * Running on http://192.168.1.108:5000/ (Press CTRL+C to quit)
```

### 3. Ejecutar en segundo plano (opcional)

```bash
# Ejecutar en segundo plano
nohup python3 app.py > app.log 2>&1 &
```

---

## 🧪 Pruebas y Verificación

### 1. Verificar que la aplicación responde

```bash
# Verificar que el servidor está ejecutándose
curl http://localhost:5000
```

### 2. Probar inicialización del dispositivo

```bash
curl -X POST -H "Content-Type: application/json" http://localhost:5000/initialize
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Dispositivo ya está inicializado correctamente"
}
```

### 3. Probar control del LED

```bash
# Encender LED
curl -X POST -H "Content-Type: application/json" -d '{"state": true}' http://localhost:5000/led

# Apagar LED
curl -X POST -H "Content-Type: application/json" -d '{"state": false}' http://localhost:5000/led
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "LED del lector encendido"
}
```

### 4. Probar captura de huellas

```bash
# Capturar huella sin guardar imagen
curl -X POST -H "Content-Type: application/json" -d '{"save_image": false}' http://localhost:5000/capturar-huella

# Capturar huella y guardar imagen
curl -X POST -H "Content-Type: application/json" -d '{"save_image": true}' http://localhost:5000/capturar-huella
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Huella capturada exitosamente",
  "capture_time": "2025-07-10 22:46:19"
}
```

---

## 📊 Endpoints Disponibles

| Endpoint | Método | Descripción | Parámetros |
|----------|---------|-------------|------------|
| `/initialize` | POST | Inicializar dispositivo | Ninguno |
| `/led` | POST | Controlar LED | `{"state": true/false}` |
| `/capturar-huella` | POST | Capturar huella digital | `{"save_image": true/false}` |

---

## 🔧 Solución de Problemas

### Error: "cannot import name 'PYSGFPLib'"

**Problema:** Error de importación del SDK.

**Solución:**
```bash
# Verificar que las importaciones en app.py sean correctas
# Debe ser: from sdk import PYSGFPLib
# No: from sgfplib import PYSGFPLib
```

### Error: "libusb-0.1.so.4: cannot open shared object file"

**Problema:** Falta la biblioteca libusb.

**Solución:**
```bash
sudo apt install libusb-0.1-4
```

### Error: "No se pudo abrir el dispositivo con ningún ID"

**Problema:** Permisos USB o dispositivo no conectado.

**Solución:**
```bash
# Verificar conexión del dispositivo
lsusb | grep -i secugen

# Verificar permisos
ls -la /dev/bus/usb/*/

# Reconfigurar permisos
sudo cp docker/99SecuGen.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

# Agregar usuario al grupo plugdev
sudo usermod -a -G plugdev $USER
```

### Error: "Error de acceso al dispositivo"

**Problema:** Dispositivo ya en uso o reinicialización innecesaria.

**Solución:**
El dispositivo se inicializa automáticamente al arrancar la aplicación. No es necesario reinicializarlo manualmente.

---

## 🚦 Scripts de Automatización

### Script de inicio automático

Crear `start.sh`:
```bash
#!/bin/bash
cd /ruta/al/proyecto/driver-bloqueo-digital-huella-main
source venv/bin/activate
export LD_LIBRARY_PATH=$PWD/lib/linux3:$LD_LIBRARY_PATH
export PYTHONPATH=$PWD:$PYTHONPATH
python3 app.py
```

```bash
chmod +x start.sh
./start.sh
```

### Script de verificación

Crear `test.sh`:
```bash
#!/bin/bash
echo "🔍 Verificando dispositivo USB..."
lsusb | grep -i secugen

echo "🔍 Probando inicialización..."
curl -X POST -H "Content-Type: application/json" http://localhost:5000/initialize

echo "🔍 Probando LED..."
curl -X POST -H "Content-Type: application/json" -d '{"state": true}' http://localhost:5000/led

echo "🔍 Probando captura..."
curl -X POST -H "Content-Type: application/json" -d '{"save_image": false}' http://localhost:5000/capturar-huella
```

---

## 📞 Soporte

### Logs de depuración

```bash
# Ver logs de la aplicación
tail -f app.log

# Ver logs del sistema USB
dmesg | grep -i usb

# Verificar procesos Python
ps aux | grep python3
```

### Información del sistema

```bash
# Información del sistema
uname -a
python3 --version
lsusb
groups
```

---

## ✅ Checklist de Instalación

- [ ] Sistema Ubuntu/Debian actualizado
- [ ] Dependencias instaladas (Python, libusb, etc.)
- [ ] Reglas udev configuradas
- [ ] Usuario en grupo plugdev
- [ ] Entorno virtual creado
- [ ] Dependencias Python instaladas
- [ ] Variables de entorno configuradas
- [ ] Dispositivo USB conectado y detectado
- [ ] Aplicación ejecutándose correctamente
- [ ] Endpoints probados y funcionando
- [ ] LED controlable
- [ ] Captura de huellas funcional

---

## 🎯 Resultado Esperado

Al completar esta instalación, deberías tener:

✅ **Aplicación Flask** ejecutándose en `http://localhost:5000`  
✅ **Dispositivo SecuGen** completamente funcional  
✅ **Control del LED** operativo  
✅ **Captura de huellas** funcionando  
✅ **API REST** lista para integración  

---

**¡Instalación completada! 🎉**
