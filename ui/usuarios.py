"""
Módulo de Usuarios para NegocioSmart
Gestión de usuarios y permisos del sistema
"""

import customtkinter as ctk
from tkinter import messagebox
from utils.logger import Logger

class ModuloUsuarios:
    """Módulo de gestión de usuarios"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = Logger() if Logger else None
        
    def mostrar(self):
        """Mostrar interfaz de usuarios"""
        messagebox.showinfo(
            "👥 Gestión de Usuarios", 
            "🚧 Módulo de usuarios en desarrollo\n\n"
            "✨ Próximamente disponible:\n\n"
            "• Crear usuarios\n"
            "• Asignar permisos\n" 
            "• Roles de sistema\n"
            "• Control de acceso\n"
            "• Auditoría de actividad"
        )
        
        if self.logger:
            self.logger.info("👥 Módulo de usuarios accedido")