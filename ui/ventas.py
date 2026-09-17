"""
Módulo de Ventas - NegocioSmart
===========================

Interfaz para el registro y gestión de ventas.

Autor: Sistema NegocioSmart
Fecha: 2025-10-04
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

class ModuloVentas:
    """Módulo para gestión de ventas"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz del módulo de ventas"""
        
        # Título
        titulo = ctk.CTkLabel(
            self.parent,
            text="💰 Gestión de Ventas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Barra de herramientas
        toolbar_frame = ctk.CTkFrame(main_frame)
        toolbar_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Botones de acción
        btn_nueva_venta = ctk.CTkButton(
            toolbar_frame,
            text="🛒 Nueva Venta",
            width=150,
            fg_color="#28a745",
            command=self._nueva_venta
        )
        btn_nueva_venta.pack(side="left", padx=(0, 10))
        
        btn_factura = ctk.CTkButton(
            toolbar_frame,
            text="📄 Generar Factura",
            width=150,
            command=self._generar_factura
        )
        btn_factura.pack(side="left", padx=(0, 10))
        
        btn_historial = ctk.CTkButton(
            toolbar_frame,
            text="📊 Historial",
            width=120,
            command=self._ver_historial
        )
        btn_historial.pack(side="left", padx=(0, 10))
        
        # Filtros por fecha
        filter_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(filter_frame, text="📅 Filtrar:").pack(side="left", padx=(0, 5))
        
        self.fecha_inicio = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Fecha inicio (YYYY-MM-DD)",
            width=150
        )
        self.fecha_inicio.pack(side="left", padx=(0, 5))
        
        self.fecha_fin = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Fecha fin (YYYY-MM-DD)",
            width=150
        )
        self.fecha_fin.pack(side="left", padx=(0, 10))
        
        btn_filtrar = ctk.CTkButton(
            filter_frame,
            text="Filtrar",
            width=80,
            command=self._filtrar_ventas
        )
        btn_filtrar.pack(side="left")
        
        # Contenido principal
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Resumen de ventas del día
        resumen_frame = ctk.CTkFrame(content_frame)
        resumen_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            resumen_frame,
            text="📈 Resumen del Día",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        stats_frame = ctk.CTkFrame(resumen_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Stats cards
        stat1 = ctk.CTkFrame(stats_frame)
        stat1.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(stat1, text="💵 Ventas Hoy", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(stat1, text="$0.00", font=ctk.CTkFont(size=20), text_color="#28a745").pack(pady=(0, 10))
        
        stat2 = ctk.CTkFrame(stats_frame)
        stat2.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(stat2, text="🧾 Facturas", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(stat2, text="0", font=ctk.CTkFont(size=20), text_color="#007bff").pack(pady=(0, 10))
        
        stat3 = ctk.CTkFrame(stats_frame)
        stat3.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(stat3, text="📦 Productos Vendidos", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(stat3, text="0", font=ctk.CTkFont(size=20), text_color="#ffc107").pack(pady=(0, 10))
        
        # Lista de ventas
        lista_frame = ctk.CTkFrame(content_frame)
        lista_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        mensaje = ctk.CTkLabel(
            lista_frame,
            text="🛍️ Historial de Ventas\n\n🚧 Lista de ventas en desarrollo\n\nAquí aparecerá el historial completo de ventas\ncon opciones de filtrado y generación de reportes.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        mensaje.pack(expand=True, pady=50)
    
    def _nueva_venta(self):
        """Iniciar proceso de nueva venta"""
        messagebox.showinfo("Nueva Venta", "Formulario de nueva venta en desarrollo")
    
    def _generar_factura(self):
        """Generar factura de venta"""
        messagebox.showinfo("Generar Factura", "Generador de facturas en desarrollo")
    
    def _ver_historial(self):
        """Ver historial completo de ventas"""
        messagebox.showinfo("Historial", "Historial de ventas en desarrollo")
    
    def _filtrar_ventas(self):
        """Filtrar ventas por fecha"""
        inicio = self.fecha_inicio.get()
        fin = self.fecha_fin.get()
        messagebox.showinfo("Filtrar", f"Filtrando ventas:\nDesde: {inicio}\nHasta: {fin}\n\nFuncionalidad en desarrollo")