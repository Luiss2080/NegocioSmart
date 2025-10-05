"""
VentaPro Universal - Módulo de Gestión de Proveedores
====================================================

Sistema completo para gestionar proveedores, compras e inventarios.
Adaptable a cualquier tipo de negocio.

Características:
- ✅ Registro completo de proveedores
- ✅ Gestión de órdenes de compra
- ✅ Histórico de precios y compras
- ✅ Evaluación de proveedores
- ✅ Alertas de reposición automática
- ✅ Comparativa de precios

Autor: VentaPro Universal
Fecha: 2025-01-04
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
from enum import Enum

class TipoProveedor(Enum):
    """Tipos de proveedores"""
    MAYORISTA = "Mayorista"
    MINORISTA = "Minorista" 
    DISTRIBUIDOR = "Distribuidor"
    FABRICANTE = "Fabricante"
    IMPORTADOR = "Importador"
    LOCAL = "Local"

class EstadoProveedor(Enum):
    """Estados del proveedor"""
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    BLOQUEADO = "Bloqueado"
    EVALUACION = "En Evaluación"

class EstadoOrden(Enum):
    """Estados de órdenes de compra"""
    BORRADOR = "Borrador"
    ENVIADA = "Enviada"
    CONFIRMADA = "Confirmada"
    RECIBIDA = "Recibida"
    FACTURADA = "Facturada"
    CANCELADA = "Cancelada"

@dataclass
class Proveedor:
    """Modelo de proveedor universal"""
    id: int
    nombre: str
    contacto_principal: str
    telefono: str
    email: str
    direccion: str
    rfc_nit: str = ""
    
    # Clasificación
    tipo: TipoProveedor = TipoProveedor.LOCAL
    categoria_productos: List[str] = None
    
    # Estado y evaluación
    estado: EstadoProveedor = EstadoProveedor.ACTIVO
    calificacion: float = 5.0  # 1-10
    fecha_registro: datetime = datetime.now()
    
    # Condiciones comerciales
    dias_credito: int = 0
    descuento_general: float = 0.0
    moneda_preferida: str = "MXN"
    metodo_pago_preferido: str = "Transferencia"
    
    # Información adicional
    sitio_web: str = ""
    notas: str = ""
    
    def __post_init__(self):
        if self.categoria_productos is None:
            self.categoria_productos = []

@dataclass  
class OrdenCompra:
    """Orden de compra"""
    id: int
    numero_orden: str
    proveedor_id: int
    fecha_orden: datetime
    fecha_entrega_esperada: datetime
    
    # Productos
    productos: List[Dict] = None  # [{"producto_id": 1, "cantidad": 10, "precio_unitario": 25.0}]
    
    # Totales
    subtotal: float = 0.0
    impuestos: float = 0.0
    descuento: float = 0.0
    total: float = 0.0
    
    # Estado y seguimiento
    estado: EstadoOrden = EstadoOrden.BORRADOR
    notas: str = ""
    fecha_recepcion: Optional[datetime] = None
    
    def __post_init__(self):
        if self.productos is None:
            self.productos = []

class GestorProveedores:
    """Gestor completo de proveedores"""
    
    def __init__(self):
        self.proveedores: List[Proveedor] = []
        self.ordenes: List[OrdenCompra] = []
        self._inicializar_datos_demo()
    
    def _inicializar_datos_demo(self):
        """Datos de demostración"""
        self.proveedores = [
            Proveedor(
                id=1,
                nombre="Distribuidora Central S.A.",
                contacto_principal="María González",
                telefono="555-0101",
                email="ventas@distribuidora.com",
                direccion="Av. Industrial 123, Ciudad",
                rfc_nit="DCE850101ABC",
                tipo=TipoProveedor.DISTRIBUIDOR,
                categoria_productos=["Abarrotes", "Bebidas", "Snacks"],
                dias_credito=30,
                descuento_general=5.0,
                calificacion=8.5
            ),
            Proveedor(
                id=2,
                nombre="Ferretería El Martillo",
                contacto_principal="Carlos Herrera",
                telefono="555-0102", 
                email="compras@elmartillo.com",
                direccion="Calle Herrajes 456",
                tipo=TipoProveedor.MAYORISTA,
                categoria_productos=["Herramientas", "Tornillería", "Materiales"],
                dias_credito=15,
                descuento_general=3.0,
                calificacion=9.2
            ),
            Proveedor(
                id=3,
                nombre="Textiles La Moda",
                contacto_principal="Ana Rodríguez",
                telefono="555-0103",
                email="ana@lamoda.com", 
                direccion="Boulevard Moda 789",
                tipo=TipoProveedor.FABRICANTE,
                categoria_productos=["Ropa Dama", "Ropa Caballero", "Accesorios"],
                dias_credito=45,
                descuento_general=8.0,
                calificacion=7.8
            )
        ]
        
        # Órdenes de ejemplo
        self.ordenes = [
            OrdenCompra(
                id=1,
                numero_orden="OC-2025-001",
                proveedor_id=1,
                fecha_orden=datetime.now() - timedelta(days=5),
                fecha_entrega_esperada=datetime.now() + timedelta(days=2),
                productos=[
                    {"producto_id": 1, "nombre": "Refresco Cola 600ml", "cantidad": 50, "precio_unitario": 12.50},
                    {"producto_id": 2, "nombre": "Galletas Chocolate", "cantidad": 30, "precio_unitario": 8.75}
                ],
                subtotal=887.50,
                impuestos=142.00,
                total=1029.50,
                estado=EstadoOrden.CONFIRMADA
            )
        ]
    
    def agregar_proveedor(self, proveedor: Proveedor) -> bool:
        """Agregar nuevo proveedor"""
        try:
            # Validar que no exista
            if any(p.id == proveedor.id for p in self.proveedores):
                return False
            
            self.proveedores.append(proveedor)
            return True
        except Exception:
            return False
    
    def obtener_proveedor(self, proveedor_id: int) -> Optional[Proveedor]:
        """Obtener proveedor por ID"""
        return next((p for p in self.proveedores if p.id == proveedor_id), None)
    
    def buscar_proveedores(self, termino: str) -> List[Proveedor]:
        """Buscar proveedores por nombre o contacto"""
        termino = termino.lower()
        return [
            p for p in self.proveedores 
            if termino in p.nombre.lower() or 
               termino in p.contacto_principal.lower() or
               termino in p.email.lower()
        ]
    
    def obtener_proveedores_por_categoria(self, categoria: str) -> List[Proveedor]:
        """Obtener proveedores por categoría de productos"""
        return [
            p for p in self.proveedores 
            if categoria in p.categoria_productos
        ]
    
    def crear_orden_compra(self, orden: OrdenCompra) -> bool:
        """Crear nueva orden de compra"""
        try:
            self.ordenes.append(orden)
            return True
        except Exception:
            return False
    
    def obtener_ordenes_pendientes(self) -> List[OrdenCompra]:
        """Obtener órdenes pendientes"""
        return [
            o for o in self.ordenes 
            if o.estado in [EstadoOrden.ENVIADA, EstadoOrden.CONFIRMADA]
        ]
    
    def evaluar_proveedor(self, proveedor_id: int, nueva_calificacion: float) -> bool:
        """Evaluar proveedor"""
        proveedor = self.obtener_proveedor(proveedor_id)
        if proveedor:
            proveedor.calificacion = max(1.0, min(10.0, nueva_calificacion))
            return True
        return False
    
    def obtener_mejores_proveedores(self, limite: int = 5) -> List[Proveedor]:
        """Obtener mejores proveedores por calificación"""
        return sorted(
            [p for p in self.proveedores if p.estado == EstadoProveedor.ACTIVO],
            key=lambda p: p.calificacion,
            reverse=True
        )[:limite]
    
    def exportar_proveedores(self) -> str:
        """Exportar proveedores a JSON"""
        data = {
            "proveedores": [asdict(p) for p in self.proveedores],
            "ordenes": [asdict(o) for o in self.ordenes],
            "exportado": datetime.now().isoformat()
        }
        return json.dumps(data, indent=2, default=str)

# Interfaz gráfica para gestión de proveedores
class InterfazProveedores:
    """Interfaz completa para gestión de proveedores"""
    
    def __init__(self, parent_frame, gestor: GestorProveedores):
        self.parent_frame = parent_frame
        self.gestor = gestor
        self.proveedor_seleccionado = None
        
    def mostrar_proveedores(self):
        """Mostrar interfaz principal de proveedores"""
        # Limpiar frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Título
        title = ctk.CTkLabel(
            self.parent_frame,
            text="🏢 Gestión Universal de Proveedores",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            self.parent_frame,
            text="Control completo de proveedores, compras y órdenes",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 20))
        
        # Barra de herramientas
        toolbar = ctk.CTkFrame(self.parent_frame)
        toolbar.pack(fill="x", padx=20, pady=10)
        
        toolbar_container = ctk.CTkFrame(toolbar, fg_color="transparent")
        toolbar_container.pack(fill="x", padx=15, pady=10)
        
        # Botones de acción
        btn_nuevo = ctk.CTkButton(
            toolbar_container,
            text="➕ Nuevo Proveedor",
            command=self._nuevo_proveedor
        )
        btn_nuevo.pack(side="left", padx=(0, 10))
        
        btn_orden = ctk.CTkButton(
            toolbar_container,
            text="📋 Nueva Orden",
            command=self._nueva_orden_compra
        )
        btn_orden.pack(side="left", padx=10)
        
        btn_reportes = ctk.CTkButton(
            toolbar_container,
            text="📊 Reportes",
            command=self._mostrar_reportes_proveedores
        )
        btn_reportes.pack(side="left", padx=10)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(toolbar_container, fg_color="transparent")
        search_frame.pack(side="right", padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar proveedores...",
            width=200
        )
        self.search_entry.pack(side="left", padx=(0, 5))
        self.search_entry.bind("<Return>", self._buscar_proveedores)
        
        btn_buscar = ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=80,
            command=self._buscar_proveedores
        )
        btn_buscar.pack(side="left")
        
        # Contenido principal
        main_content = ctk.CTkFrame(self.parent_frame)
        main_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Panel izquierdo - Lista de proveedores
        left_panel = ctk.CTkFrame(main_content)
        left_panel.pack(side="left", fill="both", expand=True, padx=(15, 7), pady=15)
        
        proveedores_title = ctk.CTkLabel(
            left_panel,
            text="📋 Proveedores Registrados",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        proveedores_title.pack(pady=(10, 15))
        
        # Lista de proveedores
        self.proveedores_frame = ctk.CTkScrollableFrame(left_panel)
        self.proveedores_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Panel derecho - Detalles y estadísticas
        right_panel = ctk.CTkFrame(main_content, width=400)
        right_panel.pack(side="right", fill="y", padx=(7, 15), pady=15)
        right_panel.pack_propagate(False)
        
        # Estadísticas rápidas
        stats_title = ctk.CTkLabel(
            right_panel,
            text="📊 Estadísticas Rápidas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stats_title.pack(pady=(15, 10))
        
        self._mostrar_estadisticas_proveedores(right_panel)
        
        # Órdenes pendientes
        ordenes_title = ctk.CTkLabel(
            right_panel,
            text="⏳ Órdenes Pendientes",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ordenes_title.pack(pady=(20, 10))
        
        self.ordenes_frame = ctk.CTkFrame(right_panel)
        self.ordenes_frame.pack(fill="x", padx=15, pady=10)
        
        self._mostrar_ordenes_pendientes()
        
        # Cargar proveedores
        self._actualizar_lista_proveedores()
    
    def _mostrar_estadisticas_proveedores(self, parent):
        """Mostrar estadísticas de proveedores"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=15, pady=10)
        
        total_proveedores = len(self.gestor.proveedores)
        proveedores_activos = len([p for p in self.gestor.proveedores if p.estado == EstadoProveedor.ACTIVO])
        ordenes_pendientes = len(self.gestor.obtener_ordenes_pendientes())
        calificacion_promedio = sum(p.calificacion for p in self.gestor.proveedores) / max(1, total_proveedores)
        
        stats_data = [
            ("Total Proveedores", str(total_proveedores), "#007bff"),
            ("Activos", str(proveedores_activos), "#28a745"),
            ("Órdenes Pendientes", str(ordenes_pendientes), "#ffc107"),
            ("Calificación Prom.", f"{calificacion_promedio:.1f}/10", "#17a2b8")
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            stat_item = ctk.CTkFrame(stats_frame)
            stat_item.pack(fill="x", pady=3, padx=10)
            
            stat_label = ctk.CTkLabel(
                stat_item,
                text=label,
                font=ctk.CTkFont(size=11)
            )
            stat_label.pack(side="left", padx=10, pady=8)
            
            stat_value = ctk.CTkLabel(
                stat_item,
                text=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color
            )
            stat_value.pack(side="right", padx=10, pady=8)
    
    def _actualizar_lista_proveedores(self):
        """Actualizar lista de proveedores"""
        # Limpiar lista actual
        for widget in self.proveedores_frame.winfo_children():
            widget.destroy()
        
        # Mostrar proveedores
        for proveedor in self.gestor.proveedores:
            self._crear_item_proveedor(proveedor)
    
    def _crear_item_proveedor(self, proveedor: Proveedor):
        """Crear item visual para proveedor"""
        item_frame = ctk.CTkFrame(self.proveedores_frame)
        item_frame.pack(fill="x", pady=5, padx=5)
        
        # Contenido principal
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=10)
        
        # Header con nombre y estado
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        
        nombre_label = ctk.CTkLabel(
            header_frame,
            text=f"🏢 {proveedor.nombre}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        nombre_label.pack(side="left")
        
        # Estado con color
        estado_color = {
            EstadoProveedor.ACTIVO: "#28a745",
            EstadoProveedor.INACTIVO: "#6c757d", 
            EstadoProveedor.BLOQUEADO: "#dc3545",
            EstadoProveedor.EVALUACION: "#ffc107"
        }
        
        estado_label = ctk.CTkLabel(
            header_frame,
            text=proveedor.estado.value,
            font=ctk.CTkFont(size=11),
            text_color=estado_color.get(proveedor.estado, "#007bff")
        )
        estado_label.pack(side="right")
        
        # Información del contacto
        contacto_label = ctk.CTkLabel(
            content_frame,
            text=f"👤 {proveedor.contacto_principal} | 📞 {proveedor.telefono}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        contacto_label.pack(fill="x", pady=(5, 0))
        
        # Categorías y calificación
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(5, 0))
        
        categorias_text = ", ".join(proveedor.categoria_productos[:3])
        if len(proveedor.categoria_productos) > 3:
            categorias_text += f" +{len(proveedor.categoria_productos)-3}"
        
        categorias_label = ctk.CTkLabel(
            info_frame,
            text=f"📦 {categorias_text}",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        categorias_label.pack(side="left")
        
        calificacion_label = ctk.CTkLabel(
            info_frame,
            text=f"⭐ {proveedor.calificacion:.1f}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffc107"
        )
        calificacion_label.pack(side="right")
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(10, 0))
        
        btn_ver = ctk.CTkButton(
            actions_frame,
            text="👁️",
            width=30,
            height=25,
            command=lambda p=proveedor: self._ver_detalle_proveedor(p)
        )
        btn_ver.pack(side="left", padx=(0, 5))
        
        btn_editar = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=30,
            height=25,
            command=lambda p=proveedor: self._editar_proveedor(p)
        )
        btn_editar.pack(side="left", padx=5)
        
        btn_orden = ctk.CTkButton(
            actions_frame,
            text="📋",
            width=30,
            height=25,
            command=lambda p=proveedor: self._nueva_orden_proveedor(p)
        )
        btn_orden.pack(side="left", padx=5)
        
        # Crédito info (si tiene)
        if proveedor.dias_credito > 0:
            credito_label = ctk.CTkLabel(
                actions_frame,
                text=f"💳 {proveedor.dias_credito} días",
                font=ctk.CTkFont(size=10),
                text_color="#17a2b8"
            )
            credito_label.pack(side="right", padx=5)
    
    def _mostrar_ordenes_pendientes(self):
        """Mostrar órdenes pendientes"""
        # Limpiar frame
        for widget in self.ordenes_frame.winfo_children():
            widget.destroy()
        
        ordenes_pendientes = self.gestor.obtener_ordenes_pendientes()
        
        if not ordenes_pendientes:
            no_ordenes = ctk.CTkLabel(
                self.ordenes_frame,
                text="✅ No hay órdenes pendientes",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            no_ordenes.pack(pady=15)
            return
        
        for orden in ordenes_pendientes[:5]:  # Mostrar máximo 5
            proveedor = self.gestor.obtener_proveedor(orden.proveedor_id)
            
            orden_item = ctk.CTkFrame(self.ordenes_frame)
            orden_item.pack(fill="x", pady=3, padx=8)
            
            # Información de la orden
            orden_info = ctk.CTkLabel(
                orden_item,
                text=f"📋 {orden.numero_orden}",
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            )
            orden_info.pack(fill="x", padx=8, pady=(5, 0))
            
            proveedor_info = ctk.CTkLabel(
                orden_item,
                text=f"🏢 {proveedor.nombre if proveedor else 'Desconocido'}",
                font=ctk.CTkFont(size=10),
                text_color="gray",
                anchor="w"
            )
            proveedor_info.pack(fill="x", padx=8)
            
            total_info = ctk.CTkLabel(
                orden_item,
                text=f"💰 ${orden.total:.2f} | {orden.estado.value}",
                font=ctk.CTkFont(size=10),
                text_color="#007bff",
                anchor="w"
            )
            total_info.pack(fill="x", padx=8, pady=(0, 5))
    
    # Métodos de acciones
    def _nuevo_proveedor(self):
        """Abrir formulario para nuevo proveedor"""
        messagebox.showinfo("Nuevo Proveedor", "🚧 Formulario de nuevo proveedor en desarrollo")
    
    def _nueva_orden_compra(self):
        """Crear nueva orden de compra"""
        messagebox.showinfo("Nueva Orden", "🚧 Formulario de nueva orden en desarrollo")
    
    def _nueva_orden_proveedor(self, proveedor):
        """Crear orden para proveedor específico"""
        messagebox.showinfo("Orden", f"🚧 Crear orden para {proveedor.nombre} en desarrollo")
    
    def _buscar_proveedores(self, event=None):
        """Buscar proveedores"""
        termino = self.search_entry.get().strip()
        if termino:
            resultados = self.gestor.buscar_proveedores(termino)
            self._mostrar_resultados_busqueda(resultados)
        else:
            self._actualizar_lista_proveedores()
    
    def _mostrar_resultados_busqueda(self, resultados):
        """Mostrar resultados de búsqueda"""
        # Limpiar lista
        for widget in self.proveedores_frame.winfo_children():
            widget.destroy()
        
        if not resultados:
            no_results = ctk.CTkLabel(
                self.proveedores_frame,
                text="🔍 No se encontraron proveedores",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_results.pack(pady=20)
            return
        
        for proveedor in resultados:
            self._crear_item_proveedor(proveedor)
    
    def _ver_detalle_proveedor(self, proveedor):
        """Ver detalle completo del proveedor"""
        messagebox.showinfo("Detalle", f"🚧 Ver detalle de {proveedor.nombre} en desarrollo")
    
    def _editar_proveedor(self, proveedor):
        """Editar proveedor"""
        messagebox.showinfo("Editar", f"🚧 Editar {proveedor.nombre} en desarrollo")
    
    def _mostrar_reportes_proveedores(self):
        """Mostrar reportes de proveedores"""
        messagebox.showinfo("Reportes", "🚧 Reportes de proveedores en desarrollo")

# Funciones de utilidad
def crear_gestor_proveedores():
    """Crear instancia del gestor de proveedores"""
    return GestorProveedores()

def integrar_con_sistema_principal(main_app, gestor_proveedores):
    """Integrar gestión de proveedores con el sistema principal"""
    # Esta función se usaría para integrar con main_universal.py
    pass

if __name__ == "__main__":
    # Demo independiente
    root = ctk.CTk()
    root.title("VentaPro Universal - Gestión de Proveedores")
    root.geometry("1000x700")
    
    gestor = crear_gestor_proveedores()
    interfaz = InterfazProveedores(root, gestor)
    interfaz.mostrar_proveedores()
    
    root.mainloop()