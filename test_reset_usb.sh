#!/bin/bash

echo "🧪 PRUEBA DE RESET USB - API SECUGEN"
echo "====================================="

# URL base de la API
API_URL="http://localhost:5500"

# Función para hacer requests
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -n "$data" ]; then
        curl -s -X $method "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X $method "$API_URL$endpoint"
    fi
}

# Función para mostrar resultado
show_result() {
    local title=$1
    local response=$2
    
    echo ""
    echo "📋 $title"
    echo "----------------------------------------"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo "----------------------------------------"
}

echo "1. Verificando que la API esté funcionando..."
response=$(make_request "POST" "/initialize")
show_result "Inicialización" "$response"

echo ""
echo "2. Probando control de LED..."
response=$(make_request "POST" "/led" '{"state": true}')
show_result "Encender LED" "$response"

sleep 2

response=$(make_request "POST" "/led" '{"state": false}')
show_result "Apagar LED" "$response"

echo ""
echo "3. Probando reset USB..."
echo "⚠️  Esta operación puede interrumpir temporalmente el dispositivo"
read -p "¿Continuar con el reset USB? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    response=$(make_request "POST" "/reset-usb")
    show_result "Reset USB" "$response"
    
    echo ""
    echo "4. Verificando que el dispositivo siga funcionando..."
    sleep 3
    response=$(make_request "POST" "/initialize")
    show_result "Re-inicialización después del reset" "$response"
else
    echo "❌ Reset USB cancelado"
fi

echo ""
echo "✅ Prueba completada"
echo ""
echo "💡 Para usar el reset USB desde curl:"
echo "curl -X POST http://localhost:5500/reset-usb" 