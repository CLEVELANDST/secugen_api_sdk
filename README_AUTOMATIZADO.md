# SecuGen API SDK - Configuración Automatizada

Este proyecto proporciona una API REST para interactuar con lectores de huellas digitales SecuGen usando Docker.

## 🚀 Inicio Rápido

### Opción 1: Configuración Automática Completa (RECOMENDADO)

1. **Conecta tu lector de huellas SecuGen**

2. **Ejecuta la configuración automática:**
   ```bash
   chmod +x setup-host.sh
   sudo ./setup-host.sh
   ```

3. **Inicia la aplicación:**
   ```bash
   sudo ./run-secugen-api.sh
   ```

¡Eso es todo! Tu API estará disponible en `http://localhost:5000`

### Opción 2: Configuración Manual

Si prefieres hacerlo paso a paso:

1. **Conecta el dispositivo SecuGen**

2. **Configura el host:**
   ```bash
   sudo ./setup-host.sh
   ```

3. **Inicia manualmente:**
   ```bash
   sudo /usr/local/bin/docker-compose up --build -d
   ```

## 📋 Qué hace la configuración automática

El script `setup-host.sh` automatiza los siguientes pasos:

1. ✅ **Verifica Docker y Docker Compose** - Los instala si no existen
2. ✅ **Configura reglas udev** - Para el acceso automático al dispositivo USB
3. ✅ **Establece permisos del dispositivo** - Permite el acceso al lector de huellas
4. ✅ **Crea script de inicio** - `run-secugen-api.sh` para uso futuro

## 🔧 Comandos Útiles

### Iniciar la aplicación
```bash
sudo ./run-secugen-api.sh
```

### Ver logs en tiempo real
```bash
sudo docker logs -f secugen_api_sdk-api-1
```

### Detener la aplicación
```bash
sudo /usr/local/bin/docker-compose down
```

### Reiniciar solo el servicio API
```bash
sudo /usr/local/bin/docker-compose restart api
```

### Verificar estado de contenedores
```bash
sudo docker ps
```

## 🌐 Uso de la API

### Inicializar el dispositivo
```bash
curl -X POST -H "Content-Type: application/json" http://localhost:5000/initialize
```

### Capturar huella digital
```bash
curl -X POST -H "Content-Type: application/json" http://localhost:5000/capture
```

### Estado del dispositivo
```bash
curl -X GET http://localhost:5000/status
```

## 🔍 Resolución de Problemas

### El dispositivo no se detecta

1. **Verificar conexión USB:**
   ```bash
   lsusb | grep SecuGen
   ```
   Deberías ver algo como: `Bus 003 Device 002: ID 1162:2201 Secugen Corp. SecuGen USB UPx`

2. **Verificar permisos del dispositivo:**
   ```bash
   ls -la /dev/bus/usb/003/002  # Ajusta el path según tu dispositivo
   ```

3. **Reejecutar configuración:**
   ```bash
   sudo ./setup-host.sh
   ```

### Error de permisos de Docker

Si ves errores como "permission denied", asegúrate de ejecutar con `sudo`:

```bash
sudo ./run-secugen-api.sh
```

### Ver logs detallados
```bash
# Logs de la aplicación
sudo docker logs secugen_api_sdk-api-1

# Logs de la base de datos
sudo docker logs secugen_api_sdk-db-1

# Logs en tiempo real
sudo docker logs -f secugen_api_sdk-api-1
```

### Reiniciar completamente
```bash
sudo /usr/local/bin/docker-compose down
sudo docker system prune -f
sudo ./run-secugen-api.sh
```

## ⚡ Características

- **Configuración automática** del host y dispositivo USB
- **Contenedores Docker** para aislamiento y portabilidad
- **API REST** para integración fácil
- **Base de datos PostgreSQL** para almacenamiento
- **Logs detallados** para debugging
- **Scripts reutilizables** para futuras ejecuciones

## 📁 Estructura del Proyecto

```
secugen_api_sdk/
├── setup-host.sh              # Configuración automática del host
├── run-secugen-api.sh          # Script de inicio rápido
├── docker-compose.yml          # Configuración de contenedores
├── Dockerfile                  # Imagen de la aplicación
├── start.sh                    # Script de inicio del contenedor
├── app.py                      # Aplicación Flask principal
├── docker/99SecuGen.rules      # Reglas udev para el dispositivo
└── README_AUTOMATIZADO.md      # Este archivo
```

## 🔒 Consideraciones de Seguridad

- Los scripts requieren permisos `sudo` para configurar dispositivos USB
- El contenedor se ejecuta en modo privilegiado para acceder al hardware USB
- Las reglas udev se instalan globalmente en el sistema

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa que el dispositivo SecuGen esté conectado: `lsusb | grep SecuGen`
2. Ejecuta nuevamente la configuración: `sudo ./setup-host.sh`
3. Consulta los logs: `sudo docker logs secugen_api_sdk-api-1` 