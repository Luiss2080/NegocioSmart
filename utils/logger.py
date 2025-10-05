"""
Sistema de Logging - VentaPro
============================

Maneja todos los logs del sistema con niveles, rotación y formateo.
Registra actividades, errores y eventos importantes.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
import colorama
from colorama import Fore, Back, Style

# Inicializar colorama para Windows
colorama.init(autoreset=True)

class Logger:
    """Sistema de logging avanzado para VentaPro"""
    
    def __init__(self, log_file: str = "logs/app.log", log_level: str = "INFO"):
        self.log_file = log_file
        self.log_level = log_level.upper()
        
        # Crear directorio de logs si no existe
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger('VentaPro')
        self.logger.setLevel(getattr(logging, self.log_level, logging.INFO))
        
        # Evitar duplicación de handlers
        if not self.logger.handlers:
            self._configurar_handlers()
    
    def _configurar_handlers(self):
        """Configura los handlers para archivo y consola"""
        
        # Formatter para logs
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)8s | %(module)15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo con rotación
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, self.log_level, logging.INFO))
        
        # Handler para consola con colores
        console_handler = ColoredConsoleHandler()
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)8s | %(module)15s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Agregar handlers al logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, mensaje: str, modulo: str = ""):
        """Log nivel DEBUG"""
        if modulo:
            self.logger.debug(f"[{modulo}] {mensaje}")
        else:
            self.logger.debug(mensaje)
    
    def info(self, mensaje: str, modulo: str = ""):
        """Log nivel INFO"""
        if modulo:
            self.logger.info(f"[{modulo}] {mensaje}")
        else:
            self.logger.info(mensaje)
    
    def warning(self, mensaje: str, modulo: str = ""):
        """Log nivel WARNING"""
        if modulo:
            self.logger.warning(f"[{modulo}] {mensaje}")
        else:
            self.logger.warning(mensaje)
    
    def error(self, mensaje: str, modulo: str = ""):
        """Log nivel ERROR"""
        if modulo:
            self.logger.error(f"[{modulo}] {mensaje}")
        else:
            self.logger.error(mensaje)
    
    def critical(self, mensaje: str, modulo: str = ""):
        """Log nivel CRITICAL"""
        if modulo:
            self.logger.critical(f"[{modulo}] {mensaje}")
        else:
            self.logger.critical(mensaje)
    
    def log_venta(self, folio: str, total: float, cliente: str = ""):
        """Log específico para ventas"""
        mensaje = f"💰 VENTA {folio} - Total: ${total:.2f}"
        if cliente:
            mensaje += f" - Cliente: {cliente}"
        self.info(mensaje, "VENTAS")
    
    def log_producto(self, accion: str, codigo: str, nombre: str):
        """Log específico para productos"""
        mensaje = f"📦 {accion.upper()} - {codigo} - {nombre}"
        self.info(mensaje, "PRODUCTOS")
    
    def log_usuario(self, usuario: str, accion: str):
        """Log específico para usuarios"""
        mensaje = f"👤 {usuario} - {accion}"
        self.info(mensaje, "USUARIOS")
    
    def log_sistema(self, mensaje: str):
        """Log específico para eventos del sistema"""
        self.info(f"⚙️ {mensaje}", "SISTEMA")

class ColoredConsoleHandler(logging.StreamHandler):
    """Handler personalizado para mostrar logs con colores en consola"""
    
    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            stream.write(message + '\n')
            self.flush()
        except Exception:
            self.handleError(record)

class ColoredFormatter(logging.Formatter):
    """Formatter que agrega colores según el nivel de log"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.YELLOW + Style.BRIGHT
    }
    
    def format(self, record):
        # Obtener el mensaje formateado
        message = super().format(record)
        
        # Agregar color según el nivel
        color = self.COLORS.get(record.levelname, '')
        if color:
            # Colorear solo el nivel
            parts = message.split('|')
            if len(parts) >= 2:
                parts[1] = f"{color}{parts[1]}{Style.RESET_ALL}"
                message = '|'.join(parts)
        
        return message

# Instancia global del logger
logger_instance = None

def get_logger() -> Logger:
    """Obtiene la instancia global del logger"""
    global logger_instance
    if logger_instance is None:
        logger_instance = Logger()
    return logger_instance

# Funciones de conveniencia
def log_debug(mensaje: str, modulo: str = ""):
    """Función de conveniencia para debug"""
    get_logger().debug(mensaje, modulo)

def log_info(mensaje: str, modulo: str = ""):
    """Función de conveniencia para info"""
    get_logger().info(mensaje, modulo)

def log_warning(mensaje: str, modulo: str = ""):
    """Función de conveniencia para warning"""
    get_logger().warning(mensaje, modulo)

def log_error(mensaje: str, modulo: str = ""):
    """Función de conveniencia para error"""
    get_logger().error(mensaje, modulo)

def log_critical(mensaje: str, modulo: str = ""):
    """Función de conveniencia para critical"""
    get_logger().critical(mensaje, modulo)