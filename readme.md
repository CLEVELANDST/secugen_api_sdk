# 🔐 Driver Bloqueo Digital Huella
**Sistema de control para lector de huellas SecuGen con API REST, sistema robusto y Docker.**  

## 🐳 **DOCKERIZACIÓN - MIGRACIÓN ULTRA FÁCIL**

### 🚀 **Usar con Docker (RECOMENDADO para migración)**

```bash
# 1. Clonar proyecto
git clone <tu-repositorio>
cd driver-bloqueo-digital-huella-main

# 2. Configurar host (solo primera vez)
./docker-setup-host.sh

# 3. Iniciar con Docker
docker-compose up -d

# 4. Verificar funcionamiento
curl -X POST http://localhost:5000/initialize
```

### 🎯 **Ventajas de la versión Docker:**
- ✅ **Migración en 3 comandos** (sin dependencias)
- ✅ **Funciona en cualquier Linux** (Ubuntu, CentOS, etc.)
- ✅ **Entorno consistente** siempre
- ✅ **Fácil actualización** con `docker-compose pull`
- ✅ **Rollback rápido** si algo falla
- ✅ **Monitoreo integrado** con logs centralizados

---

## 🖥️ **MIGRACIÓN A OTRO PC - SISTEMA ROBUSTO**

### 🚀 **Scripts Para Que El Lector NUNCA Falle**

Si llevas este proyecto a otro PC, ejecuta estos scripts en orden para garantizar que el lector funcione siempre:

#### **1. Configuración Inicial (Solo la primera vez)**
```bash
# Copiar el proyecto
git clone <tu-repositorio>
cd driver-bloqueo-digital-huella-main

# Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-venv libusb-0.1-4 build-essential

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors numpy requests

# Configurar permisos USB (CRÍTICO)
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER

# Instalar reglas udev para dispositivo persistente
sudo cp docker/99SecuGen.rules /etc/udev/rules.d/
sudo chmod 644 /etc/udev/rules.d/99SecuGen.rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Hacer ejecutables los scripts
chmod +x iniciar_sistema_robusto.sh parar_sistema.sh
chmod +x reset_usb_device.py monitor_sistema_completo.py test_sistema_robusto.py

# REINICIAR EL SISTEMA (necesario para grupos de usuario)
sudo reboot
```

#### **2. Uso Diario (Después del reinicio)**
```bash
# COMANDO PRINCIPAL - Iniciar sistema robusto
./iniciar_sistema_robusto.sh

# Responder 'y' cuando pregunte sobre el monitor para máxima robustez
```

#### **3. Verificación (Opcional)**
```bash
# Probar que funciona
python3 test_sistema_robusto.py

# Probar API
curl -X POST http://localhost:5000/initialize
```

#### **4. Parada Segura (Al terminar)**
```bash
# Parar sistema de forma segura
./parar_sistema.sh
```

### 🛡️ **Scripts de Emergencia**

Si algo falla, ejecuta en orden:

```bash
# 1. Parar todo
./parar_sistema.sh

# 2. Reset USB (soluciona Error 2)
sudo python3 reset_usb_device.py

# 3. Reiniciar sistema
./iniciar_sistema_robusto.sh

# 4. Verificar
python3 test_sistema_robusto.py
```

### 📋 **Checklist de Migración**

**✅ Antes de copiar el proyecto:**
- [ ] Dispositivo SecuGen conectado
- [ ] Ubuntu/Debian actualizado
- [ ] Permisos de sudo disponibles

**✅ Después de la configuración inicial:**
- [ ] Ejecutar `lsusb | grep "1162:2201"` - debe mostrar el dispositivo
- [ ] Ejecutar `ls -la /dev/secugen_device` - debe mostrar el symlink
- [ ] Ejecutar `groups` - debe incluir 'dialout' y 'plugdev'

**✅ Para uso diario:**
- [ ] Siempre usar `./iniciar_sistema_robusto.sh`
- [ ] Siempre usar `./parar_sistema.sh` para parar
- [ ] Nunca usar `python3 app.py` directamente

### 🔧 **Archivos Críticos para Migración**

Asegúrate de copiar estos archivos:
- `iniciar_sistema_robusto.sh` - **CRÍTICO** - Inicio robusto
- `parar_sistema.sh` - **CRÍTICO** - Parada segura
- `monitor_sistema_completo.py` - **IMPORTANTE** - Monitoreo automático
- `reset_usb_device.py` - **IMPORTANTE** - Reset USB mejorado
- `test_sistema_robusto.py` - **ÚTIL** - Pruebas del sistema
- `docker/99SecuGen.rules` - **CRÍTICO** - Reglas udev
- `app.py` - **CRÍTICO** - Aplicación principal
- `app_backup.py` - **IMPORTANTE** - Backup para restauración
- `sdk/` - **CRÍTICO** - SDK de SecuGen
- `lib/` - **CRÍTICO** - Librerías

### 🎯 **Comandos Rápidos de Referencia**

```bash
# Inicio completo (UN SOLO COMANDO)
./iniciar_sistema_robusto.sh

# Parada segura
./parar_sistema.sh

# Reset si falla
sudo python3 reset_usb_device.py

# Verificar estado
python3 test_sistema_robusto.py

# Ver logs
tail -f logs/sistema_robusto.log
```

### 📄 **Cheat Sheet Completo**
Para una referencia rápida completa, consulta: **[COMANDOS_MIGRACION_PC.md](./COMANDOS_MIGRACION_PC.md)**

---

## 📚 Documentación Completa

### 🐳 **Docker (NUEVO)**
- 📖 **[README_DOCKER.md](./README_DOCKER.md)** - Guía completa de Docker
- 🔧 **Configuración automática con Docker Compose**
- 🚀 **Migración ultra fácil entre PCs**
- 📦 **Entorno consistente y reproducible**

### 🛡️ **Sistema Robusto**
- 📖 **[README_SISTEMA_ROBUSTO.md](./README_SISTEMA_ROBUSTO.md)** - Guía completa del sistema robusto
- 📖 **[RESUMEN_MEJORAS.md](./RESUMEN_MEJORAS.md)** - Resumen ejecutivo de mejoras
- 🔧 **Prevención automática de problemas**
- 🔄 **Reset USB automático**
- 🔍 **Monitoreo continuo**

### 🚀 **Configuración para Producción**
- 📖 **[PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md)** - Guía completa para configurar el sistema en producción
- ⚙️ **Configuración automática con un solo comando**
- 🎮 **Scripts de administración incluidos**
- 📊 **Monitoreo y backups automáticos**

### 🧪 **Pruebas de Stress**
- 📖 **[README_STRESS_TESTS.md](./README_STRESS_TESTS.md)** - Guía completa de pruebas de stress
- 🔥 **Pruebas automáticas de rendimiento**
- 📈 **Análisis de resistencia del sistema**
- 🎯 **Scripts de prueba incluidos**

### 🛠️ **Instalación y Configuración**
- 📖 **[instalacion.md](./instalacion.md)** - Guía detallada de instalación paso a paso
- 🔧 **Configuración de permisos USB**
- 📝 **Solución de problemas comunes**
- ✅ **Verificación de instalación**

### 🔍 **Testing y API**
- 📖 **[comandos_curl.md](./comandos_curl.md)** - Comandos curl para probar la API
- 🌐 **Endpoints de comparación de huellas**
- 🧪 **Ejemplos de uso práctico**
- 📊 **Pruebas de funcionalidad**

---

## 🎯 Inicio Rápido

### 🐳 **Con Docker (RECOMENDADO)**
```bash
# Configurar host y iniciar
./docker-setup-host.sh
docker-compose up -d

# Verificar
curl -X POST http://localhost:5000/initialize
```

### 🎯 **Sistema Robusto Nativo**
```bash
# Configuración inicial (solo primera vez)
./configurar_nuevo_pc.sh

# Iniciar sistema robusto
./iniciar_sistema_robusto.sh

# Verificar funcionamiento
python3 test_sistema_robusto.py

# Parar sistema
./parar_sistema.sh
```

### 🚀 **Producción Tradicional**
```bash
# Verificar sistema
./pre_production_check.sh

# Configurar para producción (automático)
./setup_production.sh

# Iniciar aplicación
./start_production.sh

# Verificar estado
./status_production.sh
```

## 📋 Requisitos Previos  
- Linux (Ubuntu/CentOS)  
- Python 3.8+ (para versión nativa)
- Docker y Docker Compose (para versión Docker)
- libusb-0.1-4
- Lector de huellas SecuGen
- Git  

## 🌐 API REST - Endpoints Disponibles

### 1. Inicializar Dispositivo
```bash
curl -X POST http://localhost:5000/initialize
```

### 2. Control del LED
```bash
# Encender LED
curl -X POST http://localhost:5000/led \
-H "Content-Type: application/json" \
-d '{"state": true}'

# Apagar LED
curl -X POST http://localhost:5000/led \
-H "Content-Type: application/json" \
-d '{"state": false}'
```

### 3. Capturar Huella
```bash
curl -X POST http://localhost:5000/capturar-huella \
-H "Content-Type: application/json" \
-d '{"save_image": false, "create_template": true, "template_id": "user_001"}'
```

### 4. Comparar Huellas
```bash
curl -X POST http://localhost:5000/comparar-huellas \
-H "Content-Type: application/json" \
-d '{"template1_id": "user_001", "template2_id": "user_002", "security_level": 1}'
```

### 5. Gestión de Templates
```bash
# Listar templates
curl -X GET http://localhost:5000/templates

# Eliminar template
curl -X DELETE http://localhost:5000/templates/user_001
```

**Para más ejemplos, consulta: [comandos_curl.md](./comandos_curl.md)**

## 🔧 Solución de Problemas

### Diagnóstico Automático
```bash
# Verificar estado completo del sistema
./status_production.sh

# Verificar configuración
./pre_production_check.sh

# Con sistema robusto
python3 test_sistema_robusto.py

# Con Docker
docker-compose logs -f
```

### Problemas Comunes

#### Error 2 del SDK (SGFDX_ERROR_FUNCTION_FAILED)
```bash
# Sistema robusto
sudo python3 reset_usb_device.py

# Docker
docker-compose restart
```

#### Puerto ocupado
```bash
# Sistema robusto
./parar_sistema.sh
./iniciar_sistema_robusto.sh

# Docker
docker-compose down
docker-compose up -d
```

#### Dispositivo USB no detectado
```bash
# Verificar dispositivo
lsusb | grep -i secugen

# Recargar reglas USB
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## 🌟 Características

- ✅ **API REST completa** para control de huellas digitales
- ✅ **Sistema robusto** que previene y soluciona problemas automáticamente
- ✅ **Dockerización completa** para migración ultra fácil
- ✅ **Configuración automática** con un solo comando
- ✅ **Pruebas de stress** integradas para verificar rendimiento
- ✅ **Monitoreo automático** con recuperación ante fallos
- ✅ **Backups programados** para proteger datos
- ✅ **Scripts de administración** para todas las operaciones
- ✅ **Servicios systemd** para integración con el sistema
- ✅ **Logs centralizados** para fácil diagnóstico
- ✅ **Documentación completa** con ejemplos prácticos

## 📝 Notas Importantes

- 🔒 El sistema se ejecuta como usuario no-root para mayor seguridad
- 🔌 Compatible con lectores SecuGen (ID: 1162:2201 y otros modelos)
- 🐧 Optimizado para sistemas Linux (Ubuntu/Debian)
- 🐳 Versión Docker funciona en cualquier distribución Linux
- 🚀 Listo para producción con configuración robusta
- 📊 Incluye herramientas de monitoreo y diagnóstico 