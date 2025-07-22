# SecuGen Manager - Script Maestro Unificado

Este script unifica todas las funcionalidades necesarias para gestionar el sistema de huellas digitales SecuGen.

## 🚀 Inicio Rápido

### 1. Configuración Inicial (Una sola vez)
```bash
# Configurar todo el sistema automáticamente
sudo ./secugen_manager.sh setup
```

### 2. Uso Diario
```bash
# Iniciar la aplicación
./secugen_manager.sh start

# Ver estado del sistema
./secugen_manager.sh status

# Parar la aplicación
./secugen_manager.sh stop
```

## 📋 Comandos Disponibles

### Configuración Inicial
- `sudo ./secugen_manager.sh install` - Instalar dependencias del sistema
- `sudo ./secugen_manager.sh setup` - Configuración completa (recomendado)
- `./secugen_manager.sh check` - Verificar requisitos del sistema

### Gestión de la Aplicación
- `./secugen_manager.sh start` - Iniciar aplicación
- `./secugen_manager.sh stop` - Parar aplicación  
- `./secugen_manager.sh restart` - Reiniciar aplicación
- `./secugen_manager.sh status` - Ver estado completo

### Utilidades
- `./secugen_manager.sh backup` - Crear backup
- `./secugen_manager.sh test` - Probar API básica
- `./secugen_manager.sh logs` - Ver logs en tiempo real
- `./secugen_manager.sh help` - Mostrar ayuda completa

## 🔧 Funcionalidades Incluidas

Este script unifica las funcionalidades de los siguientes scripts eliminados:

- ✅ **check_device.sh** - Verificación de dispositivo USB
- ✅ **start.sh** - Inicio de la aplicación
- ✅ **setup-host.sh** - Configuración del host
- ✅ **setup_production.sh** - Configuración completa de producción
- ✅ **install_host_dependencies.sh** - Instalación de dependencias
- ✅ **pre_production_check.sh** - Verificaciones pre-producción
- ✅ **show_commands.sh** - Mostrar comandos disponibles

## 📁 Estructura Resultante

```
secugen_api_sdk/
├── secugen_manager.sh          # 🎯 SCRIPT MAESTRO UNIFICADO
├── app.py                      # Aplicación principal
├── config/                     # Configuraciones
├── logs/                       # Logs de la aplicación
├── backups/                    # Respaldos automáticos
└── java/                       # Scripts de Java (mantenidos)
    ├── build_samples.sh
    ├── extract_samples.sh
    ├── run_jsgd.sh
    └── run_jsgfplibtest.sh
```

## 🎯 Ventajas del Script Unificado

1. **Un solo comando**: Todo lo necesario en un script
2. **Configuración automática**: Setup completo con un comando
3. **Gestión simplificada**: Start, stop, restart, status
4. **Diagnósticos integrados**: Verificaciones y logs
5. **Backups automáticos**: Respaldos fáciles
6. **Colores y logging**: Output claro y organizado

## 📊 Ejemplos de Uso

### Configuración inicial completa
```bash
sudo ./secugen_manager.sh setup
```

### Flujo de trabajo típico
```bash
# 1. Verificar sistema
./secugen_manager.sh check

# 2. Iniciar aplicación  
./secugen_manager.sh start

# 3. Verificar que todo funcione
./secugen_manager.sh status

# 4. Probar API
./secugen_manager.sh test
```

### Mantenimiento
```bash
# Crear backup antes de actualizaciones
./secugen_manager.sh backup

# Reiniciar si hay problemas
./secugen_manager.sh restart

# Ver logs para diagnóstico
./secugen_manager.sh logs
```

## 🚨 Notas Importantes

- Los comandos `install` y `setup` requieren **sudo**
- El script debe ejecutarse desde el directorio del proyecto
- Los scripts de Java se mantuvieron para ejemplos específicos
- El sistema crea automáticamente directorios de logs y backups
- La configuración USB se aplica automáticamente

## 🆘 Solución de Problemas

1. **Si el dispositivo no se detecta**:
   ```bash
   sudo ./secugen_manager.sh setup
   ```

2. **Si la aplicación no inicia**:
   ```bash
   ./secugen_manager.sh check
   ./secugen_manager.sh logs
   ```

3. **Para ver ayuda completa**:
   ```bash
   ./secugen_manager.sh help
   ```

---

**¡El script maestro simplifica todo el proceso en comandos fáciles de usar!** 🎉 