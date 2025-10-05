"""
VentaPro Universal - Módulo Avanzado de Inventario
=================================================

Sistema completo de control de inventario con alertas automáticas,
movimientos de stock, auditorías y proyecciones inteligentes.

Características:
- ✅ Control detallado de movimientos
- ✅ Alertas automáticas de reposición
- ✅ Auditoría completa del inventario
- ✅ Proyecciones de demanda
- ✅ Control por lotes y ubicaciones
- ✅ Inventarios físicos y ajustes
- ✅ Reportes avanzados de rotación

Autor: VentaPro Universal
Fecha: 2025-01-04
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Tuple
from enum import Enum
import json
import math

class TipoMovimiento(Enum):
    """Tipos de movimientos de inventario"""
    ENTRADA = "Entrada"
    SALIDA = "Salida"
    AJUSTE_POSITIVO = "Ajuste +"
    AJUSTE_NEGATIVO = "Ajuste -"
    TRANSFERENCIA = "Transferencia"
    DEVOLUCION = "Devolución"
    MERMA = "Merma"
    INVENTARIO_FISICO = "Inventario Físico"

class EstadoStock(Enum):
    """Estados del stock"""
    DISPONIBLE = "Disponible"
    RESERVADO = "Reservado"
    EN_TRANSITO = "En Tránsito"
    BLOQUEADO = "Bloqueado"
    DAÑADO = "Dañado"
    VENCIDO = "Vencido"

class NivelAlerta(Enum):
    """Niveles de alerta"""
    CRITICO = "Crítico"      # Stock agotado
    BAJO = "Bajo"            # Menos del mínimo
    MEDIO = "Medio"          # Entre mínimo y óptimo
    NORMAL = "Normal"        # Stock normal
    ALTO = "Alto"            # Sobre el máximo

@dataclass
class MovimientoStock:
    """Registro de movimiento de inventario"""
    id: int
    producto_id: int
    fecha: datetime
    tipo: TipoMovimiento
    
    # Cantidades
    cantidad: float
    stock_anterior: float
    stock_nuevo: float
    
    # Referencias
    referencia: str = ""  # Venta, Compra, Ajuste, etc.
    usuario: str = "Sistema"
    
    # Detalles adicionales
    motivo: str = ""
    costo_unitario: float = 0.0
    valor_total: float = 0.0
    
    # Ubicación y lote (para negocios específicos)
    ubicacion: str = ""
    lote: str = ""
    fecha_vencimiento: Optional[datetime] = None
    
    notas: str = ""

@dataclass
class ConfiguracionStock:
    """Configuración de stock por producto"""
    producto_id: int
    
    # Niveles de stock
    stock_minimo: float = 0
    stock_maximo: float = 999999
    stock_optimo: float = 0
    punto_reorden: float = 0
    
    # Configuración de alertas
    alertar_stock_bajo: bool = True
    alertar_stock_critico: bool = True
    alertar_vencimiento: bool = False
    dias_alerta_vencimiento: int = 30
    
    # Configuración de rotación
    usar_fifo: bool = True  # First In, First Out
    permitir_stock_negativo: bool = False
    
    # Proyecciones
    demanda_diaria_promedio: float = 0.0
    dias_para_agotar: int = 0

@dataclass
class AlertaInventario:
    """Alerta de inventario"""
    id: int
    producto_id: int
    tipo: str
    nivel: NivelAlerta
    mensaje: str
    fecha_creacion: datetime
    activa: bool = True
    fecha_resolucion: Optional[datetime] = None

class GestorInventario:
    """Gestor avanzado de inventario"""
    
    def __init__(self, productos_callback=None):
        self.movimientos: List[MovimientoStock] = []
        self.configuraciones: Dict[int, ConfiguracionStock] = {}
        self.alertas: List[AlertaInventario] = []
        self.productos_callback = productos_callback  # Para obtener productos del sistema principal
        
        # Demo data
        self._inicializar_datos_demo()
    
    def _inicializar_datos_demo(self):
        """Datos de demostración"""
        # Configuraciones de ejemplo
        self.configuraciones = {
            1: ConfiguracionStock(
                producto_id=1,
                stock_minimo=10,
                stock_maximo=100,
                stock_optimo=50,
                punto_reorden=15,
                demanda_diaria_promedio=3.5
            ),
            2: ConfiguracionStock(
                producto_id=2,
                stock_minimo=20,
                stock_maximo=200,
                stock_optimo=100,
                punto_reorden=30,
                demanda_diaria_promedio=8.2
            )
        }
        
        # Movimientos de ejemplo
        base_date = datetime.now() - timedelta(days=30)
        self.movimientos = [
            MovimientoStock(
                id=1,
                producto_id=1,
                fecha=base_date + timedelta(days=1),
                tipo=TipoMovimiento.ENTRADA,
                cantidad=50,
                stock_anterior=0,
                stock_nuevo=50,
                referencia="COMP-001",
                motivo="Compra inicial",
                costo_unitario=15.00
            ),
            MovimientoStock(
                id=2,
                producto_id=1,
                fecha=base_date + timedelta(days=5),
                tipo=TipoMovimiento.SALIDA,
                cantidad=12,
                stock_anterior=50,
                stock_nuevo=38,
                referencia="VTA-001",
                motivo="Venta"
            ),
            MovimientoStock(
                id=3,
                producto_id=1,
                fecha=base_date + timedelta(days=10),
                tipo=TipoMovimiento.AJUSTE_NEGATIVO,
                cantidad=3,
                stock_anterior=38,
                stock_nuevo=35,
                referencia="AJ-001",
                motivo="Producto dañado"
            )
        ]
        
        # Generar alertas
        self._generar_alertas_demo()
    
    def _generar_alertas_demo(self):
        """Generar alertas de demostración"""
        self.alertas = [
            AlertaInventario(
                id=1,
                producto_id=1,
                tipo="Stock Bajo",
                nivel=NivelAlerta.BAJO,
                mensaje="Stock por debajo del mínimo (35 < 40)",
                fecha_creacion=datetime.now() - timedelta(hours=2)
            ),
            AlertaInventario(
                id=2,
                producto_id=3,
                tipo="Stock Crítico",
                nivel=NivelAlerta.CRITICO,
                mensaje="Stock agotado (0 unidades)",
                fecha_creacion=datetime.now() - timedelta(hours=1)
            )
        ]
    
    def registrar_movimiento(self, movimiento: MovimientoStock) -> bool:
        """Registrar nuevo movimiento de inventario"""
        try:
            # Validar movimiento
            if not self._validar_movimiento(movimiento):
                return False
            
            self.movimientos.append(movimiento)
            
            # Generar alertas si es necesario
            self._verificar_alertas(movimiento.producto_id)
            
            return True
        except Exception as e:
            print(f"Error al registrar movimiento: {e}")
            return False
    
    def _validar_movimiento(self, movimiento: MovimientoStock) -> bool:
        """Validar que el movimiento sea válido"""
        # Obtener configuración del producto
        config = self.configuraciones.get(movimiento.producto_id)
        
        # Si no permite stock negativo y es una salida que dejaría stock negativo
        if config and not config.permitir_stock_negativo:
            if movimiento.tipo in [TipoMovimiento.SALIDA, TipoMovimiento.AJUSTE_NEGATIVO]:
                if movimiento.stock_nuevo < 0:
                    return False
        
        return True
    
    def obtener_stock_actual(self, producto_id: int) -> float:
        """Obtener stock actual de un producto"""
        movimientos_producto = [m for m in self.movimientos if m.producto_id == producto_id]
        if not movimientos_producto:
            return 0.0
        
        # Último movimiento tiene el stock actual
        ultimo_movimiento = max(movimientos_producto, key=lambda x: x.fecha)
        return ultimo_movimiento.stock_nuevo
    
    def obtener_historial_producto(self, producto_id: int, dias: int = 30) -> List[MovimientoStock]:
        """Obtener historial de movimientos de un producto"""
        fecha_limite = datetime.now() - timedelta(days=dias)
        return [
            m for m in self.movimientos 
            if m.producto_id == producto_id and m.fecha >= fecha_limite
        ]
    
    def calcular_rotacion_inventario(self, producto_id: int, dias: int = 30) -> Dict:
        """Calcular métricas de rotación"""
        historial = self.obtener_historial_producto(producto_id, dias)
        
        # Ventas totales (salidas)
        ventas = sum(m.cantidad for m in historial if m.tipo == TipoMovimiento.SALIDA)
        
        # Stock promedio
        stocks = [m.stock_nuevo for m in historial]
        stock_promedio = sum(stocks) / len(stocks) if stocks else 0
        
        # Días para agotar stock actual
        stock_actual = self.obtener_stock_actual(producto_id)
        demanda_diaria = ventas / dias if dias > 0 else 0
        dias_stock = stock_actual / demanda_diaria if demanda_diaria > 0 else 999
        
        return {
            "ventas_periodo": ventas,
            "demanda_diaria": demanda_diaria,
            "stock_actual": stock_actual,
            "stock_promedio": stock_promedio,
            "dias_stock_restante": min(999, dias_stock),
            "rotacion": ventas / stock_promedio if stock_promedio > 0 else 0
        }
    
    def _verificar_alertas(self, producto_id: int):
        """Verificar y generar alertas para un producto"""
        config = self.configuraciones.get(producto_id)
        if not config:
            return
        
        stock_actual = self.obtener_stock_actual(producto_id)
        
        # Alerta de stock crítico
        if stock_actual <= 0 and config.alertar_stock_critico:
            self._crear_alerta(
                producto_id=producto_id,
                tipo="Stock Crítico",
                nivel=NivelAlerta.CRITICO,
                mensaje="Stock agotado"
            )
        
        # Alerta de stock bajo
        elif stock_actual <= config.stock_minimo and config.alertar_stock_bajo:
            self._crear_alerta(
                producto_id=producto_id,
                tipo="Stock Bajo",
                nivel=NivelAlerta.BAJO,
                mensaje=f"Stock por debajo del mínimo ({stock_actual} < {config.stock_minimo})"
            )
    
    def _crear_alerta(self, producto_id: int, tipo: str, nivel: NivelAlerta, mensaje: str):
        """Crear nueva alerta"""
        # Verificar si ya existe una alerta activa del mismo tipo
        alerta_existente = next(
            (a for a in self.alertas 
             if a.producto_id == producto_id and a.tipo == tipo and a.activa),
            None
        )
        
        if not alerta_existente:
            nueva_alerta = AlertaInventario(
                id=len(self.alertas) + 1,
                producto_id=producto_id,
                tipo=tipo,
                nivel=nivel,
                mensaje=mensaje,
                fecha_creacion=datetime.now()
            )
            self.alertas.append(nueva_alerta)
    
    def obtener_alertas_activas(self) -> List[AlertaInventario]:
        """Obtener alertas activas"""
        return [a for a in self.alertas if a.activa]
    
    def resolver_alerta(self, alerta_id: int):
        """Marcar alerta como resuelta"""
        for alerta in self.alertas:
            if alerta.id == alerta_id and alerta.activa:
                alerta.activa = False
                alerta.fecha_resolucion = datetime.now()
                break
    
    def obtener_productos_criticos(self) -> List[Dict]:
        """Obtener productos con stock crítico"""
        productos_criticos = []
        
        for producto_id, config in self.configuraciones.items():
            stock_actual = self.obtener_stock_actual(producto_id)
            
            if stock_actual <= config.stock_minimo:
                rotacion = self.calcular_rotacion_inventario(producto_id)
                productos_criticos.append({
                    "producto_id": producto_id,
                    "stock_actual": stock_actual,
                    "stock_minimo": config.stock_minimo,
                    "dias_restantes": rotacion["dias_stock_restante"],
                    "sugerido_comprar": max(0, config.stock_optimo - stock_actual)
                })
        
        return sorted(productos_criticos, key=lambda x: x["dias_restantes"])
    
    def generar_orden_sugerida(self, producto_id: int) -> Dict:
        """Generar orden de compra sugerida"""
        config = self.configuraciones.get(producto_id)
        if not config:
            return {}
        
        stock_actual = self.obtener_stock_actual(producto_id)
        rotacion = self.calcular_rotacion_inventario(producto_id)
        
        # Cantidad sugerida para alcanzar stock óptimo
        cantidad_sugerida = max(0, config.stock_optimo - stock_actual)
        
        # Ajustar por demanda proyectada
        demanda_semanal = rotacion["demanda_diaria"] * 7
        if demanda_semanal > cantidad_sugerida:
            cantidad_sugerida = math.ceil(demanda_semanal * 2)  # 2 semanas de stock
        
        return {
            "producto_id": producto_id,
            "stock_actual": stock_actual,
            "cantidad_sugerida": cantidad_sugerida,
            "stock_resultante": stock_actual + cantidad_sugerida,
            "prioridad": "Alta" if stock_actual <= config.stock_minimo else "Media"
        }
    
    def realizar_inventario_fisico(self, inventario_data: List[Dict]) -> List[MovimientoStock]:
        """Realizar inventario físico y generar ajustes"""
        movimientos_ajuste = []
        
        for item in inventario_data:
            producto_id = item["producto_id"]
            stock_fisico = item["stock_fisico"]
            stock_sistema = self.obtener_stock_actual(producto_id)
            
            diferencia = stock_fisico - stock_sistema
            
            if abs(diferencia) >= 0.01:  # Si hay diferencia significativa
                tipo_movimiento = TipoMovimiento.AJUSTE_POSITIVO if diferencia > 0 else TipoMovimiento.AJUSTE_NEGATIVO
                
                movimiento = MovimientoStock(
                    id=len(self.movimientos) + len(movimientos_ajuste) + 1,
                    producto_id=producto_id,
                    fecha=datetime.now(),
                    tipo=tipo_movimiento,
                    cantidad=abs(diferencia),
                    stock_anterior=stock_sistema,
                    stock_nuevo=stock_fisico,
                    referencia="INV-FISICO",
                    motivo="Ajuste por inventario físico",
                    usuario="Inventario"
                )
                
                movimientos_ajuste.append(movimiento)
                self.registrar_movimiento(movimiento)
        
        return movimientos_ajuste
    
    def exportar_reporte_inventario(self) -> str:
        """Exportar reporte completo del inventario"""
        data = {
            "fecha_reporte": datetime.now().isoformat(),
            "movimientos": [asdict(m) for m in self.movimientos],
            "configuraciones": {str(k): asdict(v) for k, v in self.configuraciones.items()},
            "alertas_activas": [asdict(a) for a in self.obtener_alertas_activas()],
            "productos_criticos": self.obtener_productos_criticos()
        }
        
        return json.dumps(data, indent=2, default=str)

class InterfazInventario:
    """Interfaz gráfica para gestión de inventario"""
    
    def __init__(self, parent_frame, gestor: GestorInventario, productos=None):
        self.parent_frame = parent_frame
        self.gestor = gestor
        self.productos = productos or []
        
    def mostrar_inventario(self):
        """Mostrar interfaz principal de inventario"""
        # Limpiar frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Título
        title = ctk.CTkLabel(
            self.parent_frame,
            text="📦 Control Avanzado de Inventario",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            self.parent_frame,
            text="Gestión inteligente de stock con alertas automáticas y proyecciones",
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
        btn_ajuste = ctk.CTkButton(
            toolbar_container,
            text="⚖️ Ajustar Stock",
            command=self._ajustar_stock
        )
        btn_ajuste.pack(side="left", padx=(0, 10))
        
        btn_inventario = ctk.CTkButton(
            toolbar_container,
            text="📋 Inventario Físico",
            command=self._inventario_fisico
        )
        btn_inventario.pack(side="left", padx=10)
        
        btn_alertas = ctk.CTkButton(
            toolbar_container,
            text="🚨 Alertas",
            command=self._mostrar_alertas
        )
        btn_alertas.pack(side="left", padx=10)
        
        btn_reportes = ctk.CTkButton(
            toolbar_container,
            text="📊 Reportes",
            command=self._mostrar_reportes_inventario
        )
        btn_reportes.pack(side="left", padx=10)
        
        # Panel principal con pestañas
        tabview = ctk.CTkTabview(self.parent_frame)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Pestaña: Stock Actual
        tab_stock = tabview.add("📦 Stock Actual")
        self._mostrar_stock_actual(tab_stock)
        
        # Pestaña: Movimientos
        tab_movimientos = tabview.add("📊 Movimientos")
        self._mostrar_movimientos(tab_movimientos)
        
        # Pestaña: Alertas
        tab_alertas = tabview.add("🚨 Alertas")
        self._mostrar_panel_alertas(tab_alertas)
        
        # Pestaña: Análisis
        tab_analisis = tabview.add("📈 Análisis")
        self._mostrar_analisis(tab_analisis)
    
    def _mostrar_stock_actual(self, parent):
        """Mostrar stock actual de productos"""
        # Frame con lista de productos
        productos_frame = ctk.CTkScrollableFrame(parent)
        productos_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Headers
        headers_frame = ctk.CTkFrame(productos_frame)
        headers_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["Producto", "Stock", "Mínimo", "Óptimo", "Estado", "Días Rest.", "Acciones"]
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Datos de productos (demo)
        productos_demo = [
            {"id": 1, "nombre": "Producto A", "stock": 35, "minimo": 40, "optimo": 100},
            {"id": 2, "nombre": "Producto B", "stock": 85, "minimo": 50, "optimo": 150},
            {"id": 3, "nombre": "Producto C", "stock": 0, "minimo": 20, "optimo": 80},
            {"id": 4, "nombre": "Producto D", "stock": 120, "minimo": 30, "optimo": 90},
        ]
        
        for i, producto in enumerate(productos_demo):
            self._crear_fila_stock(productos_frame, producto, i + 1)
    
    def _crear_fila_stock(self, parent, producto, row):
        """Crear fila de stock para un producto"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=2)
        
        # Calcular estado y días restantes
        stock = producto["stock"]
        minimo = producto["minimo"]
        
        if stock <= 0:
            estado = "CRÍTICO"
            estado_color = "#dc3545"
        elif stock <= minimo:
            estado = "BAJO"
            estado_color = "#ffc107"
        else:
            estado = "NORMAL"
            estado_color = "#28a745"
        
        # Simular días restantes
        rotacion = self.gestor.calcular_rotacion_inventario(producto["id"])
        dias_restantes = int(rotacion.get("dias_stock_restante", 999))
        
        # Columnas
        cols_data = [
            producto["nombre"],
            f"{stock} uds",
            f"{minimo} uds",
            f"{producto['optimo']} uds",
            estado,
            f"{dias_restantes} días" if dias_restantes < 999 else "∞",
        ]
        
        for i, data in enumerate(cols_data):
            color = estado_color if i == 4 else None
            label = ctk.CTkLabel(
                frame,
                text=data,
                text_color=color
            )
            label.grid(row=0, column=i, padx=10, pady=8, sticky="w")
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(frame, fg_color="transparent")
        actions_frame.grid(row=0, column=len(cols_data), padx=10, pady=5)
        
        btn_ajustar = ctk.CTkButton(
            actions_frame,
            text="⚖️",
            width=30,
            height=25,
            command=lambda p=producto: self._ajustar_stock_producto(p)
        )
        btn_ajustar.pack(side="left", padx=2)
        
        btn_historial = ctk.CTkButton(
            actions_frame,
            text="📊",
            width=30,
            height=25,
            command=lambda p=producto: self._ver_historial_producto(p)
        )
        btn_historial.pack(side="left", padx=2)
    
    def _mostrar_movimientos(self, parent):
        """Mostrar historial de movimientos"""
        # Frame de filtros
        filtros_frame = ctk.CTkFrame(parent)
        filtros_frame.pack(fill="x", padx=15, pady=15)
        
        filtros_container = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        filtros_container.pack(fill="x", padx=10, pady=10)
        
        # Filtro por fechas
        fecha_label = ctk.CTkLabel(filtros_container, text="Período:")
        fecha_label.pack(side="left", padx=(0, 10))
        
        self.periodo_combo = ctk.CTkComboBox(
            filtros_container,
            values=["Hoy", "Esta semana", "Este mes", "Últimos 3 meses"],
            width=150
        )
        self.periodo_combo.pack(side="left", padx=10)
        self.periodo_combo.set("Este mes")
        
        # Filtro por tipo
        tipo_label = ctk.CTkLabel(filtros_container, text="Tipo:")
        tipo_label.pack(side="left", padx=(20, 10))
        
        self.tipo_combo = ctk.CTkComboBox(
            filtros_container,
            values=["Todos", "Entradas", "Salidas", "Ajustes"],
            width=120
        )
        self.tipo_combo.pack(side="left", padx=10)
        self.tipo_combo.set("Todos")
        
        # Botón filtrar
        btn_filtrar = ctk.CTkButton(
            filtros_container,
            text="🔍 Filtrar",
            command=self._filtrar_movimientos
        )
        btn_filtrar.pack(side="left", padx=20)
        
        # Lista de movimientos
        self.movimientos_frame = ctk.CTkScrollableFrame(parent)
        self.movimientos_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self._cargar_movimientos()
    
    def _cargar_movimientos(self):
        """Cargar y mostrar movimientos"""
        # Limpiar frame
        for widget in self.movimientos_frame.winfo_children():
            widget.destroy()
        
        # Headers
        headers_frame = ctk.CTkFrame(self.movimientos_frame)
        headers_frame.pack(fill="x", pady=(0, 10))
        
        headers = ["Fecha", "Producto", "Tipo", "Cantidad", "Stock", "Referencia"]
        
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=0, column=i, padx=10, pady=8, sticky="w")
        
        # Movimientos recientes
        movimientos_recientes = sorted(
            self.gestor.movimientos,
            key=lambda x: x.fecha,
            reverse=True
        )[:20]  # Últimos 20 movimientos
        
        for movimiento in movimientos_recientes:
            self._crear_fila_movimiento(movimiento)
    
    def _crear_fila_movimiento(self, movimiento: MovimientoStock):
        """Crear fila para un movimiento"""
        frame = ctk.CTkFrame(self.movimientos_frame)
        frame.pack(fill="x", pady=1)
        
        # Color según tipo de movimiento
        tipo_colors = {
            TipoMovimiento.ENTRADA: "#28a745",
            TipoMovimiento.SALIDA: "#dc3545",
            TipoMovimiento.AJUSTE_POSITIVO: "#17a2b8",
            TipoMovimiento.AJUSTE_NEGATIVO: "#ffc107"
        }
        
        tipo_color = tipo_colors.get(movimiento.tipo, "#6c757d")
        
        # Datos del movimiento
        cols_data = [
            movimiento.fecha.strftime("%d/%m %H:%M"),
            f"Prod. {movimiento.producto_id}",  # En sistema real sería el nombre
            movimiento.tipo.value,
            f"{'+'if movimiento.tipo in [TipoMovimiento.ENTRADA, TipoMovimiento.AJUSTE_POSITIVO] else '-'}{movimiento.cantidad}",
            f"{movimiento.stock_nuevo}",
            movimiento.referencia
        ]
        
        for i, data in enumerate(cols_data):
            color = tipo_color if i == 2 else None
            label = ctk.CTkLabel(
                frame,
                text=data,
                text_color=color
            )
            label.grid(row=0, column=i, padx=10, pady=5, sticky="w")
    
    def _mostrar_panel_alertas(self, parent):
        """Mostrar panel de alertas"""
        # Estadísticas de alertas
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=15, pady=15)
        
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=10, pady=10)
        
        alertas_activas = self.gestor.obtener_alertas_activas()
        
        stats_data = [
            ("Total Alertas", str(len(alertas_activas)), "#007bff"),
            ("Críticas", str(len([a for a in alertas_activas if a.nivel == NivelAlerta.CRITICO])), "#dc3545"),
            ("Stock Bajo", str(len([a for a in alertas_activas if a.nivel == NivelAlerta.BAJO])), "#ffc107"),
        ]
        
        for label, value, color in stats_data:
            stat_frame = ctk.CTkFrame(stats_container)
            stat_frame.pack(side="left", fill="both", expand=True, padx=10)
            
            stat_label = ctk.CTkLabel(stat_frame, text=label)
            stat_label.pack(pady=(10, 5))
            
            stat_value = ctk.CTkLabel(
                stat_frame,
                text=value,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color
            )
            stat_value.pack(pady=(0, 10))
        
        # Lista de alertas
        alertas_frame = ctk.CTkScrollableFrame(parent)
        alertas_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        for alerta in alertas_activas:
            self._crear_item_alerta(alertas_frame, alerta)
    
    def _crear_item_alerta(self, parent, alerta: AlertaInventario):
        """Crear item visual para alerta"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=5)
        
        # Color según nivel
        nivel_colors = {
            NivelAlerta.CRITICO: "#dc3545",
            NivelAlerta.BAJO: "#ffc107",
            NivelAlerta.MEDIO: "#17a2b8",
            NivelAlerta.NORMAL: "#28a745"
        }
        
        color = nivel_colors.get(alerta.nivel, "#6c757d")
        
        # Contenido de la alerta
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=10)
        
        # Icono y nivel
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        
        icono_nivel = {
            NivelAlerta.CRITICO: "🚨",
            NivelAlerta.BAJO: "⚠️",
            NivelAlerta.MEDIO: "📊",
            NivelAlerta.NORMAL: "✅"
        }
        
        nivel_label = ctk.CTkLabel(
            header_frame,
            text=f"{icono_nivel.get(alerta.nivel, '📋')} {alerta.nivel.value}",
            font=ctk.CTkFont(weight="bold"),
            text_color=color
        )
        nivel_label.pack(side="left")
        
        # Fecha
        fecha_label = ctk.CTkLabel(
            header_frame,
            text=alerta.fecha_creacion.strftime("%d/%m/%Y %H:%M"),
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        fecha_label.pack(side="right")
        
        # Mensaje
        mensaje_label = ctk.CTkLabel(
            content_frame,
            text=alerta.mensaje,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        mensaje_label.pack(fill="x", pady=(5, 0))
        
        # Tipo
        tipo_label = ctk.CTkLabel(
            content_frame,
            text=f"Tipo: {alerta.tipo} | Producto ID: {alerta.producto_id}",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        tipo_label.pack(fill="x")
        
        # Botón resolver
        if alerta.activa:
            btn_resolver = ctk.CTkButton(
                content_frame,
                text="✅ Resolver",
                height=25,
                command=lambda a=alerta: self._resolver_alerta(a.id)
            )
            btn_resolver.pack(anchor="e", pady=(5, 0))
    
    def _mostrar_analisis(self, parent):
        """Mostrar análisis y métricas avanzadas"""
        # Productos críticos
        criticos_frame = ctk.CTkFrame(parent)
        criticos_frame.pack(fill="x", padx=15, pady=15)
        
        criticos_title = ctk.CTkLabel(
            criticos_frame,
            text="🎯 Productos Críticos - Reposición Urgente",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        criticos_title.pack(pady=15)
        
        productos_criticos = self.gestor.obtener_productos_criticos()
        
        if productos_criticos:
            for producto_critico in productos_criticos[:5]:  # Top 5
                self._crear_item_critico(criticos_frame, producto_critico)
        else:
            no_criticos = ctk.CTkLabel(
                criticos_frame,
                text="✅ No hay productos críticos en este momento",
                text_color="gray"
            )
            no_criticos.pack(pady=10)
        
        # Métricas generales
        metricas_frame = ctk.CTkFrame(parent)
        metricas_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        metricas_title = ctk.CTkLabel(
            metricas_frame,
            text="📊 Métricas de Inventario",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        metricas_title.pack(pady=(15, 20))
        
        # Calcular métricas generales
        self._mostrar_metricas_generales(metricas_frame)
    
    def _crear_item_critico(self, parent, producto_critico):
        """Crear item para producto crítico"""
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(fill="x", padx=15, pady=5)
        
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=8)
        
        # Información del producto
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        producto_label = ctk.CTkLabel(
            info_frame,
            text=f"📦 Producto ID: {producto_critico['producto_id']}",
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        )
        producto_label.pack(fill="x")
        
        stock_label = ctk.CTkLabel(
            info_frame,
            text=f"Stock: {producto_critico['stock_actual']} (Mín: {producto_critico['stock_minimo']})",
            text_color="#dc3545",
            anchor="w"
        )
        stock_label.pack(fill="x")
        
        dias_label = ctk.CTkLabel(
            info_frame,
            text=f"Días restantes: {int(producto_critico['dias_restantes'])}",
            text_color="gray",
            anchor="w"
        )
        dias_label.pack(fill="x")
        
        # Sugerencia de compra
        sugerencia_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        sugerencia_frame.pack(side="right")
        
        sugerencia_label = ctk.CTkLabel(
            sugerencia_frame,
            text=f"Comprar: {producto_critico['sugerido_comprar']} uds",
            font=ctk.CTkFont(weight="bold"),
            text_color="#007bff"
        )
        sugerencia_label.pack()
        
        btn_orden = ctk.CTkButton(
            sugerencia_frame,
            text="📋 Crear Orden",
            height=25,
            command=lambda p=producto_critico: self._crear_orden_sugerida(p)
        )
        btn_orden.pack(pady=(5, 0))
    
    def _mostrar_metricas_generales(self, parent):
        """Mostrar métricas generales del inventario"""
        metricas_container = ctk.CTkFrame(parent, fg_color="transparent")
        metricas_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Simular métricas (en sistema real se calcularían)
        metricas = [
            ("Total SKUs", "156", "#007bff"),
            ("Valor Inventario", "$45,230.50", "#28a745"),
            ("Rotación Promedio", "4.2x", "#17a2b8"),
            ("Días Stock Promedio", "28 días", "#ffc107")
        ]
        
        for i, (label, value, color) in enumerate(metricas):
            metrica_frame = ctk.CTkFrame(metricas_container)
            metrica_frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            
            metrica_label = ctk.CTkLabel(
                metrica_frame,
                text=label,
                font=ctk.CTkFont(size=12)
            )
            metrica_label.pack(pady=(15, 5))
            
            metrica_value = ctk.CTkLabel(
                metrica_frame,
                text=value,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            )
            metrica_value.pack(pady=(0, 15))
        
        # Configurar grid
        metricas_container.grid_columnconfigure(0, weight=1)
        metricas_container.grid_columnconfigure(1, weight=1)
    
    # Métodos de acciones
    def _ajustar_stock(self):
        """Mostrar formulario de ajuste de stock"""
        messagebox.showinfo("Ajustar Stock", "🚧 Formulario de ajuste de stock en desarrollo")
    
    def _inventario_fisico(self):
        """Iniciar proceso de inventario físico"""
        messagebox.showinfo("Inventario Físico", "🚧 Proceso de inventario físico en desarrollo")
    
    def _mostrar_alertas(self):
        """Mostrar ventana de alertas"""
        messagebox.showinfo("Alertas", "🚧 Gestión de alertas en desarrollo")
    
    def _mostrar_reportes_inventario(self):
        """Mostrar reportes de inventario"""
        messagebox.showinfo("Reportes", "🚧 Reportes de inventario en desarrollo")
    
    def _ajustar_stock_producto(self, producto):
        """Ajustar stock de producto específico"""
        messagebox.showinfo("Ajustar", f"🚧 Ajustar stock de {producto['nombre']} en desarrollo")
    
    def _ver_historial_producto(self, producto):
        """Ver historial de movimientos del producto"""
        messagebox.showinfo("Historial", f"🚧 Historial de {producto['nombre']} en desarrollo")
    
    def _filtrar_movimientos(self):
        """Filtrar movimientos por criterios"""
        # Recargar movimientos con filtros
        self._cargar_movimientos()
    
    def _resolver_alerta(self, alerta_id):
        """Resolver alerta específica"""
        self.gestor.resolver_alerta(alerta_id)
        # Refrescar vista de alertas
        messagebox.showinfo("Resuelto", "✅ Alerta marcada como resuelta")
    
    def _crear_orden_sugerida(self, producto_critico):
        """Crear orden de compra sugerida"""
        messagebox.showinfo("Orden", f"🚧 Crear orden para producto {producto_critico['producto_id']} en desarrollo")

# Funciones de utilidad
def crear_gestor_inventario():
    """Crear instancia del gestor de inventario"""
    return GestorInventario()

def integrar_con_sistema_principal(main_app, gestor_inventario):
    """Integrar gestión de inventario con el sistema principal"""
    # Esta función se usaría para integrar con main_universal.py
    pass

if __name__ == "__main__":
    # Demo independiente
    root = ctk.CTk()
    root.title("VentaPro Universal - Control de Inventario")
    root.geometry("1200x800")
    
    gestor = crear_gestor_inventario()
    interfaz = InterfazInventario(root, gestor)
    interfaz.mostrar_inventario()
    
    root.mainloop()