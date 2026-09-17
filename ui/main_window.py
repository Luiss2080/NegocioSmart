"""
Ventana Principal - NegocioSmart
===========================

Ventana principal del sistema que contiene el menú, barra de herramientas
y el área de trabajo donde se cargan los diferentes módulos.

Autor: Sistema NegocioSmart
Fecha: 2025-10-04
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from pathlib import Path
import sys
import os

# Configurar CustomTkinter
ctk.set_appearance_mode("light")  # "light" o "dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# Importar módulos de UI
try:
    from .dashboard import Dashboard
    from .productos import ModuloProductos
    from .ventas import ModuloVentas
    from .clientes import ModuloClientes
    from .reportes import ModuloReportes
    modulos_disponibles = True
except ImportError as e:
    print(f"Algunos módulos de UI no están disponibles: {e}")
    modulos_disponibles = False

class MainWindow:
    """Ventana principal de la aplicación NegocioSmart"""
    
    def __init__(self):
        print("🔧 Inicializando MainWindow...")
        # Crear ventana principal
        print("📱 Creando CTk...")
        self.root = ctk.CTk()
        print("✅ CTk creado exitosamente")
        self.root.title("NegocioSmart - Sistema de Gestión de Ventas e Inventario")
        self.root.geometry("1200x800")
        # self.root.state('zoomed')  # Maximizada en Windows - Comentado por compatibilidad
        
        # Variables
        self.modulo_actual = None
        self.usuario_actual = None
        
        # Configurar el ícono (si existe)
        try:
            icon_path = "assets/images/icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Configurar el evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Inicializar interfaz
        print("🔧 Creando widgets...")
        self._crear_widgets()
        print("✅ Widgets creados")
        
        print("🔧 Configurando layout...")
        self._configurar_layout()
        print("✅ Layout configurado")
        
        print("🔧 Cargando dashboard...")
        self._cargar_dashboard()
        print("✅ Dashboard cargado")
    
    def _crear_widgets(self):
        """Crea todos los widgets de la ventana principal"""
        
        print("    📦 Creando frame principal...")
        # Frame principal (temporalmente sin parámetros para debug)
        self.main_frame = ctk.CTkFrame(self.root)
        print("    📦 Frame creado, aplicando pack...")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        print("    ✅ Frame principal configurado")
        
        # Crear barra superior
        print("  🔧 Creando barra superior...")
        self._crear_barra_superior()
        print("  ✅ Barra superior creada")
        
        # Crear menú lateral
        print("  🔧 Creando menú lateral...")
        self._crear_menu_lateral()
        print("  ✅ Menú lateral creado")
        
        # Crear área de contenido
        print("  🔧 Creando área de contenido...")
        self._crear_area_contenido()
        print("  ✅ Área de contenido creada")
        
        # Crear barra de estado
        print("  🔧 Creando barra de estado...")
        self._crear_barra_estado()
        print("  ✅ Barra de estado creada")
    
    def _crear_barra_superior(self):
        """Crea la barra superior con logo y información"""
        self.barra_superior = ctk.CTkFrame(self.main_frame, height=80)
        self.barra_superior.pack(fill="x", padx=10, pady=(10, 5))
        self.barra_superior.pack_propagate(False)
        
        # Logo y título
        self.titulo_frame = ctk.CTkFrame(self.barra_superior, fg_color="transparent")
        self.titulo_frame.pack(side="left", fill="y", padx=20)
        
        self.titulo_principal = ctk.CTkLabel(
            self.titulo_frame, 
            text="🏪 NegocioSmart", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.titulo_principal.pack(side="top", anchor="w")
        
        self.subtitulo = ctk.CTkLabel(
            self.titulo_frame, 
            text="Sistema de Gestión de Ventas e Inventario", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitulo.pack(side="top", anchor="w")
        
        # Información del usuario (lado derecho)
        self.info_frame = ctk.CTkFrame(self.barra_superior, fg_color="transparent")
        self.info_frame.pack(side="right", fill="y", padx=20)
        
        self.info_usuario = ctk.CTkLabel(
            self.info_frame, 
            text="👤 Usuario: Administrador", 
            font=ctk.CTkFont(size=12)
        )
        self.info_usuario.pack(side="top", anchor="e", pady=(15, 0))
        
        self.info_fecha = ctk.CTkLabel(
            self.info_frame, 
            text="📅 Fecha: " + self._obtener_fecha_actual(), 
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.info_fecha.pack(side="top", anchor="e")
    
    def _crear_menu_lateral(self):
        """Crea el menú lateral de navegación"""
        self.menu_lateral = ctk.CTkFrame(self.main_frame)
        self.menu_lateral.pack(side="left", fill="y", padx=(10, 5), pady=5)
        self.menu_lateral.pack_propagate(False)
        
        # Título del menú
        self.menu_titulo = ctk.CTkLabel(
            self.menu_lateral, 
            text="📋 MENÚ PRINCIPAL", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.menu_titulo.pack(pady=(20, 10))
        
        # Botones del menú
        self._crear_botones_menu()
    
    def _crear_botones_menu(self):
        """Crea los botones del menú lateral"""
        botones_menu = [
            ("🏠 Dashboard", self._cargar_dashboard, "#1f538d"),
            ("📦 Productos", self._cargar_productos, "#28a745"),
            ("💰 Punto de Venta", self._cargar_pos, "#17a2b8"),
            ("👥 Clientes", self._cargar_clientes, "#6f42c1"),
            ("📊 Reportes", self._cargar_reportes, "#fd7e14"),
            ("⚙️ Configuración", self._cargar_configuracion, "#6c757d"),
            ("👤 Usuarios", self._cargar_usuarios, "#e83e8c"),
            ("🚪 Salir", self._salir, "#dc3545")
        ]
        
        self.botones_menu = {}
        
        for texto, comando, color in botones_menu:
            btn = ctk.CTkButton(
                self.menu_lateral,
                text=texto,
                command=comando,
                width=200,
                height=40,
                font=ctk.CTkFont(size=12),
                fg_color=color,
                hover_color=self._oscurecer_color(color)
            )
            btn.pack(pady=5, padx=20)
            self.botones_menu[texto] = btn
    
    def _crear_area_contenido(self):
        """Crea el área principal donde se cargan los módulos"""
        self.area_contenido = ctk.CTkFrame(self.main_frame)
        self.area_contenido.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Frame para el contenido actual
        self.contenido_frame = ctk.CTkFrame(self.area_contenido, fg_color="transparent")
        self.contenido_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _crear_barra_estado(self):
        """Crea la barra de estado en la parte inferior"""
        self.barra_estado = ctk.CTkFrame(self.main_frame, height=30)
        self.barra_estado.pack(fill="x", side="bottom", padx=10, pady=(5, 10))
        self.barra_estado.pack_propagate(False)
        
        self.estado_label = ctk.CTkLabel(
            self.barra_estado, 
            text="✅ Sistema iniciado correctamente",
            font=ctk.CTkFont(size=10)
        )
        self.estado_label.pack(side="left", padx=10, pady=5)
        
        self.version_label = ctk.CTkLabel(
            self.barra_estado, 
            text="NegocioSmart v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.version_label.pack(side="right", padx=10, pady=5)
    
    def _configurar_layout(self):
        """Configura el layout y responsividad"""
        # Configurar grid weights si es necesario
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    # Métodos para cargar módulos
    
    def _limpiar_contenido(self):
        """Limpia el área de contenido"""
        for widget in self.contenido_frame.winfo_children():
            widget.destroy()
    
    def _cargar_dashboard(self):
        """Carga el dashboard principal"""
        self._limpiar_contenido()
        self._actualizar_estado("📊 Cargando Dashboard...")
        
        # Temporalmente usar placeholder para debug
        self._mostrar_modulo_placeholder("🏠 Dashboard", 
            "Panel de control con estadísticas en tiempo real")
    
    def _cargar_productos(self):
        """Carga el módulo de productos"""
        self._limpiar_contenido()
        self._actualizar_estado("📦 Cargando módulo de Productos...")
        
        if modulos_disponibles:
            productos = ModuloProductos(self.contenido_frame)
            self.modulo_actual = productos
            self._actualizar_estado("✅ Módulo de Productos cargado")
        else:
            self._mostrar_modulo_placeholder("📦 Gestión de Productos", 
                "Administración completa del inventario")
    
    def _cargar_pos(self):
        """Carga el punto de venta"""
        self._limpiar_contenido()
        self._actualizar_estado("💰 Cargando Punto de Venta...")
        
        if modulos_disponibles:
            pos = ModuloVentas(self.contenido_frame)
            self.modulo_actual = pos
            self._actualizar_estado("✅ Punto de Venta cargado")
        else:
            self._mostrar_modulo_placeholder("💰 Punto de Venta", 
                "Sistema de ventas rápido y eficiente")
    
    def _cargar_clientes(self):
        """Carga el módulo de clientes"""
        self._limpiar_contenido()
        self._actualizar_estado("👥 Cargando módulo de Clientes...")
        
        if modulos_disponibles:
            clientes = ModuloClientes(self.contenido_frame)
            self.modulo_actual = clientes
            self._actualizar_estado("✅ Módulo de Clientes cargado")
        else:
            self._mostrar_modulo_placeholder("👥 Gestión de Clientes", 
                "Administración de la base de clientes")
    
    def _cargar_reportes(self):
        """Carga el módulo de reportes"""
        self._limpiar_contenido()
        self._actualizar_estado("📊 Cargando módulo de Reportes...")
        
        if modulos_disponibles:
            reportes = ModuloReportes(self.contenido_frame)
            self.modulo_actual = reportes
            self._actualizar_estado("✅ Módulo de Reportes cargado")
        else:
            self._mostrar_modulo_placeholder("📊 Reportes y Análisis", 
                "Gráficos y estadísticas del negocio")
    
    def _cargar_configuracion(self):
        """Carga el módulo de configuración"""
        self._limpiar_contenido()
        self._actualizar_estado("⚙️ Cargando Configuración...")
        
        try:
            from ui.configuracion import ModuloConfiguracion
            config = ModuloConfiguracion(self.contenido_frame)
            self.modulo_actual = config
            self._actualizar_estado("✅ Configuración cargada")
        except ImportError:
            self._mostrar_modulo_placeholder("⚙️ Configuración", 
                "Ajustes del sistema y personalización")
    
    def _cargar_usuarios(self):
        """Carga el módulo de usuarios"""
        self._limpiar_contenido()
        self._actualizar_estado("👤 Cargando módulo de Usuarios...")
        
        try:
            from ui.usuarios import ModuloUsuarios
            usuarios = ModuloUsuarios(self.contenido_frame)
            self.modulo_actual = usuarios
            self._actualizar_estado("✅ Módulo de Usuarios cargado")
        except ImportError:
            self._mostrar_modulo_placeholder("👤 Gestión de Usuarios", 
                "Administración de usuarios del sistema")
    
    def _mostrar_modulo_placeholder(self, titulo: str, descripcion: str):
        """Muestra un placeholder cuando el módulo no está disponible"""
        # Título del módulo
        titulo_label = ctk.CTkLabel(
            self.contenido_frame, 
            text=titulo, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo_label.pack(pady=(20, 10))
        
        # Descripción
        desc_label = ctk.CTkLabel(
            self.contenido_frame, 
            text=descripcion, 
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        desc_label.pack(pady=(0, 30))
        
        # Mensaje
        mensaje_frame = ctk.CTkFrame(self.contenido_frame)
        mensaje_frame.pack(pady=50, padx=50, fill="x")
        
        mensaje_label = ctk.CTkLabel(
            mensaje_frame,
            text="🚧 Módulo en desarrollo\n\nEste módulo estará disponible próximamente.",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        mensaje_label.pack(pady=30)
    
    # Métodos auxiliares
    
    def _obtener_fecha_actual(self):
        """Obtiene la fecha actual formateada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y")
    
    def _oscurecer_color(self, color_hex: str) -> str:
        """Oscurece un color para el efecto hover"""
        # Implementación simple - en producción usar una librería de colores
        colores_hover = {
            "#1f538d": "#1a4a7e",
            "#28a745": "#219a3c",
            "#17a2b8": "#138496",
            "#6f42c1": "#5a32a3",
            "#fd7e14": "#e96b00",
            "#6c757d": "#545b62",
            "#e83e8c": "#d91a72",
            "#dc3545": "#c82333"
        }
        return colores_hover.get(color_hex, color_hex)
    
    def _actualizar_estado(self, mensaje: str):
        """Actualiza el mensaje en la barra de estado"""
        self.estado_label.configure(text=mensaje)
        self.root.update_idletasks()
    
    def _salir(self):
        """Maneja la salida de la aplicación"""
        self.on_closing()
    
    def on_closing(self):
        """Maneja el evento de cierre de la aplicación"""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir de NegocioSmart?"):
            try:
                # Aquí se pueden hacer tareas de limpieza
                # Como cerrar conexiones de BD, guardar configuración, etc.
                pass
            finally:
                self.root.quit()
                self.root.destroy()
    
    def ejecutar(self):
        """Inicia el loop principal de la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            messagebox.showerror("Error crítico", f"Error inesperado: {str(e)}")
            self.on_closing()

# Función principal para ejecutar la aplicación
def main():
    """Función principal para iniciar la aplicación"""
    app = MainWindow()
    app.ejecutar()

if __name__ == "__main__":
    main()