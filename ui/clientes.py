"""
Módulo de Clientes - VentaPro
=============================

Interfaz para la gestión de clientes.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

class ModuloClientes:
    """Módulo para gestión de clientes"""
    
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz del módulo de clientes"""
        
        # Título
        titulo = ctk.CTkLabel(
            self.parent,
            text="👥 Gestión de Clientes",
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
            text="👤 Nuevo Cliente",
            width=150,
            command=self._nuevo_cliente
        )
        btn_nuevo.pack(side="left", padx=(0, 10))
        
        btn_editar = ctk.CTkButton(
            toolbar_frame,
            text="✏️ Editar",
            width=120,
            command=self._editar_cliente
        )
        btn_editar.pack(side="left", padx=(0, 10))
        
        btn_eliminar = ctk.CTkButton(
            toolbar_frame,
            text="🗑️ Eliminar",
            width=120,
            fg_color="#dc3545",
            command=self._eliminar_cliente
        )
        btn_eliminar.pack(side="left", padx=(0, 10))
        
        btn_historial = ctk.CTkButton(
            toolbar_frame,
            text="📊 Historial Compras",
            width=150,
            command=self._ver_historial
        )
        btn_historial.pack(side="left", padx=(0, 10))
        
        # Búsqueda
        search_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar clientes...",
            width=200
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        btn_buscar = ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=80,
            command=self._buscar_clientes
        )
        btn_buscar.pack(side="left")
        
        # Estadísticas rápidas
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 Estadísticas de Clientes",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=(0, 10))
        
        # Cards de estadísticas
        card1 = ctk.CTkFrame(stats_grid)
        card1.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(card1, text="👥 Total Clientes", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(card1, text="0", font=ctk.CTkFont(size=18), text_color="#007bff").pack(pady=(0, 10))
        
        card2 = ctk.CTkFrame(stats_grid)
        card2.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ctk.CTkLabel(card2, text="🆕 Nuevos Este Mes", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(card2, text="0", font=ctk.CTkFont(size=18), text_color="#28a745").pack(pady=(0, 10))
        
        card3 = ctk.CTkFrame(stats_grid)
        card3.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(card3, text="⭐ Clientes VIP", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(card3, text="0", font=ctk.CTkFont(size=18), text_color="#ffc107").pack(pady=(0, 10))
        
        # Lista de clientes
        lista_frame = ctk.CTkFrame(main_frame)
        lista_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        mensaje = ctk.CTkLabel(
            lista_frame,
            text="👥 Base de Datos de Clientes\n\n🚧 Lista de clientes en desarrollo\n\nAquí aparecerá la lista completa de clientes\ncon información de contacto, historial de compras\ny opciones de gestión avanzada.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        mensaje.pack(expand=True, pady=50)
    
    def _nuevo_cliente(self):
        """Abrir formulario para nuevo cliente"""
        messagebox.showinfo("Nuevo Cliente", "Formulario de nuevo cliente en desarrollo")
    
    def _editar_cliente(self):
        """Editar cliente seleccionado"""
        messagebox.showinfo("Editar Cliente", "Función de editar cliente en desarrollo")
    
    def _eliminar_cliente(self):
        """Eliminar cliente seleccionado"""
        messagebox.showwarning("Eliminar Cliente", "Función de eliminar cliente en desarrollo")
    
    def _ver_historial(self):
        """Ver historial de compras del cliente"""
        messagebox.showinfo("Historial", "Historial de compras en desarrollo")
    
    def _buscar_clientes(self):
        """Buscar clientes"""
        termino = self.search_entry.get()
        messagebox.showinfo("Buscar", f"Buscando: '{termino}'\n\nFuncionalidad en desarrollo")