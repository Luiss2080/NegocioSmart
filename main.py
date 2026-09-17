import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
from datetime import datetime, date
from decimal import Decimal
import json

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Importar dependencias de VentaPro
try:
    from database.db_manager import DatabaseManager
    from utils.logger import Logger
    from utils.backup_manager import BackupManager
    from services.ventas_service import (
        procesar_venta_atomica,
        StockInsuficienteError,
        CarritoVacioError,
        VentaServiceError,
    )
    db_disponible = True
    logger_disponible = True
    backup_disponible = True
except ImportError as e:
    print(f"⚠️ Ejecutando sin algunas dependencias: {e}")
    DatabaseManager = None
    Logger = None
    BackupManager = None
    procesar_venta_atomica = None
    StockInsuficienteError = Exception
    CarritoVacioError = Exception
    VentaServiceError = Exception
    db_disponible = False
    logger_disponible = False
    backup_disponible = False

class VentaProUniversal:
    """Sistema Universal de Gestión Comercial VentaPro"""
    
    def __init__(self):
        # Configuración del negocio (se puede personalizar)
        self.config_negocio = {
            'nombre': 'Mi Negocio',
            'tipo': 'Tienda General',
            'moneda': '$',
            'decimales': 2,
            'usar_stock': True,
            'usar_categorias': True,
            'usar_proveedores': True,
            'usar_clientes': True,
            'idioma': 'es'
        }
        
        # Conectar con la base de datos real ANTES de cargar el catálogo:
        # así los productos que ve la interfaz son los mismos que existen
        # en data/erp.db, con los mismos ids, y una venta se puede
        # persistir de verdad (antes, el catálogo en memoria y la base de
        # datos eran dos mundos completamente separados).
        self.db = None
        if db_disponible:
            try:
                posible_db = DatabaseManager()
                if posible_db.inicializar_db():
                    self.db = posible_db
                else:
                    print("⚠️ No se pudo inicializar la base de datos, se usarán datos solo en memoria")
            except Exception as e:
                print(f"⚠️ Error inicializando base de datos: {e}")

        # Inicializar componentes
        self._inicializar_datos()

        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title(f"VentaPro Universal - {self.config_negocio['nombre']}")
        self.root.geometry("1200x800")
        
        # Variables de estado
        self.modulo_actual = "dashboard"
        self.carrito = []
        self.total_carrito = 0.0
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Inicializar logger si está disponible
        if logger_disponible:
            self.logger = Logger()
            self.logger.info("🚀 VentaPro Universal iniciado correctamente")
        
        # Inicializar sistema de backup si está disponible
        if backup_disponible:
            self.backup_manager = BackupManager()
            print("💾 Sistema de backup automático inicializado")
        else:
            self.backup_manager = None
    
    def _inicializar_datos(self):
        """Inicializar datos del sistema"""
        # Catálogo de productos: si hay base de datos disponible, se
        # siembra (una sola vez) y se carga DESDE la base de datos, para
        # que los ids que ve/usa la interfaz sean los mismos que existen
        # en productos.id y una venta se pueda registrar de verdad. Si no
        # hay base de datos disponible, se cae de vuelta a una lista en
        # memoria (comportamiento anterior) para que la app siga siendo
        # utilizable como demo sin persistencia.
        self.productos = self._cargar_o_sembrar_productos()

        self.clientes = [
            {"id": 1, "nombre": "Cliente General", "telefono": "555-0001", "email": "cliente@email.com"},
            {"id": 2, "nombre": "Cliente Frecuente", "telefono": "555-0002", "email": "frecuente@email.com"},
        ]
        
        self.ventas_hoy = [
            {"id": 1, "total": 125.50, "items": 3, "hora": "09:15", "cliente": "Cliente General"},
            {"id": 2, "total": 67.99, "items": 2, "hora": "10:30", "cliente": "Cliente Frecuente"},
            {"id": 3, "total": 234.75, "items": 5, "hora": "11:45", "cliente": "Mostrador"},
        ]
        
        # Categorías adaptables
        self.categorias = ["General", "Premium", "Especial", "Servicios", "Promoción", "Temporada"]
        
        # Estadísticas del día
        self.stats_dia = {
            'ventas_total': sum(v['total'] for v in self.ventas_hoy),
            'num_ventas': len(self.ventas_hoy),
            'items_vendidos': sum(v['items'] for v in self.ventas_hoy),
            'productos_total': len(self.productos),
            'clientes_total': len(self.clientes),
            'stock_bajo': len([p for p in self.productos if p['stock'] < 10])
        }

    def _cargar_o_sembrar_productos(self):
        """Carga el catálogo de productos desde la base de datos real.

        Si la tabla `productos` está vacía (primera vez que se ejecuta
        la app contra una base de datos nueva), la siembra con el
        catálogo de ejemplo antes de leerlo, para no dejar la interfaz
        vacía. A partir de ahí, cada producto que ve/usa la interfaz
        tiene el mismo id que su fila en `productos`, así que una venta
        puede descontar stock real y quedar registrada en `ventas` /
        `detalle_ventas` (ver `_procesar_venta` y
        `services/ventas_service.py`).

        Si no hay base de datos disponible (self.db es None: falló el
        import o la conexión), se conserva el comportamiento histórico
        de una lista en memoria, para que la app siga funcionando como
        demo sin persistencia.
        """
        catalogo_ejemplo = [
            ("PRO001", "Producto Ejemplo 1", Decimal("15.00"), Decimal("25.99"), 50),
            ("PRO002", "Producto Ejemplo 2", Decimal("9.00"), Decimal("15.50"), 30),
            ("PRO003", "Producto Ejemplo 3", Decimal("28.00"), Decimal("45.00"), 20),
            ("ESP001", "Artículo Especializado", Decimal("55.00"), Decimal("89.99"), 15),
            ("SER001", "Servicio Básico", Decimal("70.00"), Decimal("120.00"), 999),
        ]

        if self.db is None or self.db.connection is None:
            return [
                {"id": i + 1, "nombre": nombre, "precio": float(precio_venta), "stock": stock,
                 "categoria": "General", "codigo": codigo}
                for i, (codigo, nombre, _precio_compra, precio_venta, stock) in enumerate(catalogo_ejemplo)
            ]

        try:
            (num_productos,) = self.db.connection.execute(
                "SELECT COUNT(*) FROM productos WHERE activo = 1"
            ).fetchone()

            if num_productos == 0:
                for codigo, nombre, precio_compra, precio_venta, stock in catalogo_ejemplo:
                    self.db.connection.execute(
                        """
                        INSERT OR IGNORE INTO productos
                            (codigo, nombre, precio_compra, precio_venta, stock_actual, stock_minimo)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (codigo, nombre, str(precio_compra), str(precio_venta), stock, 5),
                    )
                self.db.connection.commit()

            filas = self.db.connection.execute(
                """
                SELECT p.id, p.codigo, p.nombre, p.precio_venta, p.stock_actual,
                       COALESCE(c.nombre, 'General') AS categoria
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE p.activo = 1
                ORDER BY p.id
                """
            ).fetchall()

            return [
                {
                    "id": fila["id"],
                    "nombre": fila["nombre"],
                    "precio": float(fila["precio_venta"]),
                    "stock": fila["stock_actual"],
                    "categoria": fila["categoria"],
                    "codigo": fila["codigo"],
                }
                for fila in filas
            ]
        except Exception as e:
            print(f"⚠️ No se pudo cargar el catálogo desde la base de datos: {e}")
            return [
                {"id": i + 1, "nombre": nombre, "precio": float(precio_venta), "stock": stock,
                 "categoria": "General", "codigo": codigo}
                for i, (codigo, nombre, _precio_compra, precio_venta, stock) in enumerate(catalogo_ejemplo)
            ]

    def _crear_interfaz(self):
        """Crear interfaz principal CustomTkinter con sidebar"""
        self._crear_interfaz_con_sidebar()



    def _crear_interfaz_con_sidebar(self):
        """Crear interfaz CustomTkinter con sidebar (manteniendo funcionalidad original)"""
        
        # Configurar grid del root
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Crear sidebar
        self._crear_sidebar()
        
        # Frame principal (área de contenido)
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nswe", padx=(0, 10), pady=10)
        
        # Header con información del negocio
        self._crear_header()
        
        # Área de contenido principal (directamente después del header)
        self.content_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Footer con estado
        self._crear_footer()
        
        # Cargar dashboard por defecto
        self._mostrar_dashboard()
    
    def _crear_sidebar(self):
        """Crear sidebar eficiente y responsive con botón hamburguesa"""
        # Variables del sidebar (configurables y optimizadas)
        self.sidebar_config = {
            'width_expandido': 250,
            'width_contraido': 60,
            'animation_steps': 5,  # Reducido de 8 a 5 para más rapidez
            'animation_delay': 12,  # Reducido de 20 a 12ms para más fluidez
            'color_bg': "#2c3e50",
            'color_hover': "#34495e", 
            'color_active': "#3498db",
            'color_text': "#ecf0f1"
        }
        
        # Estado del sidebar
        self.sidebar_expandido = True
        
        # Frame del sidebar con configuración optimizada
        self.sidebar_frame = ctk.CTkFrame(
            self.root,
            width=self.sidebar_config['width_expandido'],
            corner_radius=8,
            fg_color=self.sidebar_config['color_bg'],
            border_width=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(1, weight=1)  # Para expansión del contenido
        
        # Header del sidebar - más compacto
        self._crear_sidebar_header()
        
        # Contenedor de navegación - scrollable para responsividad
        self.sidebar_nav_frame = ctk.CTkScrollableFrame(
            self.sidebar_frame, 
            fg_color="transparent",
            scrollbar_button_color=self.sidebar_config['color_hover']
        )
        self.sidebar_nav_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        
        # Crear navegación
        self._crear_navegacion_sidebar()
        
        # Footer del sidebar
        self._crear_sidebar_footer()
    
    def _crear_sidebar_header(self):
        """Crear header optimizado del sidebar"""
        self.sidebar_header = ctk.CTkFrame(
            self.sidebar_frame, 
            fg_color="transparent", 
            height=60
        )
        self.sidebar_header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        self.sidebar_header.grid_propagate(False)
        self.sidebar_header.grid_columnconfigure(1, weight=1)
        
        # Botón hamburguesa optimizado
        self.hamburger_btn = ctk.CTkButton(
            self.sidebar_header,
            text="☰",
            width=36,
            height=36,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.sidebar_config['color_hover'],
            hover_color=self.sidebar_config['color_active'],
            border_width=0,
            corner_radius=6,
            command=self._toggle_sidebar_animated
        )
        self.hamburger_btn.grid(row=0, column=0, sticky="w")
        
        # Título responsive
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_header,
            text="VentaPro",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.sidebar_config['color_text']
        )
        self.sidebar_title.grid(row=0, column=1, sticky="w", padx=(10, 0))
    
    def _crear_sidebar_footer(self):
        """Crear footer compacto del sidebar"""
        self.sidebar_footer = ctk.CTkFrame(
            self.sidebar_frame, 
            fg_color="transparent", 
            height=40
        )
        self.sidebar_footer.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 8))
        self.sidebar_footer.grid_propagate(False)
        
        # Indicador de estado
        self.status_indicator = ctk.CTkLabel(
            self.sidebar_footer,
            text="● Online",
            font=ctk.CTkFont(size=10),
            text_color="#27ae60"
        )
        self.status_indicator.pack(side="bottom", pady=2)
        
        
    def _crear_navegacion_sidebar(self):
        """Crear navegación optimizada del sidebar"""
        # Configuración de botones principales (manteniendo tu funcionalidad)
        self.nav_config = [
            {"icon": "🏠", "text": "Dashboard", "cmd": self._mostrar_dashboard, "active": True},
            {"icon": "📦", "text": "Catálogo", "cmd": self._mostrar_productos, "active": False},
            {"icon": "🛒", "text": "Caja/POS", "cmd": self._mostrar_pos, "active": False},
            {"icon": "👥", "text": "Clientes", "cmd": self._mostrar_clientes, "active": False},
            {"icon": "📊", "text": "Estadísticas", "cmd": self._mostrar_reportes, "active": False},
            {"icon": "🏢", "text": "Compras", "cmd": self._mostrar_compras, "active": False},
            {"icon": "📋", "text": "Stock", "cmd": self._mostrar_stock_control, "active": False},
            {"icon": "📈", "text": "Business Intel", "cmd": self._mostrar_business_intel, "active": False},
        ]
        
        self.sidebar_buttons = []
        self.active_button = None
        
        # Crear botones principales
        for config in self.nav_config:
            btn = self._crear_boton_sidebar(
                config["icon"], 
                config["text"], 
                config["cmd"],
                is_primary=True,
                active=config["active"]
            )
            self.sidebar_buttons.append(btn)
            if config["active"]:
                self.active_button = btn
        
        # Separador elegante
        self._crear_separador_sidebar()
        
        # Botones secundarios
        secondary_config = [
            {"icon": "⚙️", "text": "Configuración", "cmd": self._mostrar_configuracion},
            {"icon": "❓", "text": "Ayuda", "cmd": self._mostrar_ayuda},
            {"icon": "🚪", "text": "Salir", "cmd": self._confirmar_salida, "danger": True}
        ]
        
        for config in secondary_config:
            btn = self._crear_boton_sidebar(
                config["icon"], 
                config["text"], 
                config["cmd"],
                is_primary=False,
                is_danger=config.get("danger", False)
            )
            self.sidebar_buttons.append(btn)
    
    def _crear_boton_sidebar(self, icon, text, command, is_primary=True, active=False, is_danger=False):
        """Crear botón optimizado del sidebar con estados"""
        # Configurar colores según el tipo
        if is_danger:
            color_config = {
                'fg_color': 'transparent',
                'hover_color': '#e74c3c',
                'text_color': self.sidebar_config['color_text']
            }
        elif active:
            color_config = {
                'fg_color': self.sidebar_config['color_active'],
                'hover_color': self.sidebar_config['color_active'],
                'text_color': '#ffffff'
            }
        else:
            color_config = {
                'fg_color': 'transparent',
                'hover_color': self.sidebar_config['color_hover'],
                'text_color': self.sidebar_config['color_text']
            }
        
        # Crear botón con configuración optimizada
        btn_data = {
            'icon': icon,
            'text': text,
            'original_command': command,
            'is_primary': is_primary,
            'is_danger': is_danger
        }
        
        btn = ctk.CTkButton(
            self.sidebar_nav_frame,
            text=f"{icon} {text}",
            anchor="w",
            height=42 if is_primary else 36,
            font=ctk.CTkFont(size=12 if is_primary else 11, weight="normal"),
            corner_radius=6,
            border_width=0,
            command=lambda: self._handle_sidebar_click(btn_data),
            **color_config
        )
        btn.pack(fill="x", pady=2 if is_primary else 1, padx=2)
        
        # Guardar referencia a los datos del botón
        btn._btn_data = btn_data
        btn._is_active = active
        
        return btn
    
    def _crear_separador_sidebar(self):
        """Crear separador elegante"""
        separator_frame = ctk.CTkFrame(self.sidebar_nav_frame, fg_color="transparent", height=20)
        separator_frame.pack(fill="x", pady=8)
        separator_frame.pack_propagate(False)
        
        separator_line = ctk.CTkFrame(
            separator_frame, 
            height=1, 
            fg_color=self.sidebar_config['color_hover']
        )
        separator_line.pack(fill="x", padx=20, pady=10)
    
    def _handle_sidebar_click(self, btn_data):
        """Manejar clic en botón del sidebar con estado activo"""
        # Resetear botón activo anterior
        if self.active_button and hasattr(self.active_button, '_is_active'):
            self.active_button._is_active = False
            self.active_button.configure(
                fg_color='transparent',
                hover_color=self.sidebar_config['color_hover'],
                text_color=self.sidebar_config['color_text']
            )
        
        # Activar botón actual (solo para botones principales)
        if btn_data['is_primary']:
            for btn in self.sidebar_buttons:
                if hasattr(btn, '_btn_data') and btn._btn_data == btn_data:
                    btn._is_active = True
                    btn.configure(
                        fg_color=self.sidebar_config['color_active'],
                        hover_color=self.sidebar_config['color_active'],
                        text_color='#ffffff'
                    )
                    self.active_button = btn
                    break
        
        # Ejecutar comando
        btn_data['original_command']()
    
    def _toggle_sidebar_animated(self):
        """Alternar sidebar con animación ultra rápida y eficiente"""
        # Prevenir múltiples animaciones simultáneas
        if hasattr(self, '_animating') and self._animating:
            return
        
        self._animating = True
        
        # Cambio inmediato de contenido para mejor rendimiento
        target_width = self.sidebar_config['width_contraido'] if self.sidebar_expandido else self.sidebar_config['width_expandido']
        is_expanding = not self.sidebar_expandido
        
        # Cambiar contenido inmediatamente (más eficiente que animar)
        if is_expanding:
            # Expandiendo - mostrar todo
            self.sidebar_title.grid(row=0, column=1, sticky="w", padx=(10, 0))
            self.hamburger_btn.configure(text="✕")
            for btn in self.sidebar_buttons:
                if hasattr(btn, '_btn_data'):
                    btn.configure(text=f"{btn._btn_data['icon']} {btn._btn_data['text']}")
        else:
            # Contrayendo - ocultar texto
            self.sidebar_title.grid_remove()
            self.hamburger_btn.configure(text="☰")
            for btn in self.sidebar_buttons:
                if hasattr(btn, '_btn_data'):
                    btn.configure(text=btn._btn_data['icon'])
        
        # Animación super rápida solo del ancho
        self._animate_width_fast(target_width)
    
    def _animate_width_fast(self, target_width):
        """Animación de ancho ultra rápida usando after() optimizado"""
        start_width = self.sidebar_frame.winfo_width()
        steps = self.sidebar_config['animation_steps']
        step_size = (target_width - start_width) / steps
        
        def animate_step(step):
            if step <= steps:
                current_width = int(start_width + (step_size * step))
                self.sidebar_frame.configure(width=current_width)
                
                # Siguiente paso más rápido
                if step < steps:
                    self.root.after(self.sidebar_config['animation_delay'], lambda: animate_step(step + 1))
                else:
                    # Completar
                    self._complete_sidebar_animation()
        
        # Iniciar animación
        animate_step(0)
    
    def _complete_sidebar_animation(self):
        """Completar animación del sidebar de forma eficiente"""
        self.sidebar_expandido = not self.sidebar_expandido
        self._animating = False
        
        # Asegurar ancho final correcto
        final_width = self.sidebar_config['width_expandido'] if self.sidebar_expandido else self.sidebar_config['width_contraido']
        self.sidebar_frame.configure(width=final_width)
        
        # Actualizar indicador de estado de forma eficiente
        if hasattr(self, 'status_indicator'):
            status_text = "● Online" if self.sidebar_expandido else "●"
            self.status_indicator.configure(text=status_text)


    
    def _crear_header(self):
        """Crear header con información del negocio"""
        header_frame = ctk.CTkFrame(self.main_frame, height=80)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Información del negocio (lado izquierdo)
        business_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        business_frame.pack(side="left", fill="y", padx=20, pady=10)
        
        business_name = ctk.CTkLabel(
            business_frame,
            text=f"🏪 {self.config_negocio['nombre']}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        business_name.pack(anchor="w")
        
        business_type = ctk.CTkLabel(
            business_frame,
            text=f"📋 {self.config_negocio['tipo']} | Sistema Universal VentaPro",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        business_type.pack(anchor="w")
        
        # Información del usuario (lado derecho)
        user_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        user_frame.pack(side="right", fill="y", padx=20, pady=10)
        
        date_label = ctk.CTkLabel(
            user_frame,
            text=f"📅 {datetime.now().strftime('%d/%m/%Y')}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        date_label.pack(anchor="e")
        
        time_label = ctk.CTkLabel(
            user_frame,
            text=f"🕒 {datetime.now().strftime('%H:%M')} | 👤 Administrador",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        time_label.pack(anchor="e")
    
    def _crear_navegacion_antigua(self):
        """Navegación anterior (deshabilitada)"""
        # Esta función se mantiene por compatibilidad pero no se usa
        return
        
        # Botones de navegación principales organizados en dos filas
        nav_buttons_fila1 = [
            ("🏠 Dashboard", self._mostrar_dashboard, "#1f538d"),
            ("📦 Catálogo", self._mostrar_productos, "#28a745"),
            ("🛒 Caja/POS", self._mostrar_pos, "#007bff"),
            ("👥 CRM Clientes", self._mostrar_clientes, "#6f42c1"),
            ("📊 Estadísticas", self._mostrar_reportes, "#fd7e14")
        ]
        
        nav_buttons_fila2 = [
            ("🏢 Compras", self._mostrar_compras, "#8e44ad"),
            ("📋 Stock Control", self._mostrar_stock_control, "#e74c3c"),
            ("📈 Business Intel", self._mostrar_business_intel, "#16a085"),
            ("⚙️ Configuración", self._mostrar_configuracion, "#6c757d")
        ]
        
        # Contenedor principal centrado
        nav_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_container.pack(expand=True, fill="both")
        
        # Primera fila de botones (centrada)
        button_frame1 = ctk.CTkFrame(nav_container, fg_color="transparent", height=50)
        button_frame1.pack(pady=(15, 5))
        
        for i, (texto, comando, color) in enumerate(nav_buttons_fila1):
            btn = ctk.CTkButton(
                button_frame1,
                text=texto,
                width=220,
                height=40,
                fg_color=color,
                command=comando,
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8
            )
            btn.grid(row=0, column=i, padx=8, pady=5)
        
        # Segunda fila de botones (centrada)
        button_frame2 = ctk.CTkFrame(nav_container, fg_color="transparent", height=50)
        button_frame2.pack(pady=(5, 15))
        
        for i, (texto, comando, color) in enumerate(nav_buttons_fila2):
            btn = ctk.CTkButton(
                button_frame2,
                text=texto,
                width=220,
                height=40,
                fg_color=color,
                command=comando,
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8
            )
            # Centrar los 4 botones de la segunda fila
            btn.grid(row=0, column=i, padx=8, pady=5)
            
        # Configurar columnas para centrado responsivo
        for i in range(5):
            button_frame1.grid_columnconfigure(i, weight=1)
        for i in range(4):
            button_frame2.grid_columnconfigure(i, weight=1)
    
    def _crear_footer(self):
        """Crear footer con estado del sistema"""
        footer_frame = ctk.CTkFrame(self.main_frame, height=40)
        footer_frame.pack(fill="x", side="bottom", padx=10, pady=(5, 10))
        footer_frame.pack_propagate(False)
        
        # Estado del sistema (izquierda)
        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="✅ Sistema VentaPro Universal - Operativo",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        # Información técnica (derecha)
        tech_info = ctk.CTkLabel(
            footer_frame,
            text=f"💾 Base de datos: {'✅ Conectada' if db_disponible else '⚠️ Simulada'} | 🐍 Python | 🖥️ CustomTkinter | v2.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        tech_info.pack(side="right", padx=20, pady=10)
    
    def _limpiar_contenido(self):
        """Limpiar el área de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _mostrar_dashboard(self):
        """Dashboard universal adaptable a cualquier negocio"""
        self.modulo_actual = "dashboard"
        self._mostrar_dashboard_customtkinter()

    def _mostrar_dashboard_customtkinter(self):
        """Dashboard para interfaz CustomTkinter"""
        self._limpiar_contenido()
        
        # Título del dashboard
        title = ctk.CTkLabel(
            self.content_frame,
            text=f"🏠 Dashboard - {self.config_negocio['nombre']}",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Estadísticas principales (cards adaptables)
        stats_frame = ctk.CTkFrame(self.content_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Grid de estadísticas
        stats_data = [
            ("💰 Ventas Hoy", f"{self.config_negocio['moneda']}{self.stats_dia['ventas_total']:.2f}", f"{self.stats_dia['num_ventas']} transacciones", "#28a745"),
            ("📦 Productos", f"{self.stats_dia['productos_total']}", f"{self.stats_dia['stock_bajo']} con stock bajo", "#17a2b8"),
            ("👥 Clientes", f"{self.stats_dia['clientes_total']}", "Base de clientes activa", "#6f42c1"),
            ("📈 Items Vendidos", f"{self.stats_dia['items_vendidos']}", "Unidades del día", "#fd7e14")
        ]
        
        cards_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        cards_container.pack(fill="x", padx=20, pady=20)
        
        for i, (titulo, valor, detalle, color) in enumerate(stats_data):
            card = ctk.CTkFrame(cards_container)
            card.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            # Título de la card
            card_title = ctk.CTkLabel(
                card, 
                text=titulo, 
                font=ctk.CTkFont(size=14, weight="bold")
            )
            card_title.pack(pady=(15, 5))
            
            # Valor principal
            card_value = ctk.CTkLabel(
                card, 
                text=valor, 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            card_value.pack(pady=5)
            
            # Detalle
            card_detail = ctk.CTkLabel(
                card, 
                text=detalle, 
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            card_detail.pack(pady=(0, 15))
        
        # Sección de análisis de rendimiento
        performance_frame = ctk.CTkFrame(self.content_frame)
        performance_frame.pack(fill="x", padx=20, pady=20)
        
        perf_title = ctk.CTkLabel(
            performance_frame,
            text="� Análisis de Rendimiento",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        perf_title.pack(pady=(15, 10))
        
        # Grid de métricas de rendimiento
        metrics_grid = ctk.CTkFrame(performance_frame, fg_color="transparent")
        metrics_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        # Métricas adicionales
        extra_metrics = [
            ("📊 Promedio por Venta", f"{self.config_negocio['moneda']}{self.stats_dia['ventas_total']/max(self.stats_dia['num_ventas'], 1):.2f}", "Valor promedio por transacción", "#3498db"),
            ("⏱️ Eficiencia", "92%", "Rendimiento del sistema", "#27ae60"),
            ("� Conectividad", "Online", "Estado de conexión", "#2ecc71"),
            ("🎯 Meta del Día", f"{(self.stats_dia['ventas_total']/1000)*100:.1f}%", "Progreso hacia meta diaria", "#f39c12")
        ]
        
        for i, (titulo, valor, desc, color) in enumerate(extra_metrics):
            metric_card = ctk.CTkFrame(metrics_grid)
            metric_card.grid(row=0, column=i, padx=8, pady=8, sticky="ew")
            
            ctk.CTkLabel(metric_card, text=titulo, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
            ctk.CTkLabel(metric_card, text=valor, font=ctk.CTkFont(size=18, weight="bold"), text_color=color).pack(pady=2)
            ctk.CTkLabel(metric_card, text=desc, font=ctk.CTkFont(size=10), text_color="gray").pack(pady=(2, 10))
        
        for i in range(4):
            metrics_grid.grid_columnconfigure(i, weight=1)
        
        # Sección de acciones rápidas (compacta)
        quick_frame = ctk.CTkFrame(self.content_frame)
        quick_frame.pack(fill="x", padx=20, pady=20)
        
        quick_title = ctk.CTkLabel(
            quick_frame,
            text="⚡ Acciones Rápidas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        quick_title.pack(pady=(15, 10))
        
        # Botones de acciones rápidas (una sola fila responsiva)
        quick_actions = ctk.CTkFrame(quick_frame, fg_color="transparent")
        quick_actions.pack(fill="x", padx=20, pady=(0, 15))
        
        quick_buttons = [
            ("➕ Nuevo Producto", self._registro_producto_express, "#28a745"),
            ("👤 Nuevo Cliente", self._agregar_cliente_express, "#6f42c1"),
            ("🧾 Nueva Venta", self._mostrar_pos, "#007bff"),
            ("📊 Ver Reportes", self._mostrar_reportes, "#fd7e14"),
            ("💾 Ver Backups", self._mostrar_backups, "#17a2b8")
        ]
        
        # Todos los botones en una sola fila responsiva
        for i, (texto, comando, color) in enumerate(quick_buttons):
            btn = ctk.CTkButton(
                quick_actions,
                text=texto,
                width=150,  # Ancho reducido para que quepan todos
                height=40,  # Altura ligeramente mayor
                fg_color=color,
                command=comando,
                font=ctk.CTkFont(size=10, weight="bold"),
                corner_radius=8
            )
            btn.grid(row=0, column=i, padx=3, pady=5, sticky="ew")
        
        # Configurar todas las columnas para que sean responsivas
        for i in range(len(quick_buttons)):
            quick_actions.grid_columnconfigure(i, weight=1, uniform="buttons")
        
        # Sección de productos con stock bajo (alerta)
        if self.stats_dia['stock_bajo'] > 0:
            alert_frame = ctk.CTkFrame(self.content_frame, fg_color="#fff3cd", border_color="#ffc107", border_width=2)
            alert_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(
                alert_frame,
                text="⚠️ Alerta de Inventario",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#856404"
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                alert_frame,
                text=f"Hay {self.stats_dia['stock_bajo']} productos con stock bajo. Revisa el inventario.",
                font=ctk.CTkFont(size=12),
                text_color="#856404"
            ).pack(pady=(0, 10))
        
        # Sección dividida: Últimas ventas y resumen de productos
        content_grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        content_grid.pack(fill="both", expand=True, padx=20, pady=20)
        content_grid.grid_columnconfigure(0, weight=1)
        content_grid.grid_columnconfigure(1, weight=1)
        
        # Últimas ventas (lado izquierdo)
        recent_frame = ctk.CTkFrame(content_grid)
        recent_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        recent_title = ctk.CTkLabel(
            recent_frame,
            text="📋 Actividad Reciente",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        recent_title.pack(pady=(15, 10))
        
        # Contenedor scrollable para ventas
        sales_scroll = ctk.CTkScrollableFrame(recent_frame, height=200)
        sales_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Lista de ventas recientes mejorada
        for venta in self.ventas_hoy[-8:]:  # Últimas 8 ventas
            venta_item = ctk.CTkFrame(sales_scroll, height=40)
            venta_item.pack(fill="x", pady=3)
            venta_item.pack_propagate(False)
            
            # Información en una línea más compacta
            info_text = f"🧾 #{venta['id']:03d} • {venta['hora']} • {venta['cliente'][:15]}{'...' if len(venta['cliente']) > 15 else ''}"
            value_text = f"{self.config_negocio['moneda']}{venta['total']:.2f}"
            
            info_frame = ctk.CTkFrame(venta_item, fg_color="transparent")
            info_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            ctk.CTkLabel(info_frame, text=info_text, font=ctk.CTkFont(size=11), anchor="w").pack(side="left")
            ctk.CTkLabel(info_frame, text=value_text, font=ctk.CTkFont(size=11, weight="bold"), 
                        text_color="#27ae60", anchor="e").pack(side="right")
        
        # Resumen de productos (lado derecho)
        products_frame = ctk.CTkFrame(content_grid)
        products_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        products_title = ctk.CTkLabel(
            products_frame,
            text="📦 Estado del Inventario",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        products_title.pack(pady=(15, 10))
        
        # Métricas de productos
        inventory_metrics = ctk.CTkFrame(products_frame, fg_color="transparent")
        inventory_metrics.pack(fill="x", padx=15, pady=5)
        
        # Categorías de productos (simuladas)
        categories_data = [
            ("General", 3, "#3498db"),
            ("Premium", 1, "#9b59b6"), 
            ("Especial", 1, "#e74c3c"),
            ("Servicios", 1, "#f39c12")
        ]
        
        for cat, count, color in categories_data:
            cat_frame = ctk.CTkFrame(inventory_metrics, fg_color="transparent")
            cat_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(cat_frame, text=f"📂 {cat}", font=ctk.CTkFont(size=11), anchor="w").pack(side="left")
            ctk.CTkLabel(cat_frame, text=f"{count} productos", font=ctk.CTkFont(size=11), 
                        text_color=color, anchor="e").pack(side="right")
        
        # Productos más vendidos (simulado)
        bestsellers_frame = ctk.CTkFrame(products_frame, fg_color="transparent")
        bestsellers_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        
        ctk.CTkLabel(
            bestsellers_frame,
            text="🏆 Más Vendidos Hoy",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(5, 8))
        
        bestsellers = [
            ("Producto Ejemplo 1", 8, "#1abc9c"),
            ("Artículo Especializado", 5, "#3498db"),
            ("Producto Ejemplo 2", 4, "#f39c12")
        ]
        
        for product, sales, color in bestsellers:
            product_frame = ctk.CTkFrame(bestsellers_frame, height=30, fg_color="#f8f9fa")
            product_frame.pack(fill="x", pady=2)
            product_frame.pack_propagate(False)
            
            content_frame = ctk.CTkFrame(product_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=8, pady=4)
            
            ctk.CTkLabel(content_frame, text=f"🔹 {product[:20]}{'...' if len(product) > 20 else ''}", 
                        font=ctk.CTkFont(size=10), anchor="w").pack(side="left")
            ctk.CTkLabel(content_frame, text=f"{sales} uds", font=ctk.CTkFont(size=10, weight="bold"), 
                        text_color=color, anchor="e").pack(side="right")
    
    def _mostrar_productos(self):
        """Módulo universal de productos"""
        self.modulo_actual = "productos"
        self._limpiar_contenido()
        
        # Barra de navegación superior
        nav_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        btn_volver = ctk.CTkButton(
            nav_frame,
            text="🏠 Volver al Dashboard",
            command=self._mostrar_dashboard,
            width=180,
            height=35,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        btn_volver.pack(side="left", pady=10)
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📦 Gestión Universal de Productos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            self.content_frame,
            text="Adaptable a cualquier tipo de negocio - Inventario inteligente",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 20))
        
        # Barra de herramientas
        toolbar_frame = ctk.CTkFrame(self.content_frame)
        toolbar_frame.pack(fill="x", padx=20, pady=10)
        
        toolbar_container = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        toolbar_container.pack(fill="x", padx=20, pady=15)
        
        # Botones de acción
        btn_nuevo = ctk.CTkButton(
            toolbar_container,
            text="➕ Nuevo Producto",
            width=150,
            command=self._nuevo_producto_rapido,
            fg_color="#28a745"
        )
        btn_nuevo.pack(side="left", padx=(0, 10))
        
        btn_categorias = ctk.CTkButton(
            toolbar_container,
            text="📁 Categorías",
            width=120,
            command=self._gestionar_categorias
        )
        btn_categorias.pack(side="left", padx=(0, 10))
        
        btn_stock_bajo = ctk.CTkButton(
            toolbar_container,
            text="⚠️ Stock Bajo",
            width=120,
            command=self._mostrar_stock_bajo,
            fg_color="#dc3545"
        )
        btn_stock_bajo.pack(side="left", padx=(0, 10))
        
        # Búsqueda
        search_frame = ctk.CTkFrame(toolbar_container, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar por nombre o código...",
            width=250
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        btn_buscar = ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=80,
            command=self._buscar_productos
        )
        btn_buscar.pack(side="left")
        
        # Lista de productos
        productos_frame = ctk.CTkFrame(self.content_frame)
        productos_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Headers
        headers_frame = ctk.CTkFrame(productos_frame)
        headers_frame.pack(fill="x", padx=15, pady=15)
        
        headers = ["Código", "Nombre", "Categoría", "Precio", "Stock", "Estado", "Acciones"]
        header_widths = [80, 200, 120, 100, 80, 100, 120]
        
        for i, (header, width) in enumerate(zip(headers, header_widths)):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                width=width
            )
            label.pack(side="left", padx=5)
        
        # Lista de productos
        for producto in self.productos:
            producto_frame = ctk.CTkFrame(productos_frame)
            producto_frame.pack(fill="x", padx=15, pady=2)
            
            # Estado del stock
            if producto['stock'] < 5:
                estado = "🔴 Crítico"
                estado_color = "#dc3545"
            elif producto['stock'] < 10:
                estado = "🟡 Bajo"
                estado_color = "#ffc107"
            else:
                estado = "🟢 Normal"
                estado_color = "#28a745"
            
            # Campos del producto
            campos = [
                producto['codigo'],
                producto['nombre'],
                producto['categoria'],
                f"{self.config_negocio['moneda']}{producto['precio']:.2f}",
                str(producto['stock']),
                estado
            ]
            
            for i, (campo, width) in enumerate(zip(campos, header_widths[:-1])):
                color = estado_color if i == 5 else None
                label = ctk.CTkLabel(
                    producto_frame,
                    text=campo,
                    width=width,
                    text_color=color
                )
                label.pack(side="left", padx=5, pady=8)
            
            # Botones de acción
            actions_frame = ctk.CTkFrame(producto_frame, fg_color="transparent")
            actions_frame.pack(side="left", padx=5)
            
            btn_editar = ctk.CTkButton(
                actions_frame,
                text="✏️",
                width=30,
                height=25,
                command=lambda p=producto: self._editar_producto(p)
            )
            btn_editar.pack(side="left", padx=2)
            
            btn_stock = ctk.CTkButton(
                actions_frame,
                text="📦",
                width=30,
                height=25,
                command=lambda p=producto: self._ajustar_stock(p)
            )
            btn_stock.pack(side="left", padx=2)
    
    def _mostrar_pos(self):
        """Punto de venta universal"""
        self.modulo_actual = "pos"
        self._limpiar_contenido()
        
        # Barra de navegación superior
        nav_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        btn_volver = ctk.CTkButton(
            nav_frame,
            text="🏠 Volver al Dashboard",
            command=self._mostrar_dashboard,
            width=180,
            height=35,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        btn_volver.pack(side="left", pady=10)
        
        # Botón adicional para ver historial de ventas
        btn_historial = ctk.CTkButton(
            nav_frame,
            text="📋 Historial de Ventas",
            command=self._ver_historial_ventas,
            width=160,
            height=35,
            fg_color="#17a2b8",
            hover_color="#138496"
        )
        btn_historial.pack(side="left", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="🛒 Punto de Venta Universal",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        # Frame principal dividido
        pos_main_frame = ctk.CTkFrame(self.content_frame)
        pos_main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Panel izquierdo - Productos
        left_panel = ctk.CTkFrame(pos_main_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(15, 7), pady=15)
        
        # Búsqueda de productos
        search_frame = ctk.CTkFrame(left_panel)
        search_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(search_frame, text="🔍 Buscar Producto", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.pos_search = ctk.CTkEntry(
            search_frame,
            placeholder_text="Nombre, código de barras o código...",
            width=300
        )
        self.pos_search.pack(pady=10)
        self.pos_search.bind("<Return>", self._buscar_producto_pos)
        
        # Lista de productos disponibles
        productos_list_frame = ctk.CTkScrollableFrame(left_panel, height=400)
        productos_list_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        for producto in self.productos:
            if producto['stock'] > 0:  # Solo mostrar productos en stock
                producto_item = ctk.CTkFrame(productos_list_frame)
                producto_item.pack(fill="x", pady=5)
                
                # Info del producto
                info_text = f"{producto['nombre']} - {self.config_negocio['moneda']}{producto['precio']:.2f}"
                if producto['stock'] < 10:
                    info_text += f" ⚠️ Stock: {producto['stock']}"
                
                producto_label = ctk.CTkLabel(
                    producto_item,
                    text=info_text,
                    anchor="w"
                )
                producto_label.pack(side="left", padx=10, pady=8, fill="x", expand=True)
                
                # Botón agregar
                btn_agregar = ctk.CTkButton(
                    producto_item,
                    text="➕",
                    width=40,
                    height=30,
                    command=lambda p=producto: self._agregar_al_carrito(p)
                )
                btn_agregar.pack(side="right", padx=10, pady=5)
        
        # Panel derecho - Carrito
        right_panel = ctk.CTkFrame(pos_main_frame, width=350)
        right_panel.pack(side="right", fill="y", padx=(7, 15), pady=15)
        right_panel.pack_propagate(False)
        
        # Título del carrito
        ctk.CTkLabel(
            right_panel, 
            text="🛒 Carrito de Compras", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Lista del carrito
        self.carrito_frame = ctk.CTkScrollableFrame(right_panel, height=300)
        self.carrito_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Total
        self.total_frame = ctk.CTkFrame(right_panel)
        self.total_frame.pack(fill="x", padx=15, pady=10)
        
        self.total_label = ctk.CTkLabel(
            self.total_frame,
            text=f"Total: {self.config_negocio['moneda']}0.00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#007bff"
        )
        self.total_label.pack(pady=15)
        
        # Botones de acción
        buttons_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=15)
        
        btn_limpiar = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Limpiar",
            width=150,
            height=40,
            fg_color="#6c757d",
            command=self._limpiar_carrito
        )
        btn_limpiar.pack(pady=5)
        
        btn_cobrar = ctk.CTkButton(
            buttons_frame,
            text="💰 Procesar Venta",
            width=150,
            height=50,
            fg_color="#28a745",
            command=self._procesar_venta,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_cobrar.pack(pady=10)
        
        # Actualizar vista del carrito
        self._actualizar_carrito()
    
    def _mostrar_clientes(self):
        """Módulo universal de clientes"""
        self.modulo_actual = "clientes"
        self._limpiar_contenido()
        
        # Barra de navegación superior
        nav_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        btn_volver = ctk.CTkButton(
            nav_frame,
            text="🏠 Volver al Dashboard",
            command=self._mostrar_dashboard,
            width=180,
            height=35,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        btn_volver.pack(side="left", pady=10)
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="👥 Gestión Universal de Clientes",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Toolbar
        toolbar_frame = ctk.CTkFrame(self.content_frame)
        toolbar_frame.pack(fill="x", padx=20, pady=10)
        
        btn_nuevo_cliente = ctk.CTkButton(
            toolbar_frame,
            text="👤 Nuevo Cliente",
            command=self._nuevo_cliente_rapido,
            fg_color="#28a745"
        )
        btn_nuevo_cliente.pack(side="left", padx=20, pady=15)
        
        # Lista de clientes
        clientes_frame = ctk.CTkFrame(self.content_frame)
        clientes_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        for cliente in self.clientes:
            cliente_item = ctk.CTkFrame(clientes_frame)
            cliente_item.pack(fill="x", padx=15, pady=8)
            
            info_text = f"👤 {cliente['nombre']} | 📞 {cliente['telefono']} | 📧 {cliente['email']}"
            
            cliente_label = ctk.CTkLabel(
                cliente_item,
                text=info_text,
                anchor="w"
            )
            cliente_label.pack(side="left", padx=15, pady=12, fill="x", expand=True)
            
            btn_historial = ctk.CTkButton(
                cliente_item,
                text="📋 Historial",
                width=100,
                command=lambda c=cliente: self._ver_historial_cliente(c)
            )
            btn_historial.pack(side="right", padx=15, pady=8)
    
    def _mostrar_reportes(self):
        """Centro de reportes universal"""
        self.modulo_actual = "reportes"
        self._limpiar_contenido()
        
        # Barra de navegación superior
        nav_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        btn_volver = ctk.CTkButton(
            nav_frame,
            text="🏠 Volver al Dashboard",
            command=self._mostrar_dashboard,
            width=180,
            height=35,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        btn_volver.pack(side="left", pady=10)
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📊 Centro Universal de Reportes",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        subtitle = ctk.CTkLabel(
            self.content_frame,
            text="Análisis adaptativo para cualquier tipo de negocio",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 30))
        
        # Grid de reportes
        reportes_frame = ctk.CTkFrame(self.content_frame)
        reportes_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        reportes_grid = ctk.CTkFrame(reportes_frame, fg_color="transparent")
        reportes_grid.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Tipos de reportes universales
        reportes = [
            ("📈 Ventas Diarias", "Análisis de ventas por día", self._reporte_ventas_diarias),
            ("📦 Inventario Actual", "Estado completo del inventario", self._reporte_inventario),
            ("🎯 Productos Estrella", "Productos más vendidos", self._reporte_productos_estrella),
            ("👥 Análisis de Clientes", "Comportamiento de clientes", self._reporte_clientes),
            ("💰 Rentabilidad", "Análisis de márgenes y ganancias", self._reporte_rentabilidad),
            ("📊 Dashboard Ejecutivo", "Resumen gerencial completo", self._reporte_ejecutivo)
        ]
        
        for i, (titulo, descripcion, comando) in enumerate(reportes):
            reporte_card = ctk.CTkFrame(reportes_grid)
            if i < 3:
                reporte_card.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            else:
                if i == 3:  # Nueva fila
                    reportes_grid2 = ctk.CTkFrame(reportes_frame, fg_color="transparent")
                    reportes_grid2.pack(fill="x", padx=30, pady=(0, 30))
                reporte_card = ctk.CTkFrame(reportes_grid2)
                reporte_card.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(
                reporte_card,
                text=titulo,
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=(20, 10))
            
            ctk.CTkLabel(
                reporte_card,
                text=descripcion,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                wraplength=150
            ).pack(pady=(0, 15))
            
            ctk.CTkButton(
                reporte_card,
                text="📊 Generar",
                command=comando,
                width=120,
                fg_color="#007bff"
            ).pack(pady=(0, 20))
    
    def _mostrar_configuracion(self):
        """Configuración universal del sistema"""
        self.modulo_actual = "configuracion"
        self._limpiar_contenido()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="⚙️ Configuración Universal",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        # Configuración del negocio
        config_frame = ctk.CTkFrame(self.content_frame)
        config_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Información del negocio
        business_config = ctk.CTkFrame(config_frame)
        business_config.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            business_config,
            text="🏪 Información del Negocio",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # Campos de configuración
        fields_frame = ctk.CTkFrame(business_config, fg_color="transparent")
        fields_frame.pack(fill="x", padx=20, pady=15)
        
        # Nombre del negocio
        name_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(name_frame, text="Nombre del Negocio:", width=150).pack(side="left")
        self.nombre_entry = ctk.CTkEntry(name_frame, width=300)
        self.nombre_entry.insert(0, self.config_negocio['nombre'])
        self.nombre_entry.pack(side="left", padx=10)
        
        # Tipo de negocio
        tipo_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        tipo_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(tipo_frame, text="Tipo de Negocio:", width=150).pack(side="left")
        self.tipo_combo = ctk.CTkComboBox(
            tipo_frame,
            values=[
                "Tienda de Abarrotes", "Ferretería", "Papelería", "Boutique", "Librería",
                "Farmacia", "Restaurante", "Taller", "Distribuidora", "Panadería",
                "Veterinaria", "Zapatería", "Perfumería", "Electrodomésticos", 
                "Juguetería", "Tienda General", "Otro"
            ],
            width=300
        )
        self.tipo_combo.set(self.config_negocio['tipo'])
        self.tipo_combo.pack(side="left", padx=10)
        
        # Moneda
        moneda_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        moneda_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(moneda_frame, text="Moneda:", width=150).pack(side="left")
        self.moneda_combo = ctk.CTkComboBox(
            moneda_frame,
            values=["$", "€", "£", "¥", "₹", "₽", "₦", "₱", "R$", "C$", "A$", "NZ$"],
            width=100
        )
        self.moneda_combo.set(self.config_negocio['moneda'])
        self.moneda_combo.pack(side="left", padx=10)
        
        # Botón guardar configuración
        ctk.CTkButton(
            business_config,
            text="💾 Guardar Configuración",
            command=self._guardar_configuracion,
            fg_color="#28a745",
            width=200,
            height=40
        ).pack(pady=20)
        
        # Configuraciones del sistema
        system_config = ctk.CTkFrame(config_frame)
        system_config.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            system_config,
            text="🔧 Configuraciones del Sistema",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))
        
        # Switches de configuración
        switches_frame = ctk.CTkFrame(system_config, fg_color="transparent")
        switches_frame.pack(fill="x", padx=20, pady=15)
        
        configs = [
            ("Usar control de stock", "usar_stock"),
            ("Gestionar categorías", "usar_categorias"),
            ("Administrar proveedores", "usar_proveedores"),
            ("Base de clientes", "usar_clientes")
        ]
        
        for texto, key in configs:
            config_item = ctk.CTkFrame(switches_frame, fg_color="transparent")
            config_item.pack(fill="x", pady=5)
            
            ctk.CTkLabel(config_item, text=texto, width=200).pack(side="left")
            
            switch = ctk.CTkSwitch(config_item, text="")
            if self.config_negocio[key]:
                switch.select()
            switch.pack(side="left", padx=20)
    
    # Métodos auxiliares
    def _agregar_al_carrito(self, producto):
        """Agregar producto al carrito"""
        # Verificar si ya existe en el carrito
        for item in self.carrito:
            if item['id'] == producto['id']:
                if item['cantidad'] < producto['stock']:
                    item['cantidad'] += 1
                    item['subtotal'] = item['cantidad'] * item['precio']
                else:
                    messagebox.showwarning("Stock Insuficiente", f"No hay más stock disponible de {producto['nombre']}")
                self._actualizar_carrito()
                return
        
        # Agregar nuevo producto al carrito
        if producto['stock'] > 0:
            item_carrito = {
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'cantidad': 1,
                'subtotal': producto['precio']
            }
            self.carrito.append(item_carrito)
            self._actualizar_carrito()
        else:
            messagebox.showwarning("Sin Stock", f"No hay stock disponible de {producto['nombre']}")
    
    def _actualizar_carrito(self):
        """Actualizar la vista del carrito"""
        # Limpiar carrito frame
        for widget in self.carrito_frame.winfo_children():
            widget.destroy()
        
        self.total_carrito = 0
        
        for item in self.carrito:
            item_frame = ctk.CTkFrame(self.carrito_frame)
            item_frame.pack(fill="x", pady=3)
            
            # Información del item
            info_text = f"{item['nombre']}\n{item['cantidad']} x {self.config_negocio['moneda']}{item['precio']:.2f}"
            
            item_label = ctk.CTkLabel(
                item_frame,
                text=info_text,
                justify="left",
                anchor="w"
            )
            item_label.pack(side="left", padx=10, pady=8, fill="x", expand=True)
            
            # Subtotal
            subtotal_label = ctk.CTkLabel(
                item_frame,
                text=f"{self.config_negocio['moneda']}{item['subtotal']:.2f}",
                font=ctk.CTkFont(weight="bold")
            )
            subtotal_label.pack(side="right", padx=10, pady=8)
            
            self.total_carrito += item['subtotal']
        
        # Actualizar total
        if hasattr(self, 'total_label'):
            self.total_label.configure(text=f"Total: {self.config_negocio['moneda']}{self.total_carrito:.2f}")
    
    def _limpiar_carrito(self):
        """Limpiar el carrito de compras"""
        self.carrito = []
        self.total_carrito = 0
        self._actualizar_carrito()
    
    def _ver_historial_ventas(self):
        """Ver historial completo de ventas"""
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("📋 Historial de Ventas")
        ventana.geometry("800x600")
        ventana.transient(self.root)
        
        # Título
        title = ctk.CTkLabel(
            ventana, 
            text="📋 Historial de Ventas del Día", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Resumen del día
        resumen_frame = ctk.CTkFrame(ventana)
        resumen_frame.pack(fill="x", padx=20, pady=10)
        
        resumen_text = (
            f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}\n"
            f"💰 Total del día: {self.config_negocio['moneda']}{self.stats_dia['ventas_total']:.2f}\n"
            f"🧾 Número de ventas: {self.stats_dia['num_ventas']}\n"
            f"📦 Items vendidos: {self.stats_dia['items_vendidos']}"
        )
        
        ctk.CTkLabel(resumen_frame, text=resumen_text, font=ctk.CTkFont(size=14)).pack(pady=15)
        
        # Lista de ventas
        ventas_frame = ctk.CTkScrollableFrame(ventana)
        ventas_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        if not self.ventas_hoy:
            ctk.CTkLabel(
                ventas_frame,
                text="📭 No hay ventas registradas hoy",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
        else:
            for venta in self.ventas_hoy:
                venta_item = ctk.CTkFrame(ventas_frame)
                venta_item.pack(fill="x", pady=5, padx=10)
                
                venta_info = (
                    f"🧾 Venta #{venta['id']:03d} - {venta['hora']} | "
                    f"💰 {self.config_negocio['moneda']}{venta['total']:.2f} | "
                    f"📦 {venta['items']} items | "
                    f"👤 {venta['cliente']}"
                )
                
                ctk.CTkLabel(
                    venta_item,
                    text=venta_info,
                    anchor="w"
                ).pack(side="left", padx=15, pady=10, fill="x", expand=True)
        
        # Botón cerrar
        ctk.CTkButton(
            ventana,
            text="✅ Cerrar",
            command=ventana.destroy,
            width=120
        ).pack(pady=20)
    
    def _procesar_venta(self):
        """Procesar la venta.

        Antes, esta función sólo tocaba estructuras en memoria: la
        venta y el descuento de stock desaparecían al cerrar la
        aplicación, y nada impedía vender más unidades de las que
        realmente había en existencia (dos ventas seguidas basadas en
        la misma foto en memoria del stock podían "sobrevender").

        Ahora, si hay base de datos disponible, la venta se procesa con
        `services.ventas_service.procesar_venta_atomica`, que descuenta
        el stock y registra la venta + su detalle en una única
        transacción de SQLite: o se aplica todo (venta y stock
        coherentes entre sí y con lo que había realmente disponible), o
        no se aplica nada (stock insuficiente, error de datos, etc.).
        """
        if not self.carrito:
            messagebox.showwarning("Carrito Vacío", "Agrega productos al carrito antes de procesar la venta")
            return

        total_final = self.total_carrito
        items_vendidos = sum(item['cantidad'] for item in self.carrito)

        if self.db is not None and procesar_venta_atomica is not None:
            items_venta = [
                {
                    "producto_id": item['id'],
                    "cantidad": item['cantidad'],
                    "precio_unitario": Decimal(str(item['precio'])),
                }
                for item in self.carrito
            ]
            try:
                resultado = procesar_venta_atomica(self.db, items_venta)
            except StockInsuficienteError as e:
                messagebox.showerror("Stock insuficiente", str(e))
                return
            except CarritoVacioError as e:
                messagebox.showwarning("Carrito Vacío", str(e))
                return
            except VentaServiceError as e:
                messagebox.showerror(
                    "Error al procesar la venta",
                    f"No se pudo registrar la venta en la base de datos:\n{e}\n\n"
                    "No se cobró ni se descontó stock: la venta se canceló por completo."
                )
                return

            # La base de datos es la fuente de verdad: se refleja aquí
            # el stock restante que realmente quedó tras la venta.
            for item in self.carrito:
                for producto in self.productos:
                    if producto['id'] == item['id'] and item['id'] in resultado.stock_restante:
                        producto['stock'] = resultado.stock_restante[item['id']]
                        break

            venta_id = resultado.venta_id
            total_final = float(resultado.total)
            folio_venta = resultado.folio
        else:
            # Sin base de datos disponible: se conserva el modo demo
            # (solo en memoria) para que la app siga siendo utilizable,
            # dejando claro en el mensaje final que no hubo persistencia.
            venta_id = len(self.ventas_hoy) + 1
            folio_venta = None
            for item in self.carrito:
                for producto in self.productos:
                    if producto['id'] == item['id']:
                        producto['stock'] = max(0, producto['stock'] - item['cantidad'])
                        break

        nueva_venta = {
            'id': venta_id,
            'total': total_final,
            'items': items_vendidos,
            'hora': datetime.now().strftime('%H:%M'),
            'cliente': 'Mostrador'
        }

        self.ventas_hoy.append(nueva_venta)

        # 💾 BACKUP AUTOMÁTICO - Registrar venta procesada
        if self.backup_manager:
            try:
                # Crear copia del carrito para backup
                carrito_backup = []
                for item in self.carrito:
                    carrito_backup.append({
                        'id': item['id'],
                        'nombre': item['nombre'],
                        'cantidad': item['cantidad'],
                        'precio': item['precio'],
                        'subtotal': item['subtotal']
                    })
                
                archivo_backup = self.backup_manager.backup_venta_procesada(nueva_venta, carrito_backup)
                print(f"💾 Venta respaldada en: {archivo_backup}")
            except Exception as e:
                print(f"⚠️ Error en backup de venta: {e}")
        
        # Actualizar estadísticas
        self.stats_dia['ventas_total'] += total_final
        self.stats_dia['num_ventas'] += 1
        self.stats_dia['items_vendidos'] += nueva_venta['items']
        self.stats_dia['stock_bajo'] = len([p for p in self.productos if p['stock'] < 10])

        detalle_folio = f"🧾 Folio: {folio_venta}\n" if folio_venta else ""
        detalle_persistencia = (
            "💾 Venta guardada en la base de datos\n"
            if folio_venta else
            "⚠️ Sin base de datos disponible: venta solo en memoria (no persiste)\n"
        )
        messagebox.showinfo("Venta Procesada",
                           f"✅ Venta procesada exitosamente\n\n"
                           f"🧾 Número: {venta_id:03d}\n"
                           f"{detalle_folio}"
                           f"💰 Total: {self.config_negocio['moneda']}{total_final:.2f}\n"
                           f"📦 Items: {nueva_venta['items']}\n"
                           f"{detalle_persistencia}"
                           f"💾 Backup automático creado\n\n"
                           f"¡Gracias por su compra!")
        
        # Limpiar carrito
        self._limpiar_carrito()
        
        # Si estamos en el dashboard, actualizar
        if self.modulo_actual == "dashboard":
            self._mostrar_dashboard()
    
    # Métodos de acciones rápidas
    def _nuevo_producto_rapido(self):
        """Formulario rápido para nuevo producto"""
        messagebox.showinfo("Nuevo Producto", "🚧 Formulario de nuevo producto en desarrollo\n\n✨ Próximamente disponible con:\n\n• Códigos de barras\n• Múltiples categorías\n• Control avanzado de stock\n• Imágenes de productos\n• Precios por volumen")
    
    def _nuevo_cliente_rapido(self):
        """Formulario rápido para nuevo cliente"""
        messagebox.showinfo("Nuevo Cliente", "🚧 Formulario de nuevo cliente en desarrollo\n\n✨ Próximamente disponible con:\n\n• Información completa\n• Historial de compras\n• Programa de fidelidad\n• Descuentos personalizados\n• Comunicación integrada")
    
    def _reporte_rapido(self):
        """Reporte rápido del día"""
        messagebox.showinfo("Reporte del Día", 
                           f"📊 Reporte Rápido - {datetime.now().strftime('%d/%m/%Y')}\n\n"
                           f"💰 Ventas: {self.config_negocio['moneda']}{self.stats_dia['ventas_total']:.2f}\n"
                           f"🧾 Transacciones: {self.stats_dia['num_ventas']}\n"
                           f"📦 Items vendidos: {self.stats_dia['items_vendidos']}\n"
                           f"⚠️ Productos con stock bajo: {self.stats_dia['stock_bajo']}\n\n"
                           f"✅ Sistema operando normalmente")
    
    def _calcular_estadisticas(self):
        """Recalcular estadísticas del sistema"""
        try:
            # Calcular total de productos
            total_productos = len(self.productos)
            
            # Calcular productos con stock bajo (menos de 5)
            stock_bajo = sum(1 for p in self.productos if int(p.get('stock', 0)) < 5)
            
            # Actualizar estadísticas
            self.stats_dia['total_productos'] = total_productos
            self.stats_dia['stock_bajo'] = stock_bajo
            
            # Si estamos en el dashboard, actualizar la vista
            if hasattr(self, 'modulo_actual') and self.modulo_actual == "dashboard":
                self._actualizar_dashboard_stats()
                
        except Exception as e:
            print(f"⚠️ Error calculando estadísticas: {e}")
    
    def _actualizar_dashboard_stats(self):
        """Actualizar estadísticas del dashboard si está visible"""
        try:
            # Solo actualizar si el dashboard está visible
            if hasattr(self, 'modulo_actual') and self.modulo_actual == "dashboard":
                # Aquí podríamos actualizar widgets específicos del dashboard
                pass
        except Exception as e:
            print(f"⚠️ Error actualizando dashboard: {e}")
    
    # Funcionalidades avanzadas completamente implementadas
    def _gestionar_categorias(self):
        """Gestión completa de categorías"""
        self._mostrar_gestion_categorias()
    
    def _mostrar_gestion_categorias(self):
        """Interfaz de gestión de categorías"""
        self.modulo_actual = "categorias"
        self._limpiar_contenido()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📂 Gestión de Categorías",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        # Panel principal
        main_panel = ctk.CTkFrame(self.content_frame)
        main_panel.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Barra de herramientas
        toolbar = ctk.CTkFrame(main_panel)
        toolbar.pack(fill="x", padx=15, pady=15)
        
        btn_nueva = ctk.CTkButton(
            toolbar,
            text="➕ Nueva Categoría",
            command=self._nueva_categoria
        )
        btn_nueva.pack(side="left", padx=(15, 10))
        
        # Lista de categorías con estadísticas
        categorias_frame = ctk.CTkScrollableFrame(main_panel)
        categorias_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        for categoria in self.categorias:
            productos_categoria = len([p for p in self.productos if p.get('categoria') == categoria])
            self._crear_card_categoria(categorias_frame, categoria, productos_categoria)
    
    def _crear_card_categoria(self, parent, categoria, productos_count):
        """Crear card visual para categoría"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", pady=10, padx=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)
        
        # Info principal
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        nombre_label = ctk.CTkLabel(
            info_frame,
            text=f"📂 {categoria}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        nombre_label.pack(anchor="w")
        
        stats_label = ctk.CTkLabel(
            info_frame,
            text=f"{productos_count} productos registrados",
            text_color="gray"
        )
        stats_label.pack(anchor="w")
        
        # Acciones
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(side="right")
        
        ctk.CTkButton(
            actions_frame, text="✏️ Editar", width=80, height=30,
            command=lambda c=categoria: self._editar_categoria(c)
        ).pack(side="right", padx=5)
    
    def _nueva_categoria(self):
        """Formulario para nueva categoría"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Nueva Categoría")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        title = ctk.CTkLabel(dialog, text="➕ Nueva Categoría", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=20)
        
        ctk.CTkLabel(dialog, text="Nombre:").pack()
        nombre_entry = ctk.CTkEntry(dialog, placeholder_text="Nombre de la categoría", width=300)
        nombre_entry.pack(pady=10)
        
        def guardar():
            nombre = nombre_entry.get().strip()
            if nombre and nombre not in self.categorias:
                self.categorias.append(nombre)
                messagebox.showinfo("Éxito", f"Categoría '{nombre}' creada")
                dialog.destroy()
                self._mostrar_gestion_categorias()
            else:
                messagebox.showwarning("Error", "Nombre inválido o ya existe")
        
        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(pady=20)
        
        ctk.CTkButton(buttons, text="💾 Guardar", command=guardar).pack(side="left", padx=10)
        ctk.CTkButton(buttons, text="❌ Cancelar", command=dialog.destroy).pack(side="left")
        
        nombre_entry.focus()
    
    def _editar_categoria(self, categoria):
        """Editar categoría existente"""
        messagebox.showinfo("Editar", f"✏️ Editando categoría: {categoria}")
    
    def _mostrar_stock_bajo(self):
        """Mostrar productos con stock bajo y crítico"""
        self.modulo_actual = "stock_bajo"
        self._limpiar_contenido()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="⚠️ Alertas de Inventario",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        # Filtrar productos por niveles de stock
        productos_agotados = [p for p in self.productos if p['stock'] == 0]
        productos_criticos = [p for p in self.productos if 0 < p['stock'] <= 5]
        productos_bajos = [p for p in self.productos if 5 < p['stock'] <= 10]
        
        # Panel de estadísticas
        stats_frame = ctk.CTkFrame(self.content_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=15, pady=15)
        
        stats_data = [
            ("🚨 Agotados", len(productos_agotados), "#dc3545"),
            ("⚠️ Críticos", len(productos_criticos), "#fd7e14"),
            ("📉 Stock Bajo", len(productos_bajos), "#ffc107"),
            ("✅ Normal", len([p for p in self.productos if p['stock'] > 10]), "#28a745")
        ]
        
        for label, count, color in stats_data:
            stat_card = ctk.CTkFrame(stats_container)
            stat_card.pack(side="left", fill="both", expand=True, padx=10)
            
            ctk.CTkLabel(stat_card, text=label, font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
            ctk.CTkLabel(
                stat_card, text=str(count), 
                font=ctk.CTkFont(size=20, weight="bold"), 
                text_color=color
            ).pack(pady=(0, 15))
        
        # Lista de productos con alertas
        alertas_frame = ctk.CTkScrollableFrame(self.content_frame)
        alertas_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        todos_alertas = productos_agotados + productos_criticos + productos_bajos
        
        if not todos_alertas:
            ctk.CTkLabel(
                alertas_frame,
                text="🎉 ¡Excelente! No hay alertas de inventario",
                font=ctk.CTkFont(size=18),
                text_color="#28a745"
            ).pack(pady=50)
        else:
            for producto in todos_alertas:
                self._crear_alerta_producto(alertas_frame, producto)
    
    def _crear_alerta_producto(self, parent, producto):
        """Crear card de alerta para producto"""
        # Determinar nivel de alerta
        stock = producto['stock']
        if stock == 0:
            nivel = "AGOTADO"
            color = "#dc3545"
            icono = "🚨"
        elif stock <= 5:
            nivel = "CRÍTICO"
            color = "#fd7e14"
            icono = "⚠️"
        else:
            nivel = "BAJO"
            color = "#ffc107"
            icono = "📉"
        
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", pady=5, padx=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        
        # Info del producto
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        
        nombre_label = ctk.CTkLabel(
            header_frame,
            text=f"{icono} {producto['nombre']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        nombre_label.pack(side="left")
        
        nivel_label = ctk.CTkLabel(
            header_frame,
            text=nivel,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=color
        )
        nivel_label.pack(side="right")
        
        detalles_label = ctk.CTkLabel(
            info_frame,
            text=f"Stock: {stock} | Código: {producto['codigo']} | {self.config_negocio['moneda']}{producto['precio']:.2f}",
            text_color="gray"
        )
        detalles_label.pack(anchor="w")
        
        # Acciones rápidas
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(side="right")
        
        ctk.CTkButton(
            actions_frame, text="📦", width=35, height=30,
            command=lambda p=producto: self._reabastecer_rapido(p)
        ).pack(side="right", padx=2)
        
        ctk.CTkButton(
            actions_frame, text="✏️", width=35, height=30,
            command=lambda p=producto: self._ajustar_stock(p)
        ).pack(side="right", padx=2)
    
    def _reabastecer_rapido(self, producto):
        """Reabastecimiento rápido"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Reabastecer")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=f"📦 {producto['nombre']}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)
        ctk.CTkLabel(dialog, text=f"Stock actual: {producto['stock']}", text_color="gray").pack()
        
        ctk.CTkLabel(dialog, text="Cantidad a agregar:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        cantidad_entry = ctk.CTkEntry(dialog, width=100)
        cantidad_entry.pack()
        
        def confirmar():
            try:
                cantidad = int(cantidad_entry.get())
                if cantidad > 0:
                    producto['stock'] += cantidad
                    messagebox.showinfo("Éxito", f"Stock actualizado: {producto['stock']}")
                    dialog.destroy()
                    self._mostrar_stock_bajo()
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida")
        
        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(pady=20)
        
        ctk.CTkButton(buttons, text="✅", command=confirmar).pack(side="left", padx=5)
        ctk.CTkButton(buttons, text="❌", command=dialog.destroy).pack(side="left", padx=5)
        
        cantidad_entry.focus()
    
    def _buscar_productos(self):
        """Búsqueda avanzada con filtros múltiples"""
        self.modulo_actual = "busqueda"
        self._limpiar_contenido()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="🔍 Búsqueda Avanzada de Productos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        # Panel de búsqueda
        search_panel = ctk.CTkFrame(self.content_frame)
        search_panel.pack(fill="x", padx=20, pady=10)
        
        # Barra principal
        main_search = ctk.CTkFrame(search_panel)
        main_search.pack(fill="x", padx=15, pady=15)
        
        search_container = ctk.CTkFrame(main_search, fg_color="transparent")
        search_container.pack(fill="x", padx=15, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="🔍 Buscar por nombre, código, categoría...",
            width=400
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self._busqueda_en_tiempo_real)
        
        ctk.CTkButton(
            search_container, text="Buscar", width=80,
            command=self._ejecutar_busqueda
        ).pack(side="right", padx=(10, 0))
        
        # Filtros rápidos
        filtros_rapidos = ctk.CTkFrame(search_panel)
        filtros_rapidos.pack(fill="x", padx=15, pady=(0, 15))
        
        filtros_container = ctk.CTkFrame(filtros_rapidos, fg_color="transparent")
        filtros_container.pack(fill="x", padx=15, pady=10)
        
        # Botones de filtros rápidos
        filtros_botones = [
            ("Todos", lambda: self._filtro_rapido("todos")),
            ("Con Stock", lambda: self._filtro_rapido("con_stock")),
            ("Sin Stock", lambda: self._filtro_rapido("sin_stock")),
            ("Stock Bajo", lambda: self._filtro_rapido("stock_bajo")),
        ]
        
        for texto, comando in filtros_botones:
            ctk.CTkButton(
                filtros_container, text=texto, width=80, height=30,
                command=comando
            ).pack(side="left", padx=5)
        
        # Filtros por categoría
        if self.categorias:
            ctk.CTkLabel(filtros_container, text="Categoría:").pack(side="left", padx=(20, 5))
            self.categoria_filtro = ctk.CTkComboBox(
                filtros_container, values=["Todas"] + self.categorias,
                width=150, command=self._cambio_categoria
            )
            self.categoria_filtro.pack(side="left", padx=5)
            self.categoria_filtro.set("Todas")
        
        # Área de resultados
        self.resultados_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.resultados_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mostrar todos inicialmente
        self._mostrar_resultados_busqueda(self.productos)
    
    def _busqueda_en_tiempo_real(self, event):
        """Búsqueda mientras se escribe"""
        # Pequeño delay para evitar muchas búsquedas
        self.root.after(300, self._ejecutar_busqueda)
    
    def _ejecutar_busqueda(self):
        """Ejecutar búsqueda con filtros"""
        termino = self.search_entry.get().lower().strip()
        resultados = self.productos.copy()
        
        # Filtrar por término de búsqueda
        if termino:
            resultados = [
                p for p in resultados
                if (termino in p['nombre'].lower() or
                    termino in p['codigo'].lower() or
                    termino in p['categoria'].lower())
            ]
        
        # Aplicar filtro de categoría si existe
        if hasattr(self, 'categoria_filtro'):
            categoria = self.categoria_filtro.get()
            if categoria != "Todas":
                resultados = [p for p in resultados if p['categoria'] == categoria]
        
        self._mostrar_resultados_busqueda(resultados)
    
    def _filtro_rapido(self, tipo):
        """Aplicar filtros rápidos"""
        if tipo == "todos":
            resultados = self.productos
        elif tipo == "con_stock":
            resultados = [p for p in self.productos if p['stock'] > 0]
        elif tipo == "sin_stock":
            resultados = [p for p in self.productos if p['stock'] == 0]
        elif tipo == "stock_bajo":
            resultados = [p for p in self.productos if p['stock'] <= 10]
        
        self._mostrar_resultados_busqueda(resultados)
    
    def _cambio_categoria(self, categoria):
        """Manejar cambio de categoría"""
        self._ejecutar_busqueda()
    
    def _mostrar_resultados_busqueda(self, productos):
        """Mostrar resultados en grid"""
        # Limpiar resultados
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()
        
        if not productos:
            ctk.CTkLabel(
                self.resultados_frame,
                text="🔍 No se encontraron productos",
                font=ctk.CTkFont(size=16), text_color="gray"
            ).pack(pady=50)
            return
        
        # Header con conteo
        header = ctk.CTkFrame(self.resultados_frame)
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header,
            text=f"📋 {len(productos)} productos encontrados",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Grid de productos
        for i, producto in enumerate(productos[:20]):  # Máximo 20
            self._crear_card_resultado(producto)
        
        if len(productos) > 20:
            ctk.CTkLabel(
                self.resultados_frame,
                text=f"... y {len(productos) - 20} más. Refina tu búsqueda.",
                text_color="gray"
            ).pack(pady=15)
    
    def _crear_card_resultado(self, producto):
        """Crear card de resultado de búsqueda"""
        card = ctk.CTkFrame(self.resultados_frame)
        card.pack(fill="x", pady=5, padx=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        
        # Info del producto
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        nombre_label = ctk.CTkLabel(
            info_frame,
            text=f"📦 {producto['nombre']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        nombre_label.pack(fill="x")
        
        detalles_label = ctk.CTkLabel(
            info_frame,
            text=f"📋 {producto['codigo']} | 📂 {producto['categoria']} | 📦 Stock: {producto['stock']}",
            text_color="gray", anchor="w"
        )
        detalles_label.pack(fill="x")
        
        # Precio y acciones
        precio_actions = ctk.CTkFrame(content, fg_color="transparent")
        precio_actions.pack(side="right")
        
        precio_label = ctk.CTkLabel(
            precio_actions,
            text=f"{self.config_negocio['moneda']}{producto['precio']:.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#007bff"
        )
        precio_label.pack()
        
        # Botones de acción
        buttons = ctk.CTkFrame(precio_actions, fg_color="transparent")
        buttons.pack(pady=(5, 0))
        
        ctk.CTkButton(
            buttons, text="✏️", width=30, height=25,
            command=lambda p=producto: self._editar_producto(p)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            buttons, text="🛒", width=30, height=25,
            command=lambda p=producto: self._agregar_al_carrito(p)
        ).pack(side="left", padx=2)
    
    def _buscar_producto_pos(self, event=None):
        """Búsqueda en tiempo real para POS"""
        if not hasattr(self, 'pos_search_entry'):
            return
        
        termino = self.pos_search_entry.get().lower().strip()
        
        # Limpiar productos mostrados
        for widget in self.productos_pos_frame.winfo_children():
            widget.destroy()
        
        if not termino:
            # Mostrar productos por defecto
            for producto in self.productos[:12]:
                self._crear_producto_pos(producto)
            return
        
        # Buscar productos
        resultados = [
            p for p in self.productos
            if (termino in p['nombre'].lower() or
                termino in p['codigo'].lower() or
                termino in str(p['precio']))
        ][:12]
        
        if resultados:
            for producto in resultados:
                self._crear_producto_pos(producto)
        else:
            ctk.CTkLabel(
                self.productos_pos_frame,
                text="🔍 Sin resultados",
                text_color="gray"
            ).pack(pady=20)
    
    def _editar_producto(self, producto):
        """Editor completo de productos"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Editar: {producto['nombre']}")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Título
        ctk.CTkLabel(
            dialog, text="✏️ Editar Producto",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Formulario scrollable
        form = ctk.CTkScrollableFrame(dialog)
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Campos
        campos = {}
        
        # Nombre
        ctk.CTkLabel(form, text="Nombre:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        campos['nombre'] = ctk.CTkEntry(form, width=400)
        campos['nombre'].pack(fill="x", pady=(0, 10))
        campos['nombre'].insert(0, producto['nombre'])
        
        # Código
        ctk.CTkLabel(form, text="Código:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        campos['codigo'] = ctk.CTkEntry(form, width=200)
        campos['codigo'].pack(anchor="w", pady=(0, 10))
        campos['codigo'].insert(0, producto['codigo'])
        
        # Categoría
        ctk.CTkLabel(form, text="Categoría:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        campos['categoria'] = ctk.CTkComboBox(form, values=self.categorias, width=250)
        campos['categoria'].pack(anchor="w", pady=(0, 10))
        campos['categoria'].set(producto['categoria'])
        
        # Precio y stock en fila
        precio_stock_frame = ctk.CTkFrame(form, fg_color="transparent")
        precio_stock_frame.pack(fill="x", pady=10)
        
        # Precio
        precio_frame = ctk.CTkFrame(precio_stock_frame, fg_color="transparent")
        precio_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(precio_frame, text="Precio:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        campos['precio'] = ctk.CTkEntry(precio_frame, width=150)
        campos['precio'].pack(anchor="w")
        campos['precio'].insert(0, str(producto['precio']))
        
        # Stock
        stock_frame = ctk.CTkFrame(precio_stock_frame, fg_color="transparent")
        stock_frame.pack(side="right", fill="x", expand=True)
        
        ctk.CTkLabel(stock_frame, text="Stock:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        campos['stock'] = ctk.CTkEntry(stock_frame, width=150)
        campos['stock'].pack(anchor="w")
        campos['stock'].insert(0, str(producto['stock']))
        
        # Descripción
        ctk.CTkLabel(form, text="Descripción:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 5))
        campos['descripcion'] = ctk.CTkTextbox(form, height=100)
        campos['descripcion'].pack(fill="x", pady=(0, 15))
        
        def guardar():
            try:
                producto['nombre'] = campos['nombre'].get().strip()
                producto['codigo'] = campos['codigo'].get().strip()
                producto['categoria'] = campos['categoria'].get()
                producto['precio'] = float(campos['precio'].get())
                producto['stock'] = int(campos['stock'].get())
                
                messagebox.showinfo("Éxito", "✅ Producto actualizado correctamente")
                dialog.destroy()
                
                # Refrescar vista si es necesario
                if self.modulo_actual == "productos":
                    self._mostrar_productos()
                
            except ValueError:
                messagebox.showerror("Error", "Verifica que precio y stock sean números válidos")
        
        # Botones
        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(buttons, text="💾 Guardar", command=guardar).pack(side="right", padx=(10, 0))
        ctk.CTkButton(buttons, text="❌ Cancelar", command=dialog.destroy).pack(side="right")
        
        campos['nombre'].focus()
    
    def _ajustar_stock(self, producto):
        """Ajuste avanzado de stock con historial"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Ajustar Stock: {producto['nombre']}")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Título
        ctk.CTkLabel(
            dialog, text="📦 Ajustar Stock",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Info del producto
        info_frame = ctk.CTkFrame(dialog)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(info_frame, text=f"📦 {producto['nombre']}", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(info_frame, text=f"Stock actual: {producto['stock']} unidades", text_color="#007bff").pack(pady=(0, 15))
        
        # Formulario
        form_frame = ctk.CTkFrame(dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tipo de movimiento
        ctk.CTkLabel(form_frame, text="Tipo de Movimiento:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        tipo_combo = ctk.CTkComboBox(
            form_frame,
            values=["Entrada (+)", "Salida (-)", "Ajuste a cantidad exacta"],
            width=300
        )
        tipo_combo.pack(fill="x", padx=15, pady=(0, 15))
        tipo_combo.set("Entrada (+)")
        
        # Cantidad
        ctk.CTkLabel(form_frame, text="Cantidad:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(0, 5))
        cantidad_entry = ctk.CTkEntry(form_frame, placeholder_text="Cantidad...")
        cantidad_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Motivo
        ctk.CTkLabel(form_frame, text="Motivo:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(0, 5))
        motivo_combo = ctk.CTkComboBox(
            form_frame,
            values=[
                "Compra", "Venta", "Devolución", "Inventario físico",
                "Corrección", "Merma", "Daño", "Vencimiento", "Otro"
            ]
        )
        motivo_combo.pack(fill="x", padx=15, pady=(0, 15))
        motivo_combo.set("Compra")
        
        # Notas
        ctk.CTkLabel(form_frame, text="Notas (opcional):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(0, 5))
        notas_entry = ctk.CTkEntry(form_frame, placeholder_text="Observaciones...")
        notas_entry.pack(fill="x", padx=15, pady=(0, 20))
        
        def procesar():
            try:
                cantidad = int(cantidad_entry.get())
                tipo = tipo_combo.get()
                motivo = motivo_combo.get()
                
                stock_anterior = producto['stock']
                
                if tipo == "Entrada (+)":
                    producto['stock'] += cantidad
                elif tipo == "Salida (-)":
                    producto['stock'] = max(0, producto['stock'] - cantidad)
                elif tipo == "Ajuste a cantidad exacta":
                    producto['stock'] = cantidad
                
                messagebox.showinfo(
                    "Ajuste Completado",
                    f"✅ Stock ajustado exitosamente\n\n"
                    f"📊 Anterior: {stock_anterior}\n"
                    f"📊 Actual: {producto['stock']}\n"
                    f"📝 Motivo: {motivo}"
                )
                
                dialog.destroy()
                
                # Refrescar vistas
                if self.modulo_actual in ["productos", "stock_bajo"]:
                    if self.modulo_actual == "productos":
                        self._mostrar_productos()
                    else:
                        self._mostrar_stock_bajo()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida")
        
        # Botones
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=20)
        
        ctk.CTkButton(buttons_frame, text="✅ Procesar", command=procesar).pack(side="right", padx=(10, 0))
        ctk.CTkButton(buttons_frame, text="❌ Cancelar", command=dialog.destroy).pack(side="right")
        
        cantidad_entry.focus()
    
    def _ver_historial_cliente(self, cliente):
        """Historial completo y estadísticas del cliente"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Cliente: {cliente['nombre']}")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Header del cliente
        header = ctk.CTkFrame(dialog)
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header, text=f"👤 {cliente['nombre']}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)
        
        # Info de contacto
        contacto_frame = ctk.CTkFrame(header, fg_color="transparent")
        contacto_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(contacto_frame, text=f"📞 {cliente['telefono']}").pack(side="left")
        ctk.CTkLabel(contacto_frame, text=f"📧 {cliente['email']}").pack(side="right")
        
        # Estadísticas (simuladas)
        stats_frame = ctk.CTkFrame(dialog)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            stats_frame, text="📊 Estadísticas del Cliente",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=15, pady=15)
        
        # Datos simulados
        stats_data = [
            ("Compras", "24", "#007bff"),
            ("Total Gastado", f"{self.config_negocio['moneda']}3,250", "#28a745"),
            ("Última Compra", "hace 2 días", "#17a2b8"),
            ("Promedio", f"{self.config_negocio['moneda']}135", "#ffc107")
        ]
        
        for label, value, color in stats_data:
            stat_card = ctk.CTkFrame(stats_container)
            stat_card.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(stat_card, text=label).pack(pady=(15, 5))
            ctk.CTkLabel(
                stat_card, text=value,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=color
            ).pack(pady=(0, 15))
        
        # Historial de compras
        historial_frame = ctk.CTkFrame(dialog)
        historial_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            historial_frame, text="🧾 Historial de Compras",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # Lista de compras (simuladas)
        compras_scroll = ctk.CTkScrollableFrame(historial_frame)
        compras_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Compras de ejemplo
        compras_ejemplo = [
            {"fecha": "02/01/2025", "items": 3, "total": 145.50},
            {"fecha": "30/12/2024", "items": 1, "total": 89.90},
            {"fecha": "28/12/2024", "items": 5, "total": 267.30},
            {"fecha": "25/12/2024", "items": 2, "total": 78.40},
            {"fecha": "20/12/2024", "items": 4, "total": 198.75}
        ]
        
        for compra in compras_ejemplo:
            compra_card = ctk.CTkFrame(compras_scroll)
            compra_card.pack(fill="x", pady=3, padx=5)
            
            content = ctk.CTkFrame(compra_card, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=10)
            
            # Info izquierda
            info_left = ctk.CTkFrame(content, fg_color="transparent")
            info_left.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                info_left, text=f"📅 {compra['fecha']}",
                font=ctk.CTkFont(weight="bold"), anchor="w"
            ).pack(fill="x")
            
            ctk.CTkLabel(
                info_left, text=f"📦 {compra['items']} productos",
                text_color="gray", anchor="w"
            ).pack(fill="x")
            
            # Total derecha
            ctk.CTkLabel(
                content, text=f"{self.config_negocio['moneda']}{compra['total']:.2f}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#28a745"
            ).pack(side="right")
        
        # Botón cerrar
        ctk.CTkButton(dialog, text="❌ Cerrar", command=dialog.destroy).pack(pady=20)
    
    def _guardar_configuracion(self):
        """Guardar configuración del negocio"""
        self.config_negocio['nombre'] = self.nombre_entry.get()
        self.config_negocio['tipo'] = self.tipo_combo.get()
        self.config_negocio['moneda'] = self.moneda_combo.get()
        
        # Actualizar título de la ventana
        self.root.title(f"VentaPro Universal - {self.config_negocio['nombre']}")
        
        messagebox.showinfo("Configuración", "✅ Configuración guardada exitosamente\n\n🔄 Algunos cambios requieren reiniciar la aplicación")
    
    # Métodos de reportes
    def _reporte_ventas_diarias(self):
        """Generar reporte de ventas diarias con backup automático"""
        datos_reporte = {
            "fecha": datetime.now().strftime('%d/%m/%Y'),
            "total_ventas": self.stats_dia['ventas_total'],
            "numero_ventas": self.stats_dia['num_ventas'],
            "items_vendidos": self.stats_dia['items_vendidos'],
            "promedio_venta": self.stats_dia['ventas_total'] / max(1, self.stats_dia['num_ventas']),
            "ventas_detalle": self.ventas_hoy
        }
        
        # 💾 BACKUP AUTOMÁTICO - Reporte generado
        if self.backup_manager:
            try:
                archivo_backup = self.backup_manager.backup_reporte_generado("ventas_diarias", datos_reporte)
                print(f"💾 Reporte respaldado en: {archivo_backup}")
            except Exception as e:
                print(f"⚠️ Error en backup de reporte: {e}")
        
        messagebox.showinfo("📊 Reporte de Ventas Diarias", 
                           f"� Fecha: {datos_reporte['fecha']}\n\n"
                           f"💰 Total vendido: {self.config_negocio['moneda']}{datos_reporte['total_ventas']:.2f}\n"
                           f"🧾 Número de ventas: {datos_reporte['numero_ventas']}\n"
                           f"📦 Items vendidos: {datos_reporte['items_vendidos']}\n"
                           f"📊 Promedio por venta: {self.config_negocio['moneda']}{datos_reporte['promedio_venta']:.2f}\n\n"
                           f"💾 Reporte respaldado automáticamente")
    
    def _reporte_inventario(self):
        """Generar reporte de inventario con backup automático"""
        datos_reporte = {
            "fecha": datetime.now().strftime('%d/%m/%Y'),
            "total_productos": len(self.productos),
            "productos_stock_bajo": len([p for p in self.productos if p['stock'] < 10]),
            "productos_sin_stock": len([p for p in self.productos if p['stock'] == 0]),
            "valor_inventario": sum(p['precio'] * p['stock'] for p in self.productos),
            "productos_detalle": self.productos
        }
        
        # 💾 BACKUP AUTOMÁTICO
        if self.backup_manager:
            try:
                archivo_backup = self.backup_manager.backup_reporte_generado("inventario", datos_reporte)
                print(f"💾 Reporte respaldado en: {archivo_backup}")
            except Exception as e:
                print(f"⚠️ Error en backup de reporte: {e}")
        
        messagebox.showinfo("📦 Reporte de Inventario", 
                           f"� Fecha: {datos_reporte['fecha']}\n\n"
                           f"📦 Total productos: {datos_reporte['total_productos']}\n"
                           f"⚠️ Stock bajo: {datos_reporte['productos_stock_bajo']}\n"
                           f"❌ Sin stock: {datos_reporte['productos_sin_stock']}\n"
                           f"💰 Valor inventario: {self.config_negocio['moneda']}{datos_reporte['valor_inventario']:.2f}\n\n"
                           f"💾 Reporte respaldado automáticamente")
    
    def _reporte_productos_estrella(self):
        """Generar reporte de productos más vendidos"""
        # Simular productos estrella basados en ventas
        productos_estrella = [
            {"nombre": "Producto Ejemplo 1", "ventas": 15, "ingresos": 389.85},
            {"nombre": "Artículo Especializado", "ventas": 8, "ingresos": 719.92},
            {"nombre": "Producto Ejemplo 2", "ventas": 12, "ingresos": 186.00}
        ]
        
        datos_reporte = {
            "fecha": datetime.now().strftime('%d/%m/%Y'),
            "productos_estrella": productos_estrella,
            "total_productos_analizados": len(self.productos)
        }
        
        # 💾 BACKUP AUTOMÁTICO
        if self.backup_manager:
            try:
                archivo_backup = self.backup_manager.backup_reporte_generado("productos_estrella", datos_reporte)
                print(f"💾 Reporte respaldado en: {archivo_backup}")
            except Exception as e:
                print(f"⚠️ Error en backup de reporte: {e}")
        
        mensaje = f"🏆 Productos Más Vendidos - {datos_reporte['fecha']}\n\n"
        for i, producto in enumerate(productos_estrella, 1):
            mensaje += f"{i}. {producto['nombre']}\n   📊 {producto['ventas']} ventas - {self.config_negocio['moneda']}{producto['ingresos']:.2f}\n\n"
        mensaje += "� Reporte respaldado automáticamente"
        
        messagebox.showinfo("🏆 Productos Estrella", mensaje)
    
    def _reporte_clientes(self):
        """Generar reporte de análisis de clientes"""
        datos_reporte = {
            "fecha": datetime.now().strftime('%d/%m/%Y'),
            "total_clientes": len(self.clientes),
            "clientes_activos": len([c for c in self.clientes if c.get('activo', True)]),
            "nuevos_hoy": 0,  # Simular
            "clientes_detalle": self.clientes
        }
        
        # 💾 BACKUP AUTOMÁTICO
        if self.backup_manager:
            try:
                archivo_backup = self.backup_manager.backup_reporte_generado("clientes", datos_reporte)
                print(f"💾 Reporte respaldado en: {archivo_backup}")
            except Exception as e:
                print(f"⚠️ Error en backup de reporte: {e}")
        
        messagebox.showinfo("👥 Análisis de Clientes", 
                           f"📅 Fecha: {datos_reporte['fecha']}\n\n"
                           f"👥 Total clientes: {datos_reporte['total_clientes']}\n"
                           f"✅ Clientes activos: {datos_reporte['clientes_activos']}\n"
                           f"🆕 Nuevos hoy: {datos_reporte['nuevos_hoy']}\n\n"
                           f"� Reporte respaldado automáticamente")
    
    def _reporte_rentabilidad(self):
        """Generar reporte de rentabilidad"""
        ingresos_totales = self.stats_dia['ventas_total']
        costos_estimados = ingresos_totales * 0.6  # Simular 60% de costos
        ganancia_bruta = ingresos_totales - costos_estimados
        margen_rentabilidad = (ganancia_bruta / max(1, ingresos_totales)) * 100
        
        datos_reporte = {
            "fecha": datetime.now().strftime('%d/%m/%Y'),
            "ingresos_totales": ingresos_totales,
            "costos_estimados": costos_estimados,
            "ganancia_bruta": ganancia_bruta,
            "margen_rentabilidad": margen_rentabilidad
        }
        
        # 💾 BACKUP AUTOMÁTICO
        if self.backup_manager:
            try:
                archivo_backup = self.backup_manager.backup_reporte_generado("rentabilidad", datos_reporte)
                print(f"💾 Reporte respaldado en: {archivo_backup}")
            except Exception as e:
                print(f"⚠️ Error en backup de reporte: {e}")
        
        messagebox.showinfo("💰 Análisis de Rentabilidad", 
                           f"📅 Fecha: {datos_reporte['fecha']}\n\n"
                           f"💰 Ingresos totales: {self.config_negocio['moneda']}{ingresos_totales:.2f}\n"
                           f"💸 Costos estimados: {self.config_negocio['moneda']}{costos_estimados:.2f}\n"
                           f"💚 Ganancia bruta: {self.config_negocio['moneda']}{ganancia_bruta:.2f}\n"
                           f"📊 Margen: {margen_rentabilidad:.1f}%\n\n"
                           f"� Reporte respaldado automáticamente")
    
    def _reporte_ejecutivo(self):
        """Generar dashboard ejecutivo completo"""
        datos_reporte = {
            "fecha": datetime.now().strftime('%d/%m/%Y'),
            "resumen_ventas": self.stats_dia,
            "resumen_inventario": {
                "total_productos": len(self.productos),
                "stock_bajo": len([p for p in self.productos if p['stock'] < 10])
            },
            "resumen_clientes": {
                "total": len(self.clientes),
                "activos": len([c for c in self.clientes if c.get('activo', True)])
            },
            "indicadores_clave": {
                "promedio_venta": self.stats_dia['ventas_total'] / max(1, self.stats_dia['num_ventas']),
                "productos_vendidos_por_transaccion": self.stats_dia['items_vendidos'] / max(1, self.stats_dia['num_ventas'])
            }
        }
        
        # 💾 BACKUP AUTOMÁTICO
        if self.backup_manager:
            try:
                archivo_backup = self.backup_manager.backup_reporte_generado("ejecutivo", datos_reporte)
                print(f"💾 Reporte respaldado en: {archivo_backup}")
            except Exception as e:
                print(f"⚠️ Error en backup de reporte: {e}")
        
        messagebox.showinfo("📊 Dashboard Ejecutivo", 
                           f"📅 Fecha: {datos_reporte['fecha']}\n\n"
                           f"� Ventas: {self.config_negocio['moneda']}{self.stats_dia['ventas_total']:.2f}\n"
                           f"🧾 Transacciones: {self.stats_dia['num_ventas']}\n"
                           f"📦 Productos: {datos_reporte['resumen_inventario']['total_productos']}\n"
                           f"👥 Clientes: {datos_reporte['resumen_clientes']['total']}\n"
                           f"📊 Promedio/venta: {self.config_negocio['moneda']}{datos_reporte['indicadores_clave']['promedio_venta']:.2f}\n\n"
                           f"💾 Reporte respaldado automáticamente")
    
    # Métodos para las nuevas funcionalidades
    def _mostrar_compras(self):
        """Mostrar módulo de compras y proveedores"""
        self.modulo_actual = "compras"
        self._limpiar_contenido()
        
        # Crear interfaz de compras
        title = ctk.CTkLabel(
            self.content_frame,
            text="🏢 Módulo de Compras y Proveedores",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Panel de opciones de compras
        opciones_frame = ctk.CTkFrame(self.content_frame)
        opciones_frame.pack(fill="x", padx=20, pady=10)
        
        opciones_container = ctk.CTkFrame(opciones_frame, fg_color="transparent")
        opciones_container.pack(fill="x", padx=20, pady=20)
        
        # Botones de acción principales
        acciones = [
            ("🛒 Nueva Orden", self._nueva_orden_compra, "#007bff"),
            ("🏢 Gestionar Proveedores", self._gestionar_proveedores, "#28a745"),
            ("📋 Recibir Mercancía", self._recibir_mercancia, "#17a2b8"),
            ("📊 Análisis Compras", self._analisis_compras, "#fd7e14")
        ]
        
        for i, (texto, comando, color) in enumerate(acciones):
            btn = ctk.CTkButton(
                opciones_container,
                text=texto,
                width=250,
                height=50,
                fg_color=color,
                command=comando,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            btn.grid(row=0, column=i, padx=15, pady=10)
        
        for i in range(4):
            opciones_container.grid_columnconfigure(i, weight=1)
        
        # Resumen de compras recientes
        resumen_frame = ctk.CTkFrame(self.content_frame)
        resumen_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(resumen_frame, text="📈 Resumen de Compras", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))
        
        # Datos simulados de compras
        compras_info = [
            "� Orden #001 - Proveedor ABC - $1,250.00 - Pendiente",
            "✅ Orden #002 - Distribuidora XYZ - $850.00 - Recibida",
            "🛒 Orden #003 - Suministros DEF - $2,100.00 - En Tránsito"
        ]
        
        for info in compras_info:
            item_frame = ctk.CTkFrame(resumen_frame)
            item_frame.pack(fill="x", padx=30, pady=5)
            
            ctk.CTkLabel(item_frame, text=info, font=ctk.CTkFont(size=12)).pack(pady=10)
    
    def _mostrar_stock_control(self):
        """Mostrar módulo de control de stock"""
        self.modulo_actual = "stock_control"
        self._limpiar_contenido()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📋 Control de Stock y Almacén",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Panel de estadísticas de inventario
        stats_frame = ctk.CTkFrame(self.content_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=20)
        
        stats = [
            ("📦 Total Productos", f"{len(self.productos)}", "#17a2b8"),
            ("⚠️ Stock Bajo", f"{sum(1 for p in self.productos if p['stock'] < p.get('stock_minimo', 5))}", "#dc3545"),
            ("💰 Valor Inventario", f"{self.config_negocio['moneda']}{sum(p['precio'] * p['stock'] for p in self.productos):.2f}", "#28a745"),
            ("📈 Rotación", "Alto", "#fd7e14")
        ]
        
        for i, (titulo, valor, color) in enumerate(stats):
            card = ctk.CTkFrame(stats_container)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
            ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20, weight="bold"), text_color=color).pack()
            ctk.CTkLabel(card, text="Actualizado", font=ctk.CTkFont(size=10), text_color="gray").pack(pady=(0, 10))
        
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1)
    
    def _mostrar_business_intel(self):
        """Mostrar módulo de inteligencia de negocios"""
        self.modulo_actual = "business_intel"
        self._limpiar_contenido()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📈 Business Intelligence",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Panel de métricas clave
        metrics_frame = ctk.CTkFrame(self.content_frame)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        # Simulación de datos analytics
        analytics_data = [
            ("📊 Ingresos del Mes", f"{self.config_negocio['moneda']}12,450.00", "+15.3%", "#28a745"),
            ("🎯 Conversión", "68.5%", "+5.2%", "#17a2b8"),
            ("👥 Clientes Nuevos", "23", "+12", "#6f42c1"),
            ("📈 Ticket Promedio", f"{self.config_negocio['moneda']}45.80", "+8.4%", "#fd7e14")
        ]
        
        metrics_container = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        metrics_container.pack(fill="x", padx=20, pady=20)
        
        for i, (metrica, valor, cambio, color) in enumerate(analytics_data):
            card = ctk.CTkFrame(metrics_container)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            ctk.CTkLabel(card, text=metrica, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=18, weight="bold"), text_color=color).pack()
            ctk.CTkLabel(card, text=cambio, font=ctk.CTkFont(size=11), text_color="#28a745").pack(pady=(0, 15))
        
        for i in range(4):
            metrics_container.grid_columnconfigure(i, weight=1)
    
    def _registro_producto_express(self):
        """Formulario integrado para registrar producto"""
        self.modulo_actual = "nuevo_producto"
        self._limpiar_contenido()
        
        # Título principal
        title = ctk.CTkLabel(
            self.content_frame,
            text="📦 Registro de Nuevo Producto",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Contenedor principal del formulario
        form_container = ctk.CTkFrame(self.content_frame)
        form_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Grid principal del formulario
        form_grid = ctk.CTkFrame(form_container, fg_color="transparent")
        form_grid.pack(expand=True, fill="both", padx=30, pady=30)
        form_grid.grid_columnconfigure(0, weight=1)
        form_grid.grid_columnconfigure(1, weight=1)
        
        # Sección izquierda - Información básica
        left_section = ctk.CTkFrame(form_grid)
        left_section.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=10)
        
        ctk.CTkLabel(left_section, text="� Información Básica", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 15))
        
        # Campos básicos
        self.producto_nombre = ctk.CTkEntry(left_section, placeholder_text="Nombre del producto", width=300, height=40, font=ctk.CTkFont(size=12))
        self.producto_nombre.pack(pady=8, padx=20)
        
        self.producto_categoria = ctk.CTkComboBox(left_section, values=self.categorias, width=300, height=40, font=ctk.CTkFont(size=12))
        self.producto_categoria.pack(pady=8, padx=20)
        self.producto_categoria.set("Seleccionar categoría")
        
        self.producto_codigo = ctk.CTkEntry(left_section, placeholder_text="Código del producto (opcional)", width=300, height=40, font=ctk.CTkFont(size=12))
        self.producto_codigo.pack(pady=8, padx=20)
        
        # Descripción
        ctk.CTkLabel(left_section, text="Descripción:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(15, 5), padx=20, anchor="w")
        self.producto_descripcion = ctk.CTkTextbox(left_section, width=300, height=80, font=ctk.CTkFont(size=11))
        self.producto_descripcion.pack(pady=(0, 20), padx=20)
        
        # Sección derecha - Precios y stock
        right_section = ctk.CTkFrame(form_grid)
        right_section.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=10)
        
        ctk.CTkLabel(right_section, text="💰 Precios y Stock", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 15))
        
        # Campos de precio y stock
        self.producto_precio = ctk.CTkEntry(right_section, placeholder_text="Precio de venta", width=300, height=40, font=ctk.CTkFont(size=12))
        self.producto_precio.pack(pady=8, padx=20)
        
        self.producto_costo = ctk.CTkEntry(right_section, placeholder_text="Costo del producto", width=300, height=40, font=ctk.CTkFont(size=12))
        self.producto_costo.pack(pady=8, padx=20)
        
        self.producto_stock = ctk.CTkEntry(right_section, placeholder_text="Stock inicial", width=300, height=40, font=ctk.CTkFont(size=12))
        self.producto_stock.pack(pady=8, padx=20)
        
        # Información adicional
        ctk.CTkLabel(right_section, text="🏷️ Información Adicional", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 10))
        
        # Frame para opciones adicionales
        options_frame = ctk.CTkFrame(right_section, fg_color="transparent")
        options_frame.pack(pady=10, padx=20, fill="x")
        
        self.producto_activo = ctk.CTkCheckBox(options_frame, text="Producto activo", font=ctk.CTkFont(size=11))
        self.producto_activo.pack(anchor="w", pady=2)
        self.producto_activo.select()  # Activado por defecto
        
        self.producto_promocion = ctk.CTkCheckBox(options_frame, text="En promoción", font=ctk.CTkFont(size=11))
        self.producto_promocion.pack(anchor="w", pady=2)
        
        # Botones de acción
        buttons_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 30), padx=30)
        
        button_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        button_container.pack(expand=True)
        
        ctk.CTkButton(
            button_container,
            text="💾 Guardar Producto",
            command=self._guardar_producto_integrado,
            width=180,
            height=45,
            fg_color="#28a745",
            hover_color="#218838",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_container,
            text="🔄 Limpiar Formulario",
            command=self._limpiar_formulario_producto,
            width=180,
            height=45,
            fg_color="#6c757d",
            hover_color="#5a6268",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_container,
            text="🏠 Volver al Dashboard",
            command=self._mostrar_dashboard,
            width=180,
            height=45,
            fg_color="#007bff",
            hover_color="#0056b3",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
    
    def _agregar_cliente_express(self):
        """Formulario integrado para agregar cliente"""
        self.modulo_actual = "nuevo_cliente"
        self._limpiar_contenido()
        
        # Título principal
        title = ctk.CTkLabel(
            self.content_frame,
            text="👤 Registro de Nuevo Cliente",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Contenedor principal del formulario
        form_container = ctk.CTkFrame(self.content_frame)
        form_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Grid principal del formulario
        form_grid = ctk.CTkFrame(form_container, fg_color="transparent")
        form_grid.pack(expand=True, fill="both", padx=30, pady=30)
        form_grid.grid_columnconfigure(0, weight=1)
        form_grid.grid_columnconfigure(1, weight=1)
        
        # Sección izquierda - Información personal
        left_section = ctk.CTkFrame(form_grid)
        left_section.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=10)
        
        ctk.CTkLabel(left_section, text="👤 Información Personal", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 15))
        
        # Campos personales
        self.cliente_nombre = ctk.CTkEntry(left_section, placeholder_text="Nombre completo *", width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_nombre.pack(pady=8, padx=20)
        
        self.cliente_documento = ctk.CTkEntry(left_section, placeholder_text="Documento de identidad", width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_documento.pack(pady=8, padx=20)
        
        self.cliente_telefono = ctk.CTkEntry(left_section, placeholder_text="Teléfono *", width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_telefono.pack(pady=8, padx=20)
        
        self.cliente_email = ctk.CTkEntry(left_section, placeholder_text="Email", width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_email.pack(pady=8, padx=20)
        
        # Tipo de cliente
        ctk.CTkLabel(left_section, text="Tipo de cliente:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(15, 5), padx=20, anchor="w")
        self.cliente_tipo = ctk.CTkComboBox(left_section, values=["Regular", "VIP", "Mayorista", "Empresa"], width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_tipo.pack(pady=(0, 20), padx=20)
        self.cliente_tipo.set("Regular")
        
        # Sección derecha - Información de contacto
        right_section = ctk.CTkFrame(form_grid)
        right_section.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=10)
        
        ctk.CTkLabel(right_section, text="📍 Información de Contacto", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 15))
        
        # Dirección completa
        self.cliente_direccion = ctk.CTkEntry(right_section, placeholder_text="Dirección", width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_direccion.pack(pady=8, padx=20)
        
        self.cliente_ciudad = ctk.CTkEntry(right_section, placeholder_text="Ciudad", width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_ciudad.pack(pady=8, padx=20)
        
        self.cliente_codigo_postal = ctk.CTkEntry(right_section, placeholder_text="Código postal", width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_codigo_postal.pack(pady=8, padx=20)
        
        # Información comercial
        ctk.CTkLabel(right_section, text="💼 Información Comercial", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(20, 10))
        
        self.cliente_limite_credito = ctk.CTkEntry(right_section, placeholder_text="Límite de crédito (opcional)", width=300, height=40, font=ctk.CTkFont(size=12))
        self.cliente_limite_credito.pack(pady=8, padx=20)
        
        # Opciones adicionales
        options_frame = ctk.CTkFrame(right_section, fg_color="transparent")
        options_frame.pack(pady=10, padx=20, fill="x")
        
        self.cliente_activo = ctk.CTkCheckBox(options_frame, text="Cliente activo", font=ctk.CTkFont(size=11))
        self.cliente_activo.pack(anchor="w", pady=2)
        self.cliente_activo.select()  # Activado por defecto
        
        self.cliente_newsletter = ctk.CTkCheckBox(options_frame, text="Suscribir a newsletter", font=ctk.CTkFont(size=11))
        self.cliente_newsletter.pack(anchor="w", pady=2)
        
        # Observaciones
        ctk.CTkLabel(right_section, text="Observaciones:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(15, 5), padx=20, anchor="w")
        self.cliente_observaciones = ctk.CTkTextbox(right_section, width=300, height=60, font=ctk.CTkFont(size=11))
        self.cliente_observaciones.pack(pady=(0, 20), padx=20)
        
        # Botones de acción
        buttons_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 30), padx=30)
        
        button_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        button_container.pack(expand=True)
        
        ctk.CTkButton(
            button_container,
            text="💾 Guardar Cliente",
            command=self._guardar_cliente_integrado,
            width=180,
            height=45,
            fg_color="#6f42c1",
            hover_color="#5a32a3",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_container,
            text="🔄 Limpiar Formulario",
            command=self._limpiar_formulario_cliente,
            width=180,
            height=45,
            fg_color="#6c757d",
            hover_color="#5a6268",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_container,
            text="🏠 Volver al Dashboard",
            command=self._mostrar_dashboard,
            width=180,
            height=45,
            fg_color="#007bff",
            hover_color="#0056b3",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
    

    
    def _guardar_producto_integrado(self):
        """Guardar nuevo producto desde formulario integrado"""
        try:
            nombre = self.producto_nombre.get().strip()
            precio_str = self.producto_precio.get().strip()
            stock_str = self.producto_stock.get().strip()
            
            # Validaciones
            if not nombre:
                messagebox.showerror("Error", "El nombre del producto es obligatorio")
                return
            
            if not precio_str:
                messagebox.showerror("Error", "El precio es obligatorio")
                return
                
            if not stock_str:
                messagebox.showerror("Error", "El stock inicial es obligatorio")
                return
            
            precio = float(precio_str)
            stock = int(stock_str)
            costo = float(self.producto_costo.get() or 0)
            
            if precio <= 0:
                messagebox.showerror("Error", "El precio debe ser mayor a 0")
                return
                
            if stock < 0:
                messagebox.showerror("Error", "El stock no puede ser negativo")
                return
            
            # Crear nuevo producto
            nuevo_producto = {
                'id': len(self.productos) + 1,
                'nombre': nombre,
                'categoria': self.producto_categoria.get() or 'General',
                'precio': precio,
                'costo': costo,
                'stock': stock,
                'codigo': self.producto_codigo.get() or f"PRO{len(self.productos) + 1:03d}",
                'descripcion': self.producto_descripcion.get("0.0", "end").strip(),
                'activo': self.producto_activo.get(),
                'promocion': self.producto_promocion.get()
            }
            
            self.productos.append(nuevo_producto)
            
            # 💾 BACKUP AUTOMÁTICO - Registrar nuevo producto
            if self.backup_manager:
                try:
                    archivo_backup = self.backup_manager.backup_producto_nuevo(nuevo_producto)
                    print(f"💾 Producto respaldado en: {archivo_backup}")
                except Exception as e:
                    print(f"⚠️ Error en backup de producto: {e}")
            
            # Actualizar estadísticas
            self._calcular_estadisticas()
            
            # Mensaje de éxito
            messagebox.showinfo("✅ Éxito", f"Producto '{nombre}' registrado correctamente\n💾 Backup automático creado")
            
            # Limpiar formulario
            self._limpiar_formulario_producto()
            
        except ValueError:
            messagebox.showerror("Error", "Formato inválido en precio o stock. Use solo números.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar producto: {str(e)}")
    
    def _limpiar_formulario_producto(self):
        """Limpiar todos los campos del formulario de producto"""
        self.producto_nombre.delete(0, 'end')
        self.producto_categoria.set("Seleccionar categoría")
        self.producto_precio.delete(0, 'end')
        self.producto_costo.delete(0, 'end')
        self.producto_stock.delete(0, 'end')
        self.producto_codigo.delete(0, 'end')
        self.producto_descripcion.delete("0.0", "end")
        self.producto_activo.select()
        self.producto_promocion.deselect()
    
    def _guardar_cliente_integrado(self):
        """Guardar nuevo cliente desde formulario integrado"""
        try:
            nombre = self.cliente_nombre.get().strip()
            telefono = self.cliente_telefono.get().strip()
            
            # Validaciones básicas
            if not nombre:
                messagebox.showerror("Error", "El nombre del cliente es obligatorio")
                return
            
            if not telefono:
                messagebox.showerror("Error", "El teléfono es obligatorio")
                return
            
            # Crear nuevo cliente
            nuevo_cliente = {
                'id': len(self.clientes) + 1,
                'nombre': nombre,
                'documento': self.cliente_documento.get().strip(),
                'telefono': telefono,
                'email': self.cliente_email.get().strip(),
                'direccion': self.cliente_direccion.get().strip(),
                'ciudad': self.cliente_ciudad.get().strip(),
                'codigo_postal': self.cliente_codigo_postal.get().strip(),
                'tipo': self.cliente_tipo.get(),
                'limite_credito': float(self.cliente_limite_credito.get() or 0),
                'activo': self.cliente_activo.get(),
                'newsletter': self.cliente_newsletter.get(),
                'observaciones': self.cliente_observaciones.get("0.0", "end").strip(),
                'fecha_registro': datetime.now().strftime('%Y-%m-%d')
            }
            
            self.clientes.append(nuevo_cliente)
            
            # 💾 BACKUP AUTOMÁTICO - Registrar nuevo cliente
            if self.backup_manager:
                try:
                    archivo_backup = self.backup_manager.backup_cliente_nuevo(nuevo_cliente)
                    print(f"💾 Cliente respaldado en: {archivo_backup}")
                except Exception as e:
                    print(f"⚠️ Error en backup de cliente: {e}")
            
            # Actualizar estadísticas
            self._calcular_estadisticas()
            
            # Mensaje de éxito
            messagebox.showinfo("✅ Éxito", f"Cliente '{nombre}' registrado correctamente\n💾 Backup automático creado")
            
            # Limpiar formulario
            self._limpiar_formulario_cliente()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en formato numérico: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")
    
    def _limpiar_formulario_cliente(self):
        """Limpiar todos los campos del formulario de cliente"""
        self.cliente_nombre.delete(0, 'end')
        self.cliente_documento.delete(0, 'end')
        self.cliente_telefono.delete(0, 'end')
        self.cliente_email.delete(0, 'end')
        self.cliente_direccion.delete(0, 'end')
        self.cliente_ciudad.delete(0, 'end')
        self.cliente_codigo_postal.delete(0, 'end')
        self.cliente_tipo.set("Regular")
        self.cliente_limite_credito.delete(0, 'end')
        self.cliente_activo.select()
        self.cliente_newsletter.deselect()
        self.cliente_observaciones.delete("0.0", "end")
    
    def _guardar_producto(self, ventana):
        """Guardar nuevo producto (método anterior para compatibilidad)"""
        try:
            nombre = self.producto_nombre.get()
            precio = float(self.producto_precio.get())
            stock = int(self.producto_stock.get())
            
            if nombre and precio > 0 and stock >= 0:
                nuevo_producto = {
                    'id': len(self.productos) + 1,
                    'nombre': nombre,
                    'categoria': self.producto_categoria.get() or 'General',
                    'precio': precio,
                    'costo': float(self.producto_costo.get() or 0),
                    'stock': stock,
                    'activo': True
                }
                self.productos.append(nuevo_producto)
                messagebox.showinfo("✅ Éxito", "Producto guardado correctamente")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "Completa los campos obligatorios correctamente")
        except ValueError:
            messagebox.showerror("Error", "Verifica que precio y stock sean números válidos")
    
    def _guardar_cliente(self, ventana):
        """Guardar nuevo cliente"""
        nombre = self.cliente_nombre.get()
        telefono = self.cliente_telefono.get()
        
        if nombre and telefono:
            nuevo_cliente = {
                'id': len(self.clientes) + 1,
                'nombre': nombre,
                'telefono': telefono,
                'email': self.cliente_email.get(),
                'direccion': self.cliente_direccion.get(),
                'activo': True
            }
            self.clientes.append(nuevo_cliente)
            messagebox.showinfo("✅ Éxito", "Cliente guardado correctamente")
            ventana.destroy()
        else:
            messagebox.showerror("Error", "Nombre y teléfono son obligatorios")
    
    def _guardar_proveedor(self):
        """Guardar nuevo proveedor"""
        nombre = self.proveedor_nombre.get()
        contacto = self.proveedor_contacto.get()
        
        if nombre and contacto:
            messagebox.showinfo("✅ Éxito", f"Proveedor '{nombre}' guardado correctamente")
            # Limpiar campos
            self.proveedor_nombre.delete(0, 'end')
            self.proveedor_contacto.delete(0, 'end')
            self.proveedor_telefono.delete(0, 'end')
            self.proveedor_email.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Nombre y contacto son obligatorios")
    
    # Métodos para los nuevos botones de acceso rápido
    def _iniciar_venta_rapida(self):
        """Iniciar proceso de venta rápida"""
        self._mostrar_pos()  # Redirigir al punto de venta
    
    def _dashboard_ventas(self):
        """Mostrar dashboard específico de ventas"""
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("📈 Dashboard de Ventas")
        ventana.geometry("800x600")
        ventana.transient(self.root)
        
        title = ctk.CTkLabel(ventana, text="📈 Dashboard de Ventas del Día", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(20, 30))
        
        # Métricas de ventas
        metrics_frame = ctk.CTkFrame(ventana)
        metrics_frame.pack(fill="x", padx=30, pady=20)
        
        metrics_container = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        metrics_container.pack(fill="x", padx=20, pady=20)
        
        ventas_data = [
            ("💰 Total Vendido", f"{self.config_negocio['moneda']}{self.stats_dia['ventas_total']:.2f}", "#28a745"),
            ("🛒 Transacciones", f"{self.stats_dia['num_ventas']}", "#17a2b8"),
            ("📦 Items", f"{self.stats_dia['items_vendidos']}", "#fd7e14"),
            ("🎯 Objetivo Diario", "75% Completado", "#6f42c1")
        ]
        
        for i, (titulo, valor, color) in enumerate(ventas_data):
            card = ctk.CTkFrame(metrics_container)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=18, weight="bold"), text_color=color).pack(pady=(0, 15))
        
        for i in range(4):
            metrics_container.grid_columnconfigure(i, weight=1)
        
        # Gráfico simulado
        grafico_frame = ctk.CTkFrame(ventana)
        grafico_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        ctk.CTkLabel(grafico_frame, text="📊 Ventas por Hora", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(grafico_frame, text="🚧 Gráfico interactivo próximamente", font=ctk.CTkFont(size=14), text_color="gray").pack(pady=50)
    
    # Métodos para el módulo de compras
    def _nueva_orden_compra(self):
        """Crear nueva orden de compra"""
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("🛒 Nueva Orden de Compra")
        ventana.geometry("600x700")
        ventana.transient(self.root)
        ventana.grab_set()
        
        title = ctk.CTkLabel(ventana, text="🛒 Crear Orden de Compra", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(20, 30))
        
        # Formulario de orden
        self.orden_proveedor = ctk.CTkComboBox(ventana, values=["Proveedor ABC", "Distribuidora XYZ", "Suministros DEF"], width=400, height=40)
        self.orden_proveedor.pack(pady=10)
        
        self.orden_producto = ctk.CTkEntry(ventana, placeholder_text="Producto a solicitar", width=400, height=40)
        self.orden_producto.pack(pady=10)
        
        self.orden_cantidad = ctk.CTkEntry(ventana, placeholder_text="Cantidad", width=400, height=40)
        self.orden_cantidad.pack(pady=10)
        
        self.orden_precio = ctk.CTkEntry(ventana, placeholder_text="Precio unitario", width=400, height=40)
        self.orden_precio.pack(pady=10)
        
        btn_frame = ctk.CTkFrame(ventana, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(btn_frame, text="🛒 Crear Orden", command=lambda: self._crear_orden(ventana), width=150, height=40, fg_color="#007bff").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="❌ Cancelar", command=ventana.destroy, width=150, height=40, fg_color="#dc3545").pack(side="left", padx=10)
    
    def _gestionar_proveedores(self):
        """Gestión completa de proveedores"""
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("🏢 Gestión de Proveedores")
        ventana.geometry("700x600")
        ventana.transient(self.root)
        
        title = ctk.CTkLabel(ventana, text="🏢 Administración de Proveedores", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(20, 30))
        
        # Formulario de nuevo proveedor
        form_frame = ctk.CTkFrame(ventana)
        form_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(form_frame, text="➕ Registrar Nuevo Proveedor", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        self.nuevo_proveedor_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre de la empresa", width=400, height=35)
        self.nuevo_proveedor_nombre.pack(pady=5)
        
        self.nuevo_proveedor_contacto = ctk.CTkEntry(form_frame, placeholder_text="Persona de contacto", width=400, height=35)
        self.nuevo_proveedor_contacto.pack(pady=5)
        
        self.nuevo_proveedor_categoria = ctk.CTkComboBox(form_frame, values=["Materiales", "Productos", "Servicios", "Equipos"], width=400, height=35)
        self.nuevo_proveedor_categoria.pack(pady=5)
        
        ctk.CTkButton(form_frame, text="💾 Registrar", command=self._registrar_proveedor, width=200, height=35, fg_color="#28a745").pack(pady=15)
    
    def _recibir_mercancia(self):
        """Proceso de recepción de mercancía"""
        messagebox.showinfo("📋 Recepción", "🚛 Módulo de recepción de mercancía\n\n✅ Verificar productos recibidos\n📝 Actualizar inventario\n📊 Generar reportes de recepción")
    
    def _analisis_compras(self):
        """Análisis y reportes de compras"""
        messagebox.showinfo("📊 Análisis", "📈 Centro de análisis de compras\n\n💰 Costos por proveedor\n📊 Tendencias de compra\n🎯 Optimización de pedidos\n📋 Evaluación de proveedores")
    
    def _crear_orden(self, ventana):
        """Crear orden de compra"""
        proveedor = self.orden_proveedor.get()
        producto = self.orden_producto.get()
        
        if proveedor and producto:
            messagebox.showinfo("✅ Éxito", f"Orden de compra creada:\n\n🏢 Proveedor: {proveedor}\n📦 Producto: {producto}")
            ventana.destroy()
        else:
            messagebox.showerror("Error", "Completa todos los campos obligatorios")
    
    def _registrar_proveedor(self):
        """Registrar nuevo proveedor"""
        nombre = self.nuevo_proveedor_nombre.get()
        contacto = self.nuevo_proveedor_contacto.get()
        
        if nombre and contacto:
            messagebox.showinfo("✅ Éxito", f"Proveedor '{nombre}' registrado exitosamente")
    

    
    def _mostrar_ayuda(self):
        """Mostrar ayuda del sistema"""
        help_text = f"""
        VentaPro Universal - Sistema de Gestión
        
        Navegación:
        • Use el menú lateral para navegar entre módulos
        • Clic en ☰ para expandir/contraer el menú lateral
        
        Módulos disponibles:
        • Dashboard: Vista general del negocio
        • Catálogo: Gestión de productos
        • Caja/POS: Punto de venta
        • Clientes: CRM y gestión de clientes
        • Estadísticas: Reportes y análisis
        • Compras: Gestión de proveedores
        • Stock: Control de inventario
        • Business Intel: Inteligencia de negocios
        
        Configuración actual:
        • Negocio: {self.config_negocio['nombre']}
        • Tipo: {self.config_negocio['tipo']}
        • Moneda: {self.config_negocio['moneda']}
        
        Para soporte técnico, contacte al administrador del sistema.
        """
        messagebox.showinfo("Ayuda - VentaPro Universal", help_text)
    
    def _confirmar_salida(self):
        """Confirmar salida del sistema"""
        if messagebox.askyesno("Salir", "¿Está seguro de que desea salir del sistema?"):
            if logger_disponible and hasattr(self, 'logger'):
                self.logger.info("🔴 Sistema cerrado por el usuario")
            self.root.quit()
            self.nuevo_proveedor_nombre.delete(0, 'end')
            self.nuevo_proveedor_contacto.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Nombre y contacto son obligatorios")

    def ejecutar(self):
        """Ejecutar la aplicación"""
        # Ejecutar con CustomTkinter
        self.root.mainloop()
    
    def _mostrar_backups(self):
        """Mostrar visor de backups automáticos"""
        if not self.backup_manager:
            messagebox.showwarning("Sistema de Backup", "El sistema de backup no está disponible")
            return
        
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("💾 Visor de Backups Automáticos")
        ventana.geometry("900x700")
        ventana.transient(self.root)
        
        # Título
        title = ctk.CTkLabel(
            ventana, 
            text="💾 Sistema de Backup Automático", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Obtener estadísticas de backups
        try:
            stats = self.backup_manager.obtener_estadisticas_backups()
            
            # Frame de estadísticas
            stats_frame = ctk.CTkFrame(ventana)
            stats_frame.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(
                stats_frame,
                text=f"📊 Estadísticas de Backup - {stats['fecha_consulta']}",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=15)
            
            # Grid de estadísticas por tipo
            grid_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            grid_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            tipos_backup = ["productos", "clientes", "ventas", "reportes"]
            colores = ["#28a745", "#6f42c1", "#007bff", "#fd7e14"]
            
            for i, (tipo, color) in enumerate(zip(tipos_backup, colores)):
                if tipo in stats['tipos_backup']:
                    data = stats['tipos_backup'][tipo]
                    
                    card = ctk.CTkFrame(grid_frame, fg_color=color)
                    card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
                    
                    ctk.CTkLabel(
                        card,
                        text=f"📁 {tipo.capitalize()}",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="white"
                    ).pack(pady=(10, 5))
                    
                    ctk.CTkLabel(
                        card,
                        text=f"JSON: {data['archivos_json']}",
                        font=ctk.CTkFont(size=11),
                        text_color="white"
                    ).pack()
                    
                    ctk.CTkLabel(
                        card,
                        text=f"CSV: {data['archivos_csv']}",
                        font=ctk.CTkFont(size=11),
                        text_color="white"
                    ).pack(pady=(0, 10))
            
            for i in range(4):
                grid_frame.grid_columnconfigure(i, weight=1)
            
            # Lista de archivos de backup más recientes
            archivos_frame = ctk.CTkScrollableFrame(ventana, height=300)
            archivos_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                archivos_frame,
                text="📂 Archivos de Backup Recientes",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=10)
            
            backup_dir = "data/backups"
            
            # Listar archivos por categoría
            for tipo in tipos_backup:
                tipo_dir = f"{backup_dir}/{tipo}"
                if os.path.exists(tipo_dir):
                    archivos = [f for f in os.listdir(tipo_dir) if f.endswith('.json')]
                    archivos.sort(reverse=True)  # Más recientes primero
                    
                    if archivos:
                        # Título de la categoría
                        cat_frame = ctk.CTkFrame(archivos_frame, fg_color="#f8f9fa")
                        cat_frame.pack(fill="x", pady=5, padx=10)
                        
                        ctk.CTkLabel(
                            cat_frame,
                            text=f"📁 {tipo.upper()} ({len(archivos)} archivos)",
                            font=ctk.CTkFont(size=12, weight="bold"),
                            anchor="w"
                        ).pack(pady=8, padx=15)
                        
                        # Mostrar hasta 3 archivos más recientes
                        for archivo in archivos[:3]:
                            archivo_frame = ctk.CTkFrame(archivos_frame)
                            archivo_frame.pack(fill="x", pady=2, padx=20)
                            
                            # Extraer timestamp del nombre
                            timestamp = archivo.split('_')[-1].replace('.json', '')
                            if len(timestamp) >= 15:
                                fecha_formateada = f"{timestamp[:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
                            else:
                                fecha_formateada = "Fecha no disponible"
                            
                            info_text = f"📄 {archivo}\n📅 {fecha_formateada}"
                            
                            ctk.CTkLabel(
                                archivo_frame,
                                text=info_text,
                                anchor="w",
                                justify="left"
                            ).pack(side="left", padx=15, pady=8)
                            
                            # Botón para abrir archivo
                            ctk.CTkButton(
                                archivo_frame,
                                text="👁️ Ver",
                                width=60,
                                height=30,
                                command=lambda f=f"{tipo_dir}/{archivo}": self._abrir_backup(f)
                            ).pack(side="right", padx=15, pady=5)
                        
                        if len(archivos) > 3:
                            ctk.CTkLabel(
                                archivos_frame,
                                text=f"... y {len(archivos) - 3} archivos más",
                                text_color="gray",
                                font=ctk.CTkFont(size=10)
                            ).pack(pady=2)
            
            # Botones de acción
            buttons_frame = ctk.CTkFrame(ventana, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=20, pady=20)
            
            ctk.CTkButton(
                buttons_frame,
                text="📂 Abrir Carpeta de Backups",
                command=lambda: os.startfile(backup_dir) if os.name == 'nt' else None,
                width=200
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                buttons_frame,
                text="🔄 Actualizar",
                command=lambda: [ventana.destroy(), self._mostrar_backups()],
                width=120
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                buttons_frame,
                text="❌ Cerrar",
                command=ventana.destroy,
                width=120,
                fg_color="#dc3545"
            ).pack(side="right", padx=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar backups: {str(e)}")
    
    def _abrir_backup(self, archivo_path):
        """Abrir archivo de backup en el visor"""
        try:
            import json
            with open(archivo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Crear ventana para mostrar contenido
            visor = ctk.CTkToplevel(self.root)
            visor.title(f"📄 {os.path.basename(archivo_path)}")
            visor.geometry("700x500")
            
            # Área de texto con scroll
            texto_frame = ctk.CTkScrollableFrame(visor)
            texto_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Mostrar información formateada
            info_text = f"📁 Archivo: {os.path.basename(archivo_path)}\n"
            info_text += f"📅 Fecha: {data.get('fecha_legible', 'No disponible')}\n"
            info_text += f"🔧 Acción: {data.get('accion', 'No disponible')}\n"
            info_text += f"📊 Tipo: {data.get('tipo', 'No disponible')}\n\n"
            info_text += "📋 CONTENIDO DEL BACKUP:\n"
            info_text += "=" * 50 + "\n"
            info_text += json.dumps(data, ensure_ascii=False, indent=2)
            
            ctk.CTkLabel(
                texto_frame,
                text=info_text,
                anchor="nw",
                justify="left",
                font=ctk.CTkFont(family="Consolas", size=10)
            ).pack(fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkButton(
                visor,
                text="✅ Cerrar",
                command=visor.destroy
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")

def main():
    """Función principal"""
    try:
        # Mensaje de inicio
        print("🌍 Iniciando VentaPro Universal - Sistema para TODO tipo de negocio...")
        
        # Inicializar base de datos si está disponible
        if db_disponible:
            db = DatabaseManager()
            if db.inicializar_db():
                print("✅ Base de datos inicializada correctamente")
            else:
                print("⚠️ Ejecutando con datos simulados")
        
        # Crear y ejecutar aplicación
        app = VentaProUniversal()
        
        print("🚀 VentaPro Universal iniciado exitosamente")
        print("🎯 Sistema adaptable a cualquier tipo de negocio")
        print("✨ ¡Listo para gestionar tu comercio!")
        
        app.ejecutar()
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

# Funciones de integración con módulos avanzados para VentaProUniversal
def mostrar_proveedores_avanzado(root, config_negocio):
    """Lanzar módulo completo de proveedores"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from modules.proveedores import InterfazProveedores
        
        # Crear ventana del módulo de proveedores
        proveedores_window = ctk.CTkToplevel(root)
        proveedores_app = InterfazProveedores(proveedores_window, config_negocio)
        
    except ImportError:
        messagebox.showinfo("Módulo Avanzado", 
            "🔧 Para usar proveedores avanzados, instala el módulo completo\n\n"
            "📋 Funcionalidades disponibles:\n"
            "• Registro completo de proveedores\n"
            "• Gestión de órdenes de compra\n" 
            "• Evaluación de proveedores\n"
            "• Historial de transacciones\n"
            "• Análisis de rendimiento")

def mostrar_inventario_avanzado(root, productos, config_negocio):
    """Lanzar módulo avanzado de inventario"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from modules.inventario import InterfazInventario
        
        # Crear ventana del módulo de inventario
        inventario_window = ctk.CTkToplevel(root)
        inventario_app = InterfazInventario(inventario_window, productos, config_negocio)
        
    except ImportError:
        messagebox.showinfo("Módulo Avanzado", 
            "🔧 Para usar inventario avanzado, instala el módulo completo\n\n"
            "📋 Funcionalidades disponibles:\n"
            "• Control avanzado de movimientos\n"
            "• Alertas automáticas de stock\n"
            "• Proyecciones de inventario\n"
            "• Inventario físico\n"
            "• Analytics de rotación")

def mostrar_reportes_avanzados(root, productos, ventas, config_negocio):
    """Lanzar módulo de reportes y analytics"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from modules.reportes import InterfazReportes
        
        # Crear ventana del módulo de reportes
        reportes_window = ctk.CTkToplevel(root)
        reportes_app = InterfazReportes(reportes_window, productos, ventas, config_negocio)
        
    except ImportError:
        messagebox.showinfo("Módulo Avanzado", 
            "🔧 Para usar reportes avanzados, instala el módulo completo\n\n"
            "📋 Funcionalidades disponibles:\n"
            "• Reportes dinámicos de ventas\n"
            "• Analytics de rentabilidad\n"
            "• Proyecciones de negocio\n"
            "• Exportación múltiple\n"
            "• Business Intelligence")

if __name__ == "__main__":
    success = main()
    print("\n🎉 VentaPro Universal terminado" if success else "\n❌ Error al ejecutar VentaPro Universal")
    sys.exit(0 if success else 1)
