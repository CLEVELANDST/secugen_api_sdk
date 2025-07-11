# 🚀 Configuración para Producción - Sistema de Huellas Digitales SecuGen

## 📋 Resumen

Este documento describe cómo configurar el sistema de huellas digitales SecuGen para producción usando el script automatizado `setup_production.sh`.

## 🎯 Características de la Configuración de Producción

- ✅ **Automatización completa**: Un script configura todo
- ✅ **Servicio systemd**: Inicio automático del sistema
- ✅ **Monitoreo automático**: Verificación cada 5 minutos
- ✅ **Backups automáticos**: Backup diario a las 2 AM
- ✅ **Scripts de administración**: Inicio, parada, reinicio, estado
- ✅ **Logs centralizados**: Todos los logs en un directorio
- ✅ **Configuración segura**: Permisos y variables de entorno
- ✅ **Recuperación automática**: Reinicio en caso de fallos

## 🔧 Instalación Rápida

### 1. **Ejecutar Script de Configuración**
```bash
./setup_production.sh
```

### 2. **Reiniciar Sesión** (Importante)
```bash
# Cerrar sesión y volver a iniciar para aplicar cambios de grupo
logout
# o
sudo su - $USER
```

### 3. **Iniciar la Aplicación**
```bash
./start_production.sh
```

### 4. **Verificar Estado**
```bash
./status_production.sh
```

## 📁 Estructura de Archivos Creados

```
driver-bloqueo-digital-huella-main/
├── setup_production.sh          # Script de configuración (YA EJECUTADO)
├── start_production.sh          # Iniciar aplicación
├── stop_production.sh           # Parar aplicación
├── restart_production.sh        # Reiniciar aplicación
├── status_production.sh         # Ver estado
├── backup_production.sh         # Crear backup
├── monitor_production.sh        # Monitorear sistema
├── config/
│   └── production.env          # Configuración de producción
├── logs/                       # Directorio de logs
│   ├── app.log                # Log principal
│   ├── startup.log            # Log de inicio
│   ├── shutdown.log           # Log de parada
│   ├── restart.log            # Log de reinicio
│   └── monitor.log            # Log de monitoreo
└── backups/                    # Backups automáticos
    └── backup_YYYYMMDD_HHMMSS.tar.gz
```

## 🎮 Comandos de Administración

### **Scripts Locales**
```bash
# Iniciar aplicación
./start_production.sh

# Parar aplicación
./stop_production.sh

# Reiniciar aplicación
./restart_production.sh

# Ver estado completo
./status_production.sh

# Crear backup manual
./backup_production.sh

# Monitorear sistema
./monitor_production.sh
```

### **Servicios Systemd**
```bash
# Iniciar servicio
sudo systemctl start secugen-fingerprint-api

# Parar servicio
sudo systemctl stop secugen-fingerprint-api

# Reiniciar servicio
sudo systemctl restart secugen-fingerprint-api

# Ver estado del servicio
sudo systemctl status secugen-fingerprint-api

# Ver logs en tiempo real
sudo journalctl -u secugen-fingerprint-api -f

# Habilitar inicio automático
sudo systemctl enable secugen-fingerprint-api

# Deshabilitar inicio automático
sudo systemctl disable secugen-fingerprint-api
```

## 📊 Monitoreo y Logs

### **Logs Principales**
```bash
# Log de la aplicación
tail -f logs/app.log

# Log de inicio
tail -f logs/startup.log

# Log de monitoreo
tail -f logs/monitor.log

# Logs del sistema
sudo journalctl -u secugen-fingerprint-api -f
```

### **Monitoreo Automático**
El sistema incluye monitoreo automático que:
- ✅ Verifica que la aplicación esté corriendo cada 5 minutos
- ✅ Reinicia automáticamente si hay problemas
- ✅ Verifica que la API responda
- ✅ Controla el uso de memoria
- ✅ Rota logs automáticamente

## 🔒 Seguridad y Permisos

### **Permisos USB Configurados**
- Reglas udev para dispositivos SecuGen
- Usuario agregado al grupo `plugdev`
- Acceso completo a dispositivos USB

### **Configuración de Seguridad**
- Servicio ejecutado como usuario no-root
- Directorios protegidos
- Variables de entorno seguras
- Logs con permisos restringidos

## 📈 Backup y Recuperación

### **Backup Automático**
- Backup diario a las 2:00 AM
- Mantiene últimos 10 backups
- Excluye archivos temporales y logs

### **Backup Manual**
```bash
# Crear backup inmediato
./backup_production.sh

# Restaurar desde backup
cd ..
tar -xzf driver-bloqueo-digital-huella-main/backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

## 🛠️ Configuración Avanzada

### **Archivo de Configuración**
```bash
# Editar configuración
nano config/production.env
```

Variables disponibles:
- `FLASK_ENV`: Entorno de Flask
- `FLASK_DEBUG`: Debug mode
- `FLASK_HOST`: Host de escucha
- `FLASK_PORT`: Puerto de escucha
- `LOG_LEVEL`: Nivel de logging
- `LOG_FILE`: Archivo de log

### **Personalizar Monitoreo**
```bash
# Editar script de monitoreo
nano monitor_production.sh

# Editar cron para cambiar frecuencia
crontab -e
```

## 🔍 Diagnóstico y Solución de Problemas

### **Verificar Estado Completo**
```bash
./status_production.sh
```

### **Problemas Comunes**

#### **1. Dispositivo USB No Detectado**
```bash
# Verificar dispositivo
lsusb | grep -i secugen

# Verificar reglas udev
ls -la /etc/udev/rules.d/99SecuGen.rules

# Recargar reglas
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### **2. Aplicación No Inicia**
```bash
# Ver logs de inicio
tail -f logs/startup.log

# Verificar puerto
netstat -tuln | grep :5000

# Verificar permisos
ls -la app.py
```

#### **3. API No Responde**
```bash
# Probar endpoint
curl -X POST http://localhost:5000/initialize

# Verificar proceso
ps aux | grep python3

# Ver logs de aplicación
tail -f logs/app.log
```

#### **4. Servicio Systemd Falla**
```bash
# Ver estado detallado
sudo systemctl status secugen-fingerprint-api

# Ver logs del servicio
sudo journalctl -u secugen-fingerprint-api -n 50

# Reiniciar servicio
sudo systemctl restart secugen-fingerprint-api
```

## 📋 Checklist de Verificación

### **Después de la Instalación**
- [ ] Script `setup_production.sh` ejecutado exitosamente
- [ ] Sesión reiniciada para aplicar cambios de grupo
- [ ] Aplicación iniciada con `./start_production.sh`
- [ ] Estado verificado con `./status_production.sh`
- [ ] API responde: `curl -X POST http://localhost:5000/initialize`
- [ ] Dispositivo USB detectado: `lsusb | grep -i secugen`
- [ ] Servicio systemd habilitado: `sudo systemctl is-enabled secugen-fingerprint-api`

### **Verificación Semanal**
- [ ] Revisar logs: `ls -la logs/`
- [ ] Verificar backups: `ls -la backups/`
- [ ] Probar endpoints de la API
- [ ] Verificar uso de disco y memoria
- [ ] Revisar cron jobs: `crontab -l`

## 🎯 Pruebas de Stress en Producción

### **Ejecutar Pruebas**
```bash
# Prueba básica
python3 simple_stress_test.py

# Prueba intensa
python3 run_stress_test.py

# Prueba extrema (usar con precaución)
python3 extreme_stress_test.py
```

### **Interpretar Resultados**
- **>95% éxito**: Sistema excelente
- **85-94% éxito**: Sistema bueno
- **<85% éxito**: Revisar configuración

## 🌟 Ventajas de esta Configuración

1. **Automatización Total**: Un script configura todo
2. **Producción Lista**: Configuración robusta y segura
3. **Monitoreo Automático**: Detección y corrección de problemas
4. **Backups Automáticos**: Protección de datos
5. **Administración Fácil**: Scripts simples para todas las operaciones
6. **Logs Centralizados**: Fácil diagnóstico
7. **Recuperación Automática**: Reinicio en caso de fallos
8. **Servicio Systemd**: Integración completa con el sistema

## 🚀 Inicio Rápido para Producción

```bash
# 1. Ejecutar configuración
./setup_production.sh

# 2. Reiniciar sesión
logout && login

# 3. Iniciar aplicación
./start_production.sh

# 4. Verificar estado
./status_production.sh

# 5. Probar API
curl -X POST http://localhost:5000/initialize
```

¡Tu sistema está listo para producción! 🎉 