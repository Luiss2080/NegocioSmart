"""
Dashboard Principal - VentaPro
=============================

Panel de control principal con estadísticas, gráficos y resumen
del estado del negocio en tiempo real.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime, timedelta
import threading

class Dashboard:
    """Panel de control principal del sistema"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.datos_cargados = False
        
        # Crear la interfaz
        self._crear_interfaz()
        
        # Cargar datos en hilo separado para no bloquear la UI
        self._cargar_datos_async()
    
    def _crear_interfaz(self):
        """Crea la interfaz del dashboard"""
        
        # Título principal
        self.titulo = ctk.CTkLabel(
            self.parent, 
            text="🏠 Dashboard - Panel de Control", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.titulo.pack(pady=(0, 20))
        
        # Frame para tarjetas de estadísticas
        self.stats_frame = ctk.CTkFrame(self.parent)
        self.stats_frame.pack(fill="x", pady=(0, 20))
        
        # Crear tarjetas de estadísticas
        self._crear_tarjetas_estadisticas()
        
        # Frame inferior con gráficos y alertas
        self.inferior_frame = ctk.CTkFrame(self.parent)
        self.inferior_frame.pack(fill="both", expand=True)
        
        # Crear secciones inferiores
        self._crear_seccion_ventas()
        self._crear_seccion_inventario()
        self._crear_seccion_alertas()
    
    def _crear_tarjetas_estadisticas(self):
        """Crea las tarjetas con estadísticas principales"""
        
        # Frame contenedor para las tarjetas
        tarjetas_container = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        tarjetas_container.pack(fill="x", padx=20, pady=20)
        
        # Configurar grid
        tarjetas_container.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Datos de ejemplo (se actualizarán con datos reales)
        estadisticas = [
            ("💰 Ventas Hoy", "$1,250.00", "+12%", "#28a745"),
            ("📦 Productos", "156", "8 sin stock", "#17a2b8"),
            ("👥 Clientes", "42", "+3 nuevos", "#6f42c1"),
            ("📊 Mes Actual", "$18,500.00", "+8%", "#fd7e14")
        ]
        
        self.tarjetas = []
        
        for i, (titulo, valor, subtexto, color) in enumerate(estadisticas):
            tarjeta = self._crear_tarjeta_estadistica(
                tarjetas_container, titulo, valor, subtexto, color
            )
            tarjeta.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.tarjetas.append(tarjeta)
    
    def _crear_tarjeta_estadistica(self, parent, titulo, valor, subtexto, color):
        """Crea una tarjeta individual de estadística"""
        
        # Frame principal de la tarjeta
        tarjeta = ctk.CTkFrame(parent, width=200, height=120, fg_color=color, corner_radius=15)
        tarjeta.pack_propagate(False)
        
        # Título
        titulo_label = ctk.CTkLabel(
            tarjeta, 
            text=titulo, 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        )
        titulo_label.pack(pady=(15, 5))
        
        # Valor principal
        valor_label = ctk.CTkLabel(
            tarjeta, 
            text=valor, 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        valor_label.pack()
        
        # Subtexto
        sub_label = ctk.CTkLabel(
            tarjeta, 
            text=subtexto, 
            font=ctk.CTkFont(size=10),
            text_color="lightgray"
        )
        sub_label.pack(pady=(5, 15))
        
        return tarjeta
    
    def _crear_seccion_ventas(self):
        """Crea la sección de ventas recientes"""
        
        # Frame para ventas (lado izquierdo)
        self.ventas_frame = ctk.CTkFrame(self.inferior_frame)
        self.ventas_frame.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=20)
        
        # Título
        ventas_titulo = ctk.CTkLabel(
            self.ventas_frame, 
            text="💰 Ventas Recientes", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ventas_titulo.pack(pady=(15, 10))
        
        # Tabla de ventas recientes
        self._crear_tabla_ventas()
    
    def _crear_tabla_ventas(self):
        """Crea la tabla de ventas recientes"""
        
        # Frame para la tabla
        tabla_frame = ctk.CTkFrame(self.ventas_frame, fg_color="transparent")
        tabla_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Headers
        headers = ["Folio", "Cliente", "Total", "Hora"]
        header_frame = ctk.CTkFrame(tabla_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame, 
                text=header, 
                font=ctk.CTkFont(size=12, weight="bold"),
                width=100
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Datos de ejemplo
        ventas_ejemplo = [
            ("F-000123", "Juan Pérez", "$450.00", "14:30"),
            ("F-000122", "María López", "$125.50", "14:15"),
            ("F-000121", "Cliente General", "$89.00", "13:45"),
            ("F-000120", "Carlos Ruiz", "$234.75", "13:20"),
            ("F-000119", "Ana García", "$67.25", "12:55")
        ]
        
        # Contenedor scrollable para las ventas
        ventas_container = ctk.CTkScrollableFrame(tabla_frame, height=200)
        ventas_container.pack(fill="both", expand=True)
        
        for i, (folio, cliente, total, hora) in enumerate(ventas_ejemplo):
            fila_frame = ctk.CTkFrame(ventas_container, fg_color="transparent")
            fila_frame.pack(fill="x", pady=2)
            
            # Datos de la fila
            datos = [folio, cliente, total, hora]
            for j, dato in enumerate(datos):
                label = ctk.CTkLabel(
                    fila_frame, 
                    text=dato, 
                    font=ctk.CTkFont(size=11),
                    width=100
                )
                label.grid(row=0, column=j, padx=5, pady=2, sticky="w")
    
    def _crear_seccion_inventario(self):
        """Crea la sección de inventario"""
        
        # Frame para inventario (lado derecho superior)
        self.inventario_frame = ctk.CTkFrame(self.inferior_frame)
        self.inventario_frame.pack(side="right", fill="y", padx=(10, 20), pady=20)
        
        # Título
        inventario_titulo = ctk.CTkLabel(
            self.inventario_frame, 
            text="📦 Estado del Inventario", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        inventario_titulo.pack(pady=(15, 10))
        
        # Gráfico simple de inventario
        self._crear_grafico_inventario()
    
    def _crear_grafico_inventario(self):
        """Crea un gráfico simple del inventario"""
        
        # Frame para el gráfico
        grafico_frame = ctk.CTkFrame(self.inventario_frame, width=300, height=200)
        grafico_frame.pack(padx=15, pady=(0, 15))
        grafico_frame.pack_propagate(False)
        
        # Título del gráfico
        titulo_grafico = ctk.CTkLabel(
            grafico_frame, 
            text="Distribución por Categorías", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        titulo_grafico.pack(pady=(10, 5))
        
        # Datos de ejemplo
        categorias_datos = [
            ("Abarrotes", 45, "#28a745"),
            ("Bebidas", 30, "#17a2b8"),
            ("Limpieza", 15, "#ffc107"),
            ("Otros", 10, "#6c757d")
        ]
        
        # Crear barras simples
        for categoria, porcentaje, color in categorias_datos:
            # Frame para cada barra
            barra_frame = ctk.CTkFrame(grafico_frame, fg_color="transparent")
            barra_frame.pack(fill="x", padx=10, pady=2)
            
            # Etiqueta
            etiqueta = ctk.CTkLabel(
                barra_frame, 
                text=f"{categoria} ({porcentaje}%)", 
                font=ctk.CTkFont(size=10),
                width=120
            )
            etiqueta.pack(side="left", padx=(0, 5))
            
            # Barra de progreso
            barra = ctk.CTkProgressBar(barra_frame, width=120, progress_color=color)
            barra.pack(side="right")
            barra.set(porcentaje / 100)
    
    def _crear_seccion_alertas(self):
        """Crea la sección de alertas"""
        
        # Frame para alertas (abajo del inventario)
        self.alertas_frame = ctk.CTkFrame(self.inventario_frame)
        self.alertas_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        # Título
        alertas_titulo = ctk.CTkLabel(
            self.alertas_frame, 
            text="⚠️ Alertas del Sistema", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        alertas_titulo.pack(pady=(10, 5))
        
        # Lista de alertas
        alertas = [
            ("🔴 Stock bajo: Coca Cola 600ml (5 unidades)", "high"),
            ("🟡 Stock bajo: Pan Bimbo (3 unidades)", "medium"),
            ("🟢 Sistema funcionando correctamente", "low")
        ]
        
        for alerta, prioridad in alertas:
            color = {"high": "#dc3545", "medium": "#ffc107", "low": "#28a745"}[prioridad]
            
            alerta_label = ctk.CTkLabel(
                self.alertas_frame,
                text=alerta,
                font=ctk.CTkFont(size=10),
                text_color=color,
                anchor="w"
            )
            alerta_label.pack(fill="x", padx=10, pady=2)
    
    def _cargar_datos_async(self):
        """Carga los datos en un hilo separado"""
        def cargar():
            try:
                # Simular carga de datos
                # En la implementación real, aquí se cargarían los datos de la BD
                import time
                time.sleep(1)  # Simular tiempo de carga
                
                # Actualizar la UI en el hilo principal
                self.parent.after(0, self._actualizar_datos)
                
            except Exception as e:
                print(f"Error cargando datos del dashboard: {e}")
        
        thread = threading.Thread(target=cargar, daemon=True)
        thread.start()
    
    def _actualizar_datos(self):
        """Actualiza los datos en la interfaz"""
        # Aquí se actualizarían los datos reales
        self.datos_cargados = True
        
        # Ejemplo de actualización de una tarjeta
        if self.tarjetas:
            # Actualizar primera tarjeta con datos reales
            pass
    
    def actualizar_dashboard(self):
        """Método público para actualizar el dashboard"""
        self._cargar_datos_async()
    
    def obtener_resumen_ventas(self):
        """Obtiene el resumen de ventas del día"""
        # En la implementación real, consultar la base de datos
        return {
            'ventas_hoy': 1250.00,
            'num_ventas': 8,
            'promedio_venta': 156.25,
            'productos_vendidos': 24
        }
    
    def obtener_alertas_inventario(self):
        """Obtiene las alertas de inventario"""
        # En la implementación real, consultar productos con stock bajo
        return [
            {"producto": "Coca Cola 600ml", "stock_actual": 5, "stock_minimo": 10},
            {"producto": "Pan Bimbo", "stock_actual": 3, "stock_minimo": 8}
        ]