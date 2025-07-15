# 🔐 SecuGen Fingerprint API

API REST para lector de huellas SecuGen con sistema robusto y containerizado.

## 🚀 Instalación Rápida

### En el equipo actual:
```bash
# 1. Instalar SDK en el sistema host
sudo ./install-sdk.sh

# 2. Conectar dispositivo SecuGen

# 3. Ejecutar con Docker
docker-compose up --build
```

### En otro equipo:
📖 **[Ver guía completa de instalación](INSTALACION.md)**

## 📊 API Endpoints

| Endpoint | Método | Descripción |
|----------|---------|-------------|
| `http://localhost:5500/templates` | GET | Listar templates |
| `http://localhost:5500/initialize` | POST | Inicializar dispositivo |
| `http://localhost:5500/capturar-huella` | POST | Capturar huella |
| `http://localhost:5500/comparar-huellas` | POST | Comparar huellas |

## 🛠️ Características

- ✅ **API REST** con Flask
- ✅ **Docker containerizado** con `restart: always`
- ✅ **SDK nativo SecuGen** instalado en host
- ✅ **Puerto USB** correctamente expuesto
- ✅ **Identificador persistente** con reglas udev
- ✅ **Monitoreo del sistema** integrado
- ✅ **Logs centralizados**

## 🔧 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f secugen-api

# Probar API
curl -X GET http://localhost:5500/templates
curl -X POST http://localhost:5500/initialize

# Detener servicios
docker-compose down

# Desinstalar SDK
sudo ./uninstall-sdk.sh
```

## 📋 Requisitos

- **Linux Ubuntu 20.04+** (recomendado)
- **Docker & Docker Compose**
- **Lector SecuGen USB UPx**
- **Permisos de administrador** (para instalar SDK)

## 🆘 Solución de Problemas

### Problema: SDK no disponible
```bash
sudo ./install-sdk.sh
```

### Problema: Dispositivo no detectado
```bash
lsusb | grep -i secugen
ls -la /dev/secugen*
```

### Problema: Puerto ocupado
```bash
lsof -i :5500
```

## 📁 Estructura del Proyecto

```
├── app.py              # Aplicación Flask principal
├── docker-compose.yml  # Configuración Docker (restart: always)
├── Dockerfile         # Imagen con SDK instalado
├── install-sdk.sh     # Script de instalación SDK
├── uninstall-sdk.sh   # Script de desinstalación
├── lib/linux3/        # Librerías SecuGen
├── INSTALACION.md     # Guía completa de instalación
└── README.md          # Este archivo
```

## ⚠️ Notas Importantes

- **El SDK debe instalarse en el sistema host** (no solo en el contenedor)
- **Reiniciar sesión** después de ejecutar `install-sdk.sh`
- **Conectar el dispositivo** antes de ejecutar Docker
- **Verificar permisos** con `groups $USER` (debe incluir `plugdev`)

---

## 🔗 Enlaces Útiles

- [📖 Guía completa de instalación](INSTALACION.md)
- [🔧 Configuración Docker](docker-compose.yml)
- [📊 Logs del sistema](logs/)

## 📞 Soporte

Para instalación en otro equipo: **[INSTALACION.md](INSTALACION.md)**