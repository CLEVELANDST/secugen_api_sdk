# 🐳 DOCUMENTACIÓN DOCKER - SecuGen Fingerprint API

## 📋 **RESUMEN**

Esta documentación explica cómo usar la versión dockerizada del sistema SecuGen que incluye:
- ✅ **Sistema robusto integrado** que previene y soluciona problemas automáticamente
- ✅ **Migración ultra fácil** entre diferentes PCs con 3 comandos
- ✅ **Entorno consistente** independiente de la distribución Linux
- ✅ **Monitoreo automático** con logs centralizados
- ✅ **Recuperación automática** ante fallos del dispositivo USB

## 🎯 **MIGRACIÓN ULTRA FÁCIL CON DOCKER**

### **Para migrar a otro PC:**

```bash
# 1. Clonar proyecto
git clone <tu-repositorio>
cd driver-bloqueo-digital-huella-main

# 2. Configurar host (automático)
./docker-setup-host.sh

# 3. Iniciar sistema
docker-compose up -d

# ¡Listo! API funcionando en http://localhost:5000
```

## 🚀 **INICIO RÁPIDO**

### **Requisitos Previos**
- Linux (cualquier distribución)
- Dispositivo SecuGen conectado
- Permisos sudo

### **Instalación Automática**

```bash
# Paso 1: Configurar host automáticamente
./docker-setup-host.sh

# Paso 2: Iniciar contenedores
docker-compose up -d

# Paso 3: Verificar funcionamiento
curl -X POST http://localhost:5000/initialize
```

### **Verificación**
```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Probar API
curl -X POST http://localhost:5000/initialize
curl -X POST http://localhost:5000/led -d '{"state": true}' -H "Content-Type: application/json"
```

## 📁 **ESTRUCTURA DOCKER**

### **Contenedores Incluidos**

1. **`secugen-api`** - API principal con sistema robusto
2. **`secugen-monitor`** - Monitoreo automático continuo
3. **`secugen-logs`** - Visualización de logs centralizados

### **Volúmenes Persistentes**

```bash
driver-bloqueo-digital-huella-main/
├── logs/           # Logs persistentes
├── templates/      # Templates de huellas guardados
├── backups/        # Backups automáticos
└── docker-compose.yml
```

## 🔧 **ADMINISTRACIÓN DOCKER**

### **Comandos Básicos**

```bash
# Iniciar sistema
docker-compose up -d

# Parar sistema
docker-compose down

# Reiniciar sistema
docker-compose restart

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f secugen-api
```

### **Comandos Avanzados**

```bash
# Reconstruir imágenes
docker-compose build --no-cache

# Acceder al contenedor
docker exec -it secugen-fingerprint-api bash

# Ver recursos utilizados
docker stats

# Limpiar sistema
docker system prune -a
```

## 🛠️ **CONFIGURACIÓN AVANZADA**

### **Variables de Entorno**

Edita `docker-compose.yml` para personalizar:

```yaml
environment:
  - FLASK_ENV=production
  - FLASK_APP=app.py
  - PYTHONUNBUFFERED=1
  - TZ=America/Mexico_City  # Cambia tu zona horaria
```

### **Configuración de Recursos**

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'      # Límite de CPU
      memory: 512M     # Límite de memoria
    reservations:
      cpus: '0.5'      # CPU reservada
      memory: 256M     # Memoria reservada
```

### **Configuración de Logs**

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    # Tamaño máximo por archivo
    max-file: "3"      # Número de archivos a mantener
```

## 🔍 **MONITOREO Y LOGS**

### **Logs Disponibles**

```bash
# Logs del contenedor principal
docker-compose logs -f secugen-api

# Logs del monitor
docker-compose logs -f secugen-monitor

# Logs del sistema robusto
tail -f logs/sistema_robusto.log

# Logs de Docker entrypoint
tail -f logs/docker_entrypoint.log

# Logs de la aplicación
tail -f logs/app.log
```

### **Monitoreo en Tiempo Real**

```bash
# Ver todos los logs
docker-compose logs -f

# Filtrar logs por servicio
docker-compose logs -f secugen-api | grep ERROR

# Ver estadísticas de contenedores
docker stats

# Ver procesos en contenedores
docker exec -it secugen-fingerprint-api ps aux
```

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Problema: Dispositivo USB no detectado**

```bash
# Verificar dispositivo en host
lsusb | grep "1162:2201"

# Verificar en contenedor
docker exec -it secugen-fingerprint-api lsusb | grep "1162:2201"

# Recargar reglas udev
sudo udevadm control --reload-rules
sudo udevadm trigger
docker-compose restart
```

### **Problema: Error 2 del SDK**

```bash
# Reset automático (incluido en el sistema)
docker-compose restart

# Reset manual
docker exec -it secugen-fingerprint-api python3 reset_usb_device.py

# Verificar logs
docker-compose logs -f secugen-api | grep "Error 2"
```

### **Problema: Puerto ocupado**

```bash
# Verificar puertos
sudo netstat -tuln | grep 5000

# Parar y reiniciar
docker-compose down
docker-compose up -d
```

### **Problema: Contenedor no inicia**

```bash
# Ver logs detallados
docker-compose logs secugen-api

# Verificar configuración
docker-compose config

# Reconstruir imagen
docker-compose build --no-cache
docker-compose up -d
```

## 🔧 **MANTENIMIENTO**

### **Actualizaciones**

```bash
# Actualizar código
git pull origin main

# Reconstruir contenedores
docker-compose build

# Reiniciar con nueva imagen
docker-compose down
docker-compose up -d
```

### **Backups**

```bash
# Backup manual
docker exec -it secugen-fingerprint-api tar -czf /app/backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz /app/templates

# Backup automático (ya incluido)
# Los backups se crean automáticamente en ./backups/
```

### **Limpieza**

```bash
# Limpiar contenedores parados
docker container prune

# Limpiar imágenes no utilizadas
docker image prune -a

# Limpiar todo el sistema
docker system prune -a --volumes
```

## 📊 **RENDIMIENTO**

### **Optimización**

```yaml
# En docker-compose.yml
version: '3.8'
services:
  secugen-api:
    # Limitar recursos
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    
    # Configurar logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### **Monitoring**

```bash
# Ver uso de recursos
docker stats

# Ver logs de rendimiento
docker-compose logs -f secugen-monitor

# Verificar salud de contenedores
docker-compose ps
```

## 🔐 **SEGURIDAD**

### **Mejores Prácticas**

1. **Usuario no-root**: Los contenedores corren como usuario `secugen`
2. **Permisos mínimos**: Solo los permisos USB necesarios
3. **Logs seguros**: Logs rotan automáticamente
4. **Red aislada**: Contenedores en red privada

### **Configuración de Seguridad**

```yaml
# En docker-compose.yml
services:
  secugen-api:
    user: secugen:secugen
    read_only: true
    security_opt:
      - no-new-privileges:true
    tmpfs:
      - /tmp:rw,size=100M
```

## 🎯 **VENTAJAS DE LA VERSIÓN DOCKER**

### **Vs. Instalación Nativa**

| Característica | Docker | Nativo |
|----------------|---------|---------|
| **Migración** | 3 comandos | 10+ pasos |
| **Dependencias** | Automáticas | Manuales |
| **Consistencia** | Garantizada | Variable |
| **Rollback** | Inmediato | Complejo |
| **Aislamiento** | Completo | Parcial |
| **Monitoreo** | Integrado | Manual |

### **Beneficios Específicos**

- ✅ **Migración en 3 comandos** vs. configuración manual
- ✅ **Funciona en cualquier Linux** vs. solo Ubuntu/Debian
- ✅ **Entorno consistente** vs. dependencias variables
- ✅ **Rollback inmediato** vs. reinstalación completa
- ✅ **Logs centralizados** vs. logs dispersos
- ✅ **Monitoreo automático** vs. monitoreo manual

## 📞 **SOPORTE**

### **Diagnóstico Rápido**

```bash
# Verificar estado completo
docker-compose ps
docker-compose logs -f

# Verificar dispositivo
docker exec -it secugen-fingerprint-api lsusb | grep "1162:2201"

# Probar API
curl -X POST http://localhost:5000/initialize
```

### **Comandos de Emergencia**

```bash
# Reset completo
docker-compose down
docker system prune -f
docker-compose up -d

# Restaurar desde backup
docker exec -it secugen-fingerprint-api ls /app/backups/
# Restaurar backup específico si es necesario
```

## 🎉 **CONCLUSIÓN**

La versión Docker del sistema SecuGen ofrece:

1. **Migración ultra fácil** con solo 3 comandos
2. **Sistema robusto integrado** que previene problemas
3. **Monitoreo automático** con logs centralizados
4. **Recuperación automática** ante fallos
5. **Entorno consistente** en cualquier Linux

**¡Perfecto para migrar entre PCs sin complicaciones!**

---

**Para más información consulta:**
- [README.md](./README.md) - Documentación principal
- [README_SISTEMA_ROBUSTO.md](./README_SISTEMA_ROBUSTO.md) - Sistema robusto
- [COMANDOS_MIGRACION_PC.md](./COMANDOS_MIGRACION_PC.md) - Comandos de migración 