# 🔗 DISPOSITIVO PERSISTENTE SECUGEN

**Solución completa para identificador persistente del lector de huellas SecuGen**

## 🎯 Problema Resuelto

El dispositivo SecuGen cambia su ruta USB cada vez que se desconecta/reconecta:
- **Antes**: `/dev/bus/usb/001/007` → `/dev/bus/usb/001/008` (cambia el número)
- **Después**: `/dev/secugen_device` → **SIEMPRE LA MISMA RUTA**

## ✅ Beneficios

- 🔒 **Ruta fija**: `/dev/secugen_device` nunca cambia
- 🔄 **Persistente**: Funciona después de desconectar/reconectar
- 🛠️ **Fácil mantenimiento**: Scripts automáticos incluidos
- 📱 **Monitoreo**: Supervisión automática del dispositivo
- 🔧 **Auto-reparación**: Reset automático cuando sea necesario

## 📋 Archivos Creados

### Scripts Principales
- `identificar_dispositivo_persistente.py` - Identificación y configuración
- `crear_symlink_persistente.sh` - Creación del symlink
- `reset_usb_device.py` - Reset con soporte persistente
- `monitor_dispositivo_persistente.py` - Monitoreo automático

### Scripts de Ayuda
- `setup_persistent_device.sh` - Configuración automática
- `verificar_dispositivo.sh` - Verificación rápida
- `check_persistent_device.sh` - Verificación detallada

### Archivos de Configuración
- `docker/99SecuGen.rules` - Reglas udev actualizadas
- `logs/monitor_dispositivo.log` - Log de monitoreo

## 🚀 Instalación Rápida

### Opción 1: Configuración Automática
```bash
# Crear symlink persistente
sudo ./crear_symlink_persistente.sh

# Verificar funcionamiento
./verificar_dispositivo.sh
```

### Opción 2: Configuración Manual
```bash
# Identificar y configurar
python3 identificar_dispositivo_persistente.py

# Instalar reglas udev
sudo python3 identificar_dispositivo_persistente.py --install

# Verificar
python3 identificar_dispositivo_persistente.py --test
```

## 🛠️ Uso en Aplicaciones

### Antes (Problemático)
```python
# Ruta cambiante - PROBLEMÁTICO
device_path = "/dev/bus/usb/001/007"  # Cambia cada vez
```

### Después (Solución)
```python
# Ruta fija - SOLUCIÓN
device_path = "/dev/secugen_device"   # SIEMPRE la misma
```

## 📊 Monitoreo Automático

### Iniciar Monitoreo
```bash
# Monitoreo continuo en background
python3 monitor_dispositivo_persistente.py &

# O con nohup para que persista
nohup python3 monitor_dispositivo_persistente.py > monitor.log 2>&1 &
```

### Comandos de Monitoreo
```bash
# Ver estado actual
python3 monitor_dispositivo_persistente.py --status

# Reset manual
python3 monitor_dispositivo_persistente.py --reset

# Recrear symlink
python3 monitor_dispositivo_persistente.py --recreate

# Ayuda
python3 monitor_dispositivo_persistente.py --help
```

## 🔧 Mantenimiento

### Verificación Rápida
```bash
# Verificar que todo funciona
./verificar_dispositivo.sh

# Estado detallado
python3 monitor_dispositivo_persistente.py --status
```

### Reset Cuando Sea Necesario
```bash
# Reset completo del dispositivo
sudo python3 reset_usb_device.py

# O reset específico
python3 monitor_dispositivo_persistente.py --reset
```

### Recrear Symlink
```bash
# Si el symlink se pierde
sudo ./crear_symlink_persistente.sh

# O desde monitor
python3 monitor_dispositivo_persistente.py --recreate
```

## 📝 Configuración Avanzada

### Personalizar Monitoreo
Editar `monitor_dispositivo_persistente.py`:
```python
CONFIG = {
    'check_interval': 10,    # Segundos entre verificaciones
    'max_retries': 3,        # Intentos antes de reset
    'log_file': 'logs/monitor_dispositivo.log'
}
```

### Agregar al Startup
```bash
# Agregar al crontab para inicio automático
crontab -e

# Agregar esta línea:
@reboot cd /ruta/a/proyecto && python3 monitor_dispositivo_persistente.py
```

## 🚨 Solución de Problemas

### Problema: Symlink no existe
```bash
# Solución
sudo ./crear_symlink_persistente.sh
```

### Problema: Permisos insuficientes
```bash
# Verificar permisos
ls -la /dev/secugen_device

# Corregir permisos
sudo chmod 666 /dev/bus/usb/002/002
```

### Problema: SDK no conecta
```bash
# Reset del dispositivo
sudo python3 reset_usb_device.py

# O usar monitor
python3 monitor_dispositivo_persistente.py --reset
```

### Problema: Dispositivo no detectado
```bash
# Verificar dispositivo USB
lsusb | grep "1162:2201"

# Recrear symlink
sudo ./crear_symlink_persistente.sh
```

## 📋 Logs y Depuración

### Ver Logs de Monitoreo
```bash
# Logs en tiempo real
tail -f logs/monitor_dispositivo.log

# Logs históricos
cat logs/monitor_dispositivo.log
```

### Depuración Manual
```bash
# Verificar symlink
ls -la /dev/secugen_device

# Verificar target
readlink /dev/secugen_device

# Verificar dispositivo USB
lsusb | grep SecuGen

# Verificar reglas udev
cat /etc/udev/rules.d/99SecuGen.rules
```

## 🔄 Workflow Completo

### 1. Instalación Inicial
```bash
sudo ./crear_symlink_persistente.sh
```

### 2. Verificación
```bash
./verificar_dispositivo.sh
```

### 3. Integración en Aplicación
```python
# Usar en tu aplicación
DEVICE_PATH = "/dev/secugen_device"
```

### 4. Monitoreo (Opcional)
```bash
python3 monitor_dispositivo_persistente.py &
```

## 📱 Integración con Aplicación Principal

### Modificar app.py
```python
# Al inicio del archivo
SECUGEN_DEVICE = "/dev/secugen_device"

# En lugar de buscar dinámicamente, usar ruta fija
def get_device_path():
    if os.path.exists(SECUGEN_DEVICE):
        return SECUGEN_DEVICE
    else:
        # Fallback o error
        raise Exception("Dispositivo persistente no encontrado")
```

## 🎉 Resultado Final

- ✅ **Dispositivo persistente**: `/dev/secugen_device`
- ✅ **Scripts automáticos**: Instalación y mantenimiento
- ✅ **Monitoreo**: Supervisión automática
- ✅ **Auto-reparación**: Reset automático
- ✅ **Logs**: Registro completo de eventos
- ✅ **Documentación**: Guías completas incluidas

## 📞 Soporte

Si tienes problemas:

1. **Verificar estado**: `python3 monitor_dispositivo_persistente.py --status`
2. **Reset manual**: `sudo python3 reset_usb_device.py`
3. **Recrear symlink**: `sudo ./crear_symlink_persistente.sh`
4. **Ver logs**: `tail -f logs/monitor_dispositivo.log`

---

**¡El dispositivo SecuGen ahora tiene una ruta fija y persistente!** 🎯 