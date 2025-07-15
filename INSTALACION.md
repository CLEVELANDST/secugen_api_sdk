# 🚀 Guía de Instalación - Sistema SecuGen en Otro Equipo

## 📋 Prerrequisitos del Sistema

### Sistema Operativo
- **Linux Ubuntu 20.04+** (recomendado)
- **Debian 10+** 
- **CentOS 8+**

### Software Requerido
```bash
# Instalar Docker y Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose git curl

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker
```

### Hardware Requerido
- **Lector de huellas SecuGen** (USB UPx o compatible)
- **Puerto USB disponible**
- **Mínimo 2GB RAM**
- **1GB espacio en disco**

## 📦 Pasos de Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/CLEVELANDST/secugen_api_sdk.git
cd secugen_api_sdk
```

### 2. Instalar SDK en el Sistema Host
```bash
# Hacer el script ejecutable
chmod +x install-sdk.sh

# Ejecutar instalación (requiere sudo)
sudo ./install-sdk.sh
```

**El script install-sdk.sh hará:**
- ✅ Copiar librerías SecuGen a `/usr/lib/`
- ✅ Actualizar cache de librerías (`ldconfig`)
- ✅ Crear reglas udev para el dispositivo
- ✅ Configurar permisos de usuario
- ✅ Crear grupo `plugdev`

### 3. Conectar el Dispositivo SecuGen
```bash
# Conectar el lector de huellas USB
# Verificar que se detecta:
lsusb | grep -i secugen

# Debería mostrar algo como:
# Bus 002 Device 002: ID 1162:2201 Secugen Corp. SecuGen USB UPx

# Verificar symlink persistente:
ls -la /dev/secugen*
```

### 4. Configurar Usuario
```bash
# Reiniciar sesión o ejecutar:
newgrp plugdev

# Verificar permisos:
groups $USER
# Debería incluir: plugdev
```

### 5. Ejecutar el Sistema
```bash
# Levantar los contenedores
docker-compose up --build

# O en segundo plano:
docker-compose up --build -d
```

## 🔍 Verificación de la Instalación

### Verificar Servicios
```bash
# Ver contenedores en ejecución
docker-compose ps

# Debería mostrar:
# secugen-fingerprint-api   Up      0.0.0.0:5500->5000/tcp
# secugen-monitor          Up      
# secugen-logs             Up      
```

### Probar la API
```bash
# Probar endpoint básico
curl -X GET http://localhost:5500/templates

# Debería devolver:
# {"count":0,"success":true,"templates":[]}

# Probar inicialización del dispositivo
curl -X POST http://localhost:5500/initialize

# Si funciona:
# {"message":"Dispositivo ya está inicializado correctamente","success":true}
```

### Verificar Logs
```bash
# Ver logs en tiempo real
docker-compose logs -f secugen-api

# Buscar el mensaje de éxito:
# ✅ Dispositivo abierto exitosamente con ID: 0
# 🎉 Dispositivo inicializado correctamente y ESTABLE
```

## 🛠️ Solución de Problemas

### Problema: "libsgfdu06.so: cannot open shared object file"
```bash
# Verificar que el SDK está instalado
ls -la /usr/lib/libsgfdu06.so
ldd /usr/lib/libsgfdu06.so

# Si no existe, reinstalar:
sudo ./install-sdk.sh
```

### Problema: "No se pudo abrir el dispositivo con ningún ID"
```bash
# Verificar dispositivo USB
lsusb | grep -i secugen

# Verificar reglas udev
ls -la /dev/secugen*

# Verificar permisos
ls -la /dev/bus/usb/002/002  # Ajustar números según lsusb

# Reconectar dispositivo
sudo udevadm trigger
```

### Problema: Puerto 5500 en uso
```bash
# Ver qué usa el puerto
lsof -i :5500

# Detener el proceso
sudo kill <PID>

# O cambiar puerto en docker-compose.yml
```

### Problema: Permisos de usuario
```bash
# Agregar usuario al grupo plugdev
sudo usermod -aG plugdev $USER

# Reiniciar sesión
logout
# O ejecutar:
newgrp plugdev
```

## 📊 Endpoints Disponibles

Una vez instalado, estos endpoints estarán disponibles:

| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `/templates` | GET | Listar templates |
| `/initialize` | POST | Inicializar dispositivo |
| `/led` | POST | Control de LED |
| `/capturar-huella` | POST | Capturar huella |
| `/comparar-huellas` | POST | Comparar huellas |
| `/templates/<id>` | DELETE | Eliminar template |

## 📁 Estructura del Proyecto

```
secugen_api_sdk/
├── app.py              # Aplicación Flask principal
├── docker-compose.yml  # Configuración Docker
├── Dockerfile         # Imagen Docker
├── install-sdk.sh     # Script de instalación SDK
├── uninstall-sdk.sh   # Script de desinstalación
├── lib/linux3/        # Librerías SecuGen
├── sdk/               # SDK nativo
├── logs/              # Logs del sistema
└── templates/         # Templates de huellas
```

## 🚀 Despliegue en Producción

### Usando systemd (recomendado)
```bash
# Crear servicio systemd
sudo tee /etc/systemd/system/secugen-api.service > /dev/null <<EOF
[Unit]
Description=SecuGen API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/ruta/al/proyecto
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Habilitar servicio
sudo systemctl enable secugen-api
sudo systemctl start secugen-api
```

### Configurar Firewall
```bash
# Permitir puerto 5500
sudo ufw allow 5500/tcp
```

## 🔧 Mantenimiento

### Actualizar Sistema
```bash
# Detener servicios
docker-compose down

# Actualizar código
git pull origin main

# Reconstruir contenedores
docker-compose up --build -d
```

### Backup de Templates
```bash
# Las huellas se almacenan en:
ls -la templates/

# Hacer backup
tar -czf backup_templates_$(date +%Y%m%d).tar.gz templates/
```

### Desinstalar Completamente
```bash
# Detener contenedores
docker-compose down

# Eliminar SDK del sistema
sudo ./uninstall-sdk.sh

# Eliminar proyecto
cd .. && rm -rf secugen_api_sdk
```

## 📞 Soporte

Para problemas o dudas:
1. Verificar esta guía de instalación
2. Revisar logs: `docker-compose logs -f`
3. Verificar estado del dispositivo: `lsusb | grep -i secugen`
4. Comprobar permisos: `groups $USER`

---

## ⚠️ Notas Importantes

- **Requiere permisos de administrador** para instalar el SDK
- **El dispositivo debe estar conectado** antes de ejecutar
- **Reiniciar sesión** después de agregar usuario al grupo plugdev
- **Verificar firewall** si se accede remotamente
- **Hacer backup** de templates regularmente 