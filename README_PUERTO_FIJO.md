# 🔌 FIJACIÓN DE PUERTO USB PARA DISPOSITIVO SECUGEN

## 📋 Resumen
Esta documentación explica cómo configurar el dispositivo SecuGen para que permanezca en un puerto USB específico y no cambie cuando se reconecta.

## 🎯 Problema Resuelto
- **Problema**: El dispositivo SecuGen cambia de puerto USB cada vez que se desconecta/reconecta
- **Solución**: Configuración de reglas udev y scripts de gestión para mantener el dispositivo en un puerto específico

## 📁 Archivos Creados

### 1. `identificar_puertos_usb.sh`
**Propósito**: Identificar puertos USB disponibles y obtener información del dispositivo SecuGen.

```bash
./identificar_puertos_usb.sh
```

**Funcionalidades**:
- ✅ Muestra información del dispositivo SecuGen actual
- 🌳 Visualiza topología de puertos USB
- 🔌 Lista puertos USB disponibles
- 💡 Proporciona recomendaciones de puertos
- 📝 Genera comandos de configuración

### 2. `puerto_fijo_simple.sh`
**Propósito**: Configuración rápida para fijar el dispositivo en un puerto específico.

```bash
sudo ./puerto_fijo_simple.sh [puerto_usb]
```

**Ejemplos**:
```bash
sudo ./puerto_fijo_simple.sh          # Puerto por defecto (2-1)
sudo ./puerto_fijo_simple.sh 1-2      # Puerto específico 1-2
sudo ./puerto_fijo_simple.sh 2-1      # Puerto específico 2-1
```

**Funcionalidades**:
- ✅ Crea reglas udev optimizadas
- 🔧 Configura script de reubicación automática
- ⚡ Desactiva autosuspend USB
- 📝 Crea comando `secugen-port` para gestión

### 3. `fix_puerto_permanente.sh`
**Propósito**: Configuración avanzada completa con monitoreo automático.

```bash
sudo ./fix_puerto_permanente.sh [puerto_usb]
```

**Funcionalidades**:
- ✅ Configuración completa de reglas udev
- 🔧 Scripts de gestión de puertos
- ⚙️ Parámetros del kernel optimizados
- 🔍 Servicio de monitoreo automático
- 📊 Herramientas de diagnóstico

## 🛠️ Comandos de Gestión

### Comando Principal: `secugen-port`
Después de ejecutar cualquiera de los scripts, tendrás acceso a:

```bash
secugen-port status     # Ver estado del dispositivo
secugen-port relocate   # Reubicar al puerto preferido
secugen-port fix        # Aplicar configuración completa
```

### Ejemplo de Uso Completo

```bash
# 1. Identificar puertos disponibles
./identificar_puertos_usb.sh

# 2. Configurar puerto específico (ejemplo: 1-2)
sudo ./puerto_fijo_simple.sh 1-2

# 3. Verificar configuración
secugen-port status

# 4. Si necesitas reubicar el dispositivo
secugen-port relocate
```

## 📍 Recomendaciones de Puertos

### Puertos Recomendados
- **1-1 o 1-2**: Puertos USB 2.0 del hub raíz (mayor estabilidad)
- **2-1 o 2-2**: Puertos USB 3.0 del hub raíz (mayor velocidad)

### Puertos a Evitar
- **1-2.3.4**: Puertos con múltiples niveles (menos estables)
- **Hubs externos**: Pueden causar problemas de energía
- **Puertos frontales**: Generalmente menos estables

### Consideraciones Físicas
- ✅ **Prefiera puertos traseros**: Conexión directa a motherboard
- ✅ **Evite hubs USB**: Para dispositivos biométricos
- ✅ **Conexión directa**: Sin extensiones ni adaptadores

## 📝 Archivos de Configuración Creados

### 1. Reglas udev
```
/etc/udev/rules.d/99-secugen-puerto-fijo.rules
```

### 2. Scripts de gestión
```
/usr/local/bin/secugen_relocate.sh
/usr/local/bin/secugen-port
/usr/local/bin/secugen_port_manager.sh    # (solo versión avanzada)
/usr/local/bin/secugen_bind_port.sh       # (solo versión avanzada)
```

### 3. Servicios systemd (versión avanzada)
```
/etc/systemd/system/secugen-port-monitor.service
```

## 🔧 Solución de Problemas

### Problema: El dispositivo sigue cambiando de puerto
**Solución**:
```bash
# Verificar estado
secugen-port status

# Recargar reglas udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Forzar reubicación
secugen-port relocate
```

### Problema: Dispositivo no detectado
**Solución**:
```bash
# Verificar conexión USB
lsusb | grep 1162:2201

# Verificar permisos
ls -l /dev/bus/usb/*/*

# Reiniciar servicio udev
sudo systemctl restart udev
```

### Problema: Permisos insuficientes
**Solución**:
```bash
# Verificar grupos del usuario
groups $USER

# Añadir usuario al grupo plugdev
sudo usermod -a -G plugdev $USER

# Recargar sesión
newgrp plugdev
```

## 📊 Verificación de Configuración

### Verificar que el dispositivo está en el puerto correcto:
```bash
# Comando rápido
secugen-port status

# Verificación manual
lsusb | grep 1162:2201
ls -l /dev/secugen_device
```

### Verificar reglas udev:
```bash
# Verificar reglas instaladas
cat /etc/udev/rules.d/99-secugen-puerto-fijo.rules

# Verificar aplicación de reglas
udevadm test $(udevadm info -q path -n /dev/secugen_device)
```

## 🔄 Cambiar Puerto Configurado

### Cambiar a un puerto diferente:
```bash
# Identificar puertos disponibles
./identificar_puertos_usb.sh

# Reconfigurar a nuevo puerto
sudo ./puerto_fijo_simple.sh [nuevo_puerto]

# Ejemplo: cambiar al puerto 1-1
sudo ./puerto_fijo_simple.sh 1-1
```

### Cambiar puerto en configuración avanzada:
```bash
# Usar herramienta de control
secugen_port_control.sh set-port 1-1

# Verificar cambio
secugen-port status
```

## 🚀 Inicio Automático

### Configurar inicio automático del monitoreo (versión avanzada):
```bash
# Habilitar servicio
sudo systemctl enable secugen-port-monitor.service

# Iniciar servicio
sudo systemctl start secugen-port-monitor.service

# Verificar estado
sudo systemctl status secugen-port-monitor.service
```

## ⚡ Optimizaciones Aplicadas

### Configuración USB
- ✅ Autosuspend deshabilitado para SecuGen
- ✅ Control de energía en modo "on"
- ✅ Permisos 0666 para acceso directo
- ✅ Grupo plugdev para acceso sin root

### Reglas udev
- ✅ Symlink persistente `/dev/secugen_device`
- ✅ TAG+="uaccess" para acceso de usuario
- ✅ Configuración de energía automática
- ✅ Gestión de reubicación automática

## 🎯 Casos de Uso

### Desarrollo
```bash
# Configuración rápida para desarrollo
sudo ./puerto_fijo_simple.sh 2-1
```

### Producción
```bash
# Configuración completa con monitoreo
sudo ./fix_puerto_permanente.sh 1-2
```

### Testing
```bash
# Verificar configuración
./identificar_puertos_usb.sh
secugen-port status
```

## 📞 Soporte

### Logs del sistema
```bash
# Ver logs de udev
sudo journalctl -u systemd-udevd

# Ver logs del monitor (versión avanzada)
tail -f /var/log/secugen_port_monitor.log

# Ver logs del gestor de puertos
tail -f /var/log/secugen_port_manager.log
```

### Información de diagnóstico
```bash
# Información completa del sistema
./identificar_puertos_usb.sh

# Estado del dispositivo
secugen-port status

# Verificar aplicación Flask
curl -X POST http://localhost:5000/initialize
```

## ✅ Verificación Final

Para verificar que todo funciona correctamente:

1. **Ejecutar identificación**:
   ```bash
   ./identificar_puertos_usb.sh
   ```

2. **Configurar puerto específico**:
   ```bash
   sudo ./puerto_fijo_simple.sh [puerto_deseado]
   ```

3. **Verificar configuración**:
   ```bash
   secugen-port status
   ```

4. **Probar reconexión**:
   - Desconectar y reconectar el dispositivo
   - Verificar que se mantiene en el mismo puerto
   - Comprobar que la aplicación Flask funciona

5. **Verificar aplicación**:
   ```bash
   curl -X POST http://localhost:5000/initialize
   ```

---

**¿Necesitas ayuda adicional?**
- Ejecuta `./identificar_puertos_usb.sh` para análisis detallado
- Usa `secugen-port status` para verificar estado actual
- Consulta los logs del sistema para diagnóstico avanzado 