"""
Gestor de Configuración - VentaPro
=================================

Maneja la configuración del sistema desde archivos INI y base de datos.
Proporciona acceso centralizado a todas las configuraciones.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

import configparser
import os
from typing import Any, Optional
from pathlib import Path

class ConfigManager:
    """Gestor centralizado de configuración"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._cargar_configuracion()
    
    def _cargar_configuracion(self):
        """Carga la configuración desde el archivo INI"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
            else:
                self._crear_configuracion_default()
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            self._crear_configuracion_default()
    
    def _crear_configuracion_default(self):
        """Crea un archivo de configuración con valores por defecto"""
        # Si ya existe el archivo, no lo sobrescribimos
        if os.path.exists(self.config_file):
            return
        
        # Configuración por defecto
        default_config = {
            'DATABASE': {
                'db_path': 'data/erp.db',
                'backup_enabled': 'true',
                'backup_interval': '24',
                'max_backups': '30'
            },
            'APPLICATION': {
                'app_name': 'VentaPro',
                'app_version': '1.0.0',
                'window_title': 'VentaPro - Sistema de Gestión de Ventas',
                'theme': 'modern',
                'language': 'es',
                'debug_mode': 'false'
            },
            'BUSINESS': {
                'business_name': 'Mi Negocio',
                'business_address': 'Calle Principal 123, Ciudad',
                'business_phone': '+52 xxx-xxx-xxxx',
                'business_email': 'contacto@minegocio.com',
                'currency': 'MXN',
                'currency_symbol': '$'
            },
            'LOGGING': {
                'log_level': 'INFO',
                'log_file': 'logs/app.log',
                'max_log_size': '10MB',
                'log_rotation': '7'
            }
        }
        
        # Crear configuración
        for seccion, valores in default_config.items():
            self.config.add_section(seccion)
            for clave, valor in valores.items():
                self.config.set(seccion, clave, valor)
        
        # Guardar archivo
        self._guardar_configuracion()
    
    def _guardar_configuracion(self):
        """Guarda la configuración al archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
    
    def get(self, seccion: str, clave: str, default: Any = None) -> str:
        """Obtiene un valor de configuración"""
        try:
            return self.config.get(seccion, clave)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return str(default) if default is not None else ""
    
    def getint(self, seccion: str, clave: str, default: int = 0) -> int:
        """Obtiene un valor entero de configuración"""
        try:
            return self.config.getint(seccion, clave)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def getfloat(self, seccion: str, clave: str, default: float = 0.0) -> float:
        """Obtiene un valor flotante de configuración"""
        try:
            return self.config.getfloat(seccion, clave)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def getboolean(self, seccion: str, clave: str, default: bool = False) -> bool:
        """Obtiene un valor booleano de configuración"""
        try:
            return self.config.getboolean(seccion, clave)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def set(self, seccion: str, clave: str, valor: Any):
        """Establece un valor de configuración"""
        try:
            if not self.config.has_section(seccion):
                self.config.add_section(seccion)
            
            self.config.set(seccion, clave, str(valor))
            self._guardar_configuracion()
            
        except Exception as e:
            print(f"Error al establecer configuración: {e}")
    
    def get_database_path(self) -> str:
        """Obtiene la ruta de la base de datos"""
        return self.get('DATABASE', 'db_path', 'data/erp.db')
    
    def get_app_name(self) -> str:
        """Obtiene el nombre de la aplicación"""
        return self.get('APPLICATION', 'app_name', 'VentaPro')
    
    def get_app_version(self) -> str:
        """Obtiene la versión de la aplicación"""
        return self.get('APPLICATION', 'app_version', '1.0.0')
    
    def get_window_title(self) -> str:
        """Obtiene el título de la ventana"""
        return self.get('APPLICATION', 'window_title', 'VentaPro')
    
    def is_debug_mode(self) -> bool:
        """Verifica si está en modo debug"""
        return self.getboolean('APPLICATION', 'debug_mode', False)
    
    def get_business_name(self) -> str:
        """Obtiene el nombre del negocio"""
        return self.get('BUSINESS', 'business_name', 'Mi Negocio')
    
    def get_currency_symbol(self) -> str:
        """Obtiene el símbolo de moneda"""
        return self.get('BUSINESS', 'currency_symbol', '$')
    
    def get_log_level(self) -> str:
        """Obtiene el nivel de logging"""
        return self.get('LOGGING', 'log_level', 'INFO')
    
    def get_log_file(self) -> str:
        """Obtiene la ruta del archivo de log"""
        return self.get('LOGGING', 'log_file', 'logs/app.log')
    
    def backup_enabled(self) -> bool:
        """Verifica si los backups están habilitados"""
        return self.getboolean('DATABASE', 'backup_enabled', True)
    
    def get_backup_interval(self) -> int:
        """Obtiene el intervalo de backup en horas"""
        return self.getint('DATABASE', 'backup_interval', 24)
    
    def get_max_backups(self) -> int:
        """Obtiene el número máximo de backups a mantener"""
        return self.getint('DATABASE', 'max_backups', 30)
    
    def get_window_size(self) -> tuple:
        """Obtiene el tamaño de ventana por defecto"""
        width = self.getint('UI', 'window_width', 1200)
        height = self.getint('UI', 'window_height', 800)
        return (width, height)
    
    def has_section(self, seccion: str) -> bool:
        """Verifica si existe una sección"""
        return self.config.has_section(seccion)
    
    def has_option(self, seccion: str, clave: str) -> bool:
        """Verifica si existe una opción"""
        return self.config.has_option(seccion, clave)
    
    def get_all_sections(self) -> list:
        """Obtiene todas las secciones"""
        return self.config.sections()
    
    def get_all_options(self, seccion: str) -> list:
        """Obtiene todas las opciones de una sección"""
        try:
            return self.config.options(seccion)
        except configparser.NoSectionError:
            return []
    
    def reload(self):
        """Recarga la configuración desde el archivo"""
        self._cargar_configuracion()

# Instancia global del gestor de configuración
config_manager_instance = None

def get_config_manager() -> ConfigManager:
    """Obtiene la instancia global del gestor de configuración"""
    global config_manager_instance
    if config_manager_instance is None:
        config_manager_instance = ConfigManager()
    return config_manager_instance