#!/usr/bin/env python3
"""
VentaPro - Sistema de Gestión de Ventas e Inventario
====================================================

Sistema de punto de venta (POS) y gestión de inventario diseñado 
específicamente para pequeñas y medianas empresas.

Autor: Sistema VentaPro
Versión: 1.0.0
Fecha: 2025-10-04
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

# Imports del proyecto
from database.db_manager import DatabaseManager
from ui.main_window import MainWindow
from utils.logger import Logger
from utils.config_manager import ConfigManager

def main():
    """Función principal de la aplicación VentaPro"""
    try:
        # Inicializar logger
        logger = Logger()
        logger.info("🚀 Iniciando VentaPro - Sistema de Gestión de Ventas")
        
        # Cargar configuración
        config = ConfigManager()
        
        # Inicializar base de datos
        db_manager = DatabaseManager()
        if not db_manager.inicializar_db():
            logger.error("❌ Error al inicializar la base de datos")
            return False
        
        # Crear y mostrar ventana principal
        app = MainWindow()
        logger.info("✅ VentaPro iniciado correctamente")
        
        # Ejecutar aplicación
        app.ejecutar()
        
    except Exception as e:
        print(f"❌ Error crítico al iniciar VentaPro: {str(e)}")
        Logger().error(f"Error crítico: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Configurar encoding para Windows
    if sys.platform.startswith('win'):
        import locale
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    
    # Ejecutar aplicación
    success = main()
    sys.exit(0 if success else 1)