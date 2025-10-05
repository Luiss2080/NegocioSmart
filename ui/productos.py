"""
Módulo de Productos - VentaPro
=============================

Interfaz para la gestión completa de productos e inventario.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

class ModuloProductos:
    """Módulo para gestión de productos"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz del módulo de productos"""
        
        # Título
        titulo = ctk.CTkLabel(
            self.parent,
            text="📦 Gestión de Productos e Inventario",
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
        btn_nuevo = ctk.CTkButton(
            toolbar_frame,
            text="➕ Nuevo Producto",
            width=150,
            command=self._nuevo_producto
        )
        btn_nuevo.pack(side="left", padx=(0, 10))
        
        btn_editar = ctk.CTkButton(
            toolbar_frame,
            text="✏️ Editar",
            width=120,
            command=self._editar_producto
        )
        btn_editar.pack(side="left", padx=(0, 10))
        
        btn_eliminar = ctk.CTkButton(
            toolbar_frame,
            text="🗑️ Eliminar",
            width=120,
            fg_color="#dc3545",
            command=self._eliminar_producto
        )
        btn_eliminar.pack(side="left", padx=(0, 10))
        
        # Búsqueda
        search_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar productos...",
            width=200
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        btn_buscar = ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=80,
            command=self._buscar_productos
        )
        btn_buscar.pack(side="left")
        
        # Lista de productos (placeholder)
        lista_frame = ctk.CTkFrame(main_frame)
        lista_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensaje temporal
        mensaje = ctk.CTkLabel(
            lista_frame,
            text="📋 Lista de Productos\n\n🚧 Tabla de productos en desarrollo\n\nAquí aparecerá la lista completa de productos\ncon funcionalidades de edición, filtrado y búsqueda.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        mensaje.pack(expand=True, pady=50)
    
    def _nuevo_producto(self):
        """Abrir formulario para nuevo producto"""
        messagebox.showinfo("Nuevo Producto", "Formulario de nuevo producto en desarrollo")
    
    def _editar_producto(self):
        """Editar producto seleccionado"""
        messagebox.showinfo("Editar Producto", "Función de editar producto en desarrollo")
    
    def _eliminar_producto(self):
        """Eliminar producto seleccionado"""
        messagebox.showwarning("Eliminar Producto", "Función de eliminar producto en desarrollo")
    
    def _buscar_productos(self):
        """Buscar productos"""
        termino = self.search_entry.get()
        messagebox.showinfo("Buscar", f"Buscando: '{termino}'\n\nFuncionalidad en desarrollo")