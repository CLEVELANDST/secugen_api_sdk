# 🔐 Driver Bloqueo Digital Huella
**Sistema de control para lector de huellas SecuGen con API REST y pruebas de stress.**  

## 📚 Documentación Completa

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

## 🎯 Inicio Rápido para Producción

```bash
# 1. Verificar sistema
./pre_production_check.sh

# 2. Configurar para producción (automático)
./setup_production.sh

# 3. Iniciar aplicación
./start_production.sh

# 4. Verificar estado
./status_production.sh
```

## 📋 Requisitos Previos  
- Linux (Ubuntu/CentOS)  
- Python 3.8+
- libusb-0.1-4
- Lector de huellas SecuGen
- Git  

## 🚀 Instalación Automática (Recomendada)

### 1. Clonar el Repositorio  
```bash
git clone https://github.com/tu-usuario/driver-bloqueo-digital-huella.git
cd driver-bloqueo-digital-huella
```

### 2. Configuración Automática
```bash
# Verificar que todo esté listo
./pre_production_check.sh

# Configurar automáticamente para producción
./setup_production.sh

# Iniciar la aplicación
./start_production.sh
```

¡Eso es todo! El sistema configurará automáticamente:
- ✅ Dependencias del sistema
- ✅ Entorno Python
- ✅ Permisos USB
- ✅ Servicios systemd
- ✅ Monitoreo automático
- ✅ Backups programados

### 3. Verificar Instalación
```bash
# Ver estado completo del sistema
./status_production.sh

# Probar la API
curl -X POST http://localhost:5000/initialize
```

## 🛠️ Instalación Manual (Avanzada)

Si prefieres instalar manualmente, consulta **[instalacion.md](./instalacion.md)** para instrucciones detalladas paso a paso.

## 🎮 Administración del Sistema

### Scripts de Administración
```bash
./start_production.sh      # Iniciar aplicación
./stop_production.sh       # Parar aplicación
./restart_production.sh    # Reiniciar aplicación
./status_production.sh     # Ver estado completo
./backup_production.sh     # Crear backup
./monitor_production.sh    # Monitorear sistema
./show_commands.sh         # Ver todos los comandos
```

### Servicios systemd
```bash
sudo systemctl start secugen-fingerprint-api     # Iniciar servicio
sudo systemctl stop secugen-fingerprint-api      # Parar servicio
sudo systemctl status secugen-fingerprint-api    # Ver estado
sudo systemctl enable secugen-fingerprint-api    # Auto-inicio
```

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

## 🧪 Pruebas de Stress

### Ejecutar Pruebas
```bash
# Prueba básica (recomendada)
python3 simple_stress_test.py

# Prueba intensa automática
python3 run_stress_test.py

# Prueba extrema con concurrencia
python3 extreme_stress_test.py
```

**Para más información, consulta: [README_STRESS_TESTS.md](./README_STRESS_TESTS.md)**

## 🔧 Solución de Problemas

### Diagnóstico Automático
```bash
# Verificar estado completo del sistema
./status_production.sh

# Verificar configuración
./pre_production_check.sh

# Ver todos los comandos disponibles
./show_commands.sh
```

### Problemas Comunes

#### Dispositivo USB No Detectado
```bash
# Verificar dispositivo
lsusb | grep -i secugen

# Recargar reglas USB
sudo udevadm control --reload-rules
sudo udevadm trigger

# Verificar permisos
groups  # Debe incluir 'plugdev'
```

#### Aplicación No Responde
```bash
# Reiniciar aplicación
./restart_production.sh

# Ver logs
tail -f logs/app.log

# Verificar puerto
netstat -tuln | grep 5000
```

#### Error de Inicialización
```bash
# Verificar dependencias
./pre_production_check.sh

# Reconfigurar sistema
./setup_production.sh
```

**Para solución de problemas detallada, consulta: [instalacion.md](./instalacion.md)**

## 📊 Monitoreo y Logs

### Logs Disponibles
```bash
tail -f logs/app.log           # Log principal
tail -f logs/startup.log       # Log de inicio
tail -f logs/monitor.log       # Log de monitoreo
sudo journalctl -u secugen-fingerprint-api -f  # Logs del servicio
```

### Backups Automáticos
```bash
ls -la backups/               # Ver backups disponibles
./backup_production.sh        # Crear backup manual
```

## 📁 Estructura del Proyecto
```bash
driver-bloqueo-digital-huella/
├── 📄 Aplicación Principal
│   ├── app.py                          # API Flask principal
│   ├── sdk/                            # SDK de SecuGen
│   └── lib/                            # Bibliotecas compartidas
├── 🚀 Scripts de Producción
│   ├── setup_production.sh             # Configuración automática
│   ├── pre_production_check.sh         # Verificación del sistema
│   ├── start_production.sh             # Iniciar aplicación
│   ├── stop_production.sh              # Parar aplicación
│   ├── restart_production.sh           # Reiniciar aplicación
│   ├── status_production.sh            # Estado del sistema
│   ├── backup_production.sh            # Crear backups
│   ├── monitor_production.sh           # Monitorear sistema
│   └── show_commands.sh                # Mostrar comandos
├── 🧪 Pruebas de Stress
│   ├── simple_stress_test.py           # Prueba básica
│   ├── run_stress_test.py              # Prueba intensa
│   ├── extreme_stress_test.py          # Prueba extrema
│   └── quick_test.py                   # Prueba rápida
├── 📖 Documentación
│   ├── PRODUCTION_SETUP.md             # Guía de producción
│   ├── README_STRESS_TESTS.md          # Guía de pruebas
│   ├── instalacion.md                  # Guía de instalación
│   └── comandos_curl.md                # Comandos API
├── ⚙️ Configuración
│   ├── config/production.env           # Config de producción
│   ├── venv/                           # Entorno Python
│   ├── logs/                           # Logs del sistema
│   └── backups/                        # Backups automáticos
└── 🔧 Utilidades
    ├── docker/99SecuGen.rules          # Reglas udev
    ├── check_device.sh                 # Verificar dispositivo
    └── requirements-minimal.txt        # Dependencias Python
```

## 🌟 Características

- ✅ **API REST completa** para control de huellas digitales
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
- 🚀 Listo para producción con configuración robusta
- 📊 Incluye herramientas de monitoreo y diagnóstico