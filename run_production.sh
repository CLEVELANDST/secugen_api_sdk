#!/bin/bash

# Script optimizado para levantar el proyecto SecuGen

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Sistema de Huellas Digitales SecuGen${NC}"
echo "================================================"

# Verificar dispositivo
echo -e "${BLUE}📱 Verificando dispositivo SecuGen...${NC}"
if lsusb | grep -q "1162:2201"; then
    echo -e "${GREEN}✅ Dispositivo SecuGen detectado${NC}"
else
    echo -e "${RED}❌ Dispositivo SecuGen no detectado${NC}"
    exit 1
fi

# Configurar entorno
echo -e "${BLUE}⚙️ Configurando entorno...${NC}"
export LD_LIBRARY_PATH=$PWD/lib/linux3:$LD_LIBRARY_PATH

# Verificar y crear directorio de logs
mkdir -p logs

# Activar entorno virtual y ejecutar
echo -e "${BLUE}🔧 Activando entorno virtual...${NC}"
source venv/bin/activate

echo -e "${BLUE}🌐 Iniciando servidor Flask...${NC}"
echo -e "${YELLOW}Servidor disponible en: http://localhost:5000${NC}"
echo -e "${YELLOW}Presiona Ctrl+C para detener${NC}"
echo "================================================"

# Ejecutar aplicación
python3 app.py 