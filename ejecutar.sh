#!/bin/bash
# NegocioSmart - Ejecutor para Linux/Mac
# ============================================

echo "🚀 Iniciando NegocioSmart..."

# Verificar si existe el entorno virtual
if [ ! -d ".venv" ]; then
    echo "❌ Entorno virtual no encontrado."
    echo "💡 Ejecuta primero: ./instalar.sh"
    exit 1
fi

# Activar entorno virtual
source .venv/bin/activate

# Verificar dependencias
echo "🔍 Verificando dependencias..."
python verificar_entorno.py

# Ejecutar aplicación
echo "🎯 Ejecutando NegocioSmart..."
python main.py