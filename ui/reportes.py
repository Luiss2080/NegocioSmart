"""
Módulo de Reportes - NegocioSmart
=============================

Interfaz para generación y visualización de reportes.

Autor: Sistema NegocioSmart
Fecha: 2025-10-04
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

class ModuloReportes:
    """Módulo para generación de reportes"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz del módulo de reportes"""
        
        # Título
        titulo = ctk.CTkLabel(
            self.parent,
            text="📊 Centro de Reportes y Análisis",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Selector de reportes
        selector_frame = ctk.CTkFrame(main_frame)
        selector_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            selector_frame,
            text="📋 Seleccionar Tipo de Reporte",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        # Grid de opciones de reporte
        opciones_frame = ctk.CTkFrame(selector_frame, fg_color="transparent")
        opciones_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Fila 1 de reportes
        fila1 = ctk.CTkFrame(opciones_frame, fg_color="transparent")
        fila1.pack(fill="x", pady=(0, 10))
        
        btn_ventas = ctk.CTkButton(
            fila1,
            text="💰 Reporte de Ventas",
            width=180,
            height=40,
            command=self._reporte_ventas
        )
        btn_ventas.pack(side="left", padx=(0, 10))
        
        btn_inventario = ctk.CTkButton(
            fila1,
            text="📦 Reporte de Inventario",
            width=180,
            height=40,
            command=self._reporte_inventario
        )
        btn_inventario.pack(side="left", padx=(0, 10))
        
        btn_clientes = ctk.CTkButton(
            fila1,
            text="👥 Reporte de Clientes",
            width=180,
            height=40,
            command=self._reporte_clientes
        )
        btn_clientes.pack(side="left", padx=(0, 10))
        
        # Fila 2 de reportes
        fila2 = ctk.CTkFrame(opciones_frame, fg_color="transparent")
        fila2.pack(fill="x", pady=(0, 10))
        
        btn_financiero = ctk.CTkButton(
            fila2,
            text="💹 Reporte Financiero",
            width=180,
            height=40,
            command=self._reporte_financiero
        )
        btn_financiero.pack(side="left", padx=(0, 10))
        
        btn_productos = ctk.CTkButton(
            fila2,
            text="📈 Productos Más Vendidos",
            width=180,
            height=40,
            command=self._productos_vendidos
        )
        btn_productos.pack(side="left", padx=(0, 10))
        
        btn_personalizado = ctk.CTkButton(
            fila2,
            text="🎯 Reporte Personalizado",
            width=180,
            height=40,
            fg_color="#6f42c1",
            command=self._reporte_personalizado
        )
        btn_personalizado.pack(side="left", padx=(0, 10))
        
        # Configuración de filtros
        filtros_frame = ctk.CTkFrame(main_frame)
        filtros_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            filtros_frame,
            text="🔧 Configuración de Filtros",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        config_grid = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        config_grid.pack(fill="x", padx=20, pady=(0, 20))
        
        # Filtros de fecha
        fecha_frame = ctk.CTkFrame(config_grid, fg_color="transparent")
        fecha_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(fecha_frame, text="📅 Rango de Fechas:", width=120).pack(side="left", padx=(0, 10))
        
        self.fecha_inicio = ctk.CTkEntry(
            fecha_frame,
            placeholder_text="Fecha inicio (YYYY-MM-DD)",
            width=150
        )
        self.fecha_inicio.pack(side="left", padx=(0, 10))
        
        self.fecha_fin = ctk.CTkEntry(
            fecha_frame,
            placeholder_text="Fecha fin (YYYY-MM-DD)",
            width=150
        )
        self.fecha_fin.pack(side="left", padx=(0, 20))
        
        # Formato de salida
        formato_frame = ctk.CTkFrame(config_grid, fg_color="transparent")
        formato_frame.pack(fill="x")
        
        ctk.CTkLabel(formato_frame, text="📄 Formato:", width=120).pack(side="left", padx=(0, 10))
        
        self.formato_combo = ctk.CTkComboBox(
            formato_frame,
            values=["PDF", "Excel", "CSV", "Pantalla"],
            width=120
        )
        self.formato_combo.pack(side="left", padx=(0, 20))
        self.formato_combo.set("PDF")
        
        # Botón generar
        btn_generar = ctk.CTkButton(
            formato_frame,
            text="🚀 Generar Reporte",
            width=150,
            height=35,
            fg_color="#28a745",
            command=self._generar_reporte
        )
        btn_generar.pack(side="left")
        
        # Área de vista previa
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            preview_frame,
            text="👁️ Vista Previa del Reporte",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        mensaje = ctk.CTkLabel(
            preview_frame,
            text="📊 Centro de Análisis de Datos\n\n🚧 Sistema de reportes en desarrollo\n\nAquí se mostrarán gráficos, tablas y análisis\ncon datos actualizados del negocio.\n\n✨ Próximamente: Gráficos interactivos con Matplotlib\n📈 Análisis de tendencias y patrones de venta\n💡 Recomendaciones automáticas de negocio",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        mensaje.pack(expand=True, pady=30)
        
        # Guardamos referencia del tipo de reporte actual
        self.tipo_reporte = None
    
    def _reporte_ventas(self):
        """Configurar reporte de ventas"""
        self.tipo_reporte = "ventas"
        messagebox.showinfo("Reporte de Ventas", "Configurando reporte de ventas...\n\nIncluirá:\n- Total de ventas por período\n- Tendencias de venta\n- Análisis por productos\n- Comparativas mensuales")
    
    def _reporte_inventario(self):
        """Configurar reporte de inventario"""
        self.tipo_reporte = "inventario"
        messagebox.showinfo("Reporte de Inventario", "Configurando reporte de inventario...\n\nIncluirá:\n- Stock actual por producto\n- Productos con bajo stock\n- Rotación de inventario\n- Valorización de existencias")
    
    def _reporte_clientes(self):
        """Configurar reporte de clientes"""
        self.tipo_reporte = "clientes"
        messagebox.showinfo("Reporte de Clientes", "Configurando reporte de clientes...\n\nIncluirá:\n- Lista completa de clientes\n- Historial de compras\n- Clientes más frecuentes\n- Análisis de segmentación")
    
    def _reporte_financiero(self):
        """Configurar reporte financiero"""
        self.tipo_reporte = "financiero"
        messagebox.showinfo("Reporte Financiero", "Configurando reporte financiero...\n\nIncluirá:\n- Ingresos y gastos\n- Márgenes de ganancia\n- Flujo de caja\n- Indicadores financieros")
    
    def _productos_vendidos(self):
        """Configurar reporte de productos más vendidos"""
        self.tipo_reporte = "productos_top"
        messagebox.showinfo("Productos Más Vendidos", "Configurando análisis de productos...\n\nIncluirá:\n- Top 10 productos vendidos\n- Análisis de popularidad\n- Tendencias de demanda\n- Recomendaciones de stock")
    
    def _reporte_personalizado(self):
        """Configurar reporte personalizado"""
        self.tipo_reporte = "personalizado"
        messagebox.showinfo("Reporte Personalizado", "Configurando reporte personalizado...\n\n🎯 Próximamente:\n- Constructor de reportes drag & drop\n- Filtros avanzados personalizables\n- Métricas customizadas\n- Dashboards interactivos")
    
    def _generar_reporte(self):
        """Generar el reporte configurado"""
        if not self.tipo_reporte:
            messagebox.showwarning("Sin Reporte", "Por favor selecciona un tipo de reporte primero")
            return
        
        fecha_inicio = self.fecha_inicio.get()
        fecha_fin = self.fecha_fin.get()
        formato = self.formato_combo.get()
        
        messagebox.showinfo(
            "Generar Reporte", 
            f"Generando reporte: {self.tipo_reporte}\n"
            f"Desde: {fecha_inicio or 'Inicio'}\n"
            f"Hasta: {fecha_fin or 'Hoy'}\n"
            f"Formato: {formato}\n\n"
            f"🚧 Funcionalidad en desarrollo\n"
            f"✨ Próximamente disponible"
        )