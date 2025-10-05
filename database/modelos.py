"""
Modelos de Datos - VentaPro
===========================

Define las clases/modelos de datos que representan las entidades
del sistema de gestión de ventas e inventario.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

@dataclass
class Categoria:
    """Modelo para categorías de productos"""
    id: Optional[int] = None
    nombre: str = ""
    descripcion: str = ""
    activa: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_modificacion: datetime = field(default_factory=datetime.now)

@dataclass
class Producto:
    """Modelo para productos del inventario"""
    id: Optional[int] = None
    codigo: str = ""
    nombre: str = ""
    descripcion: str = ""
    categoria_id: Optional[int] = None
    precio_compra: Decimal = Decimal('0.00')
    precio_venta: Decimal = Decimal('0.00')
    stock_actual: int = 0
    stock_minimo: int = 0
    unidad_medida: str = "pza"
    imagen: str = ""
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_modificacion: datetime = field(default_factory=datetime.now)
    
    # Propiedades calculadas
    @property
    def margen_ganancia(self) -> Decimal:
        """Calcula el margen de ganancia"""
        if self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return Decimal('0.00')
    
    @property
    def stock_bajo(self) -> bool:
        """Indica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo

@dataclass
class Cliente:
    """Modelo para clientes"""
    id: Optional[int] = None
    codigo: str = ""
    nombre: str = ""
    apellidos: str = ""
    email: str = ""
    telefono: str = ""
    direccion: str = ""
    rfc: str = ""
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_modificacion: datetime = field(default_factory=datetime.now)
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del cliente"""
        return f"{self.nombre} {self.apellidos}".strip()

@dataclass
class DetalleVenta:
    """Modelo para el detalle de ventas"""
    id: Optional[int] = None
    venta_id: Optional[int] = None
    producto_id: int = 0
    cantidad: int = 0
    precio_unitario: Decimal = Decimal('0.00')
    descuento_linea: Decimal = Decimal('0.00')
    subtotal_linea: Decimal = Decimal('0.00')
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    # Referencias (se llenarán al cargar desde BD)
    producto: Optional[Producto] = None
    
    def calcular_subtotal(self) -> Decimal:
        """Calcula el subtotal de la línea"""
        subtotal = (self.precio_unitario * self.cantidad) - self.descuento_linea
        self.subtotal_linea = subtotal
        return subtotal

@dataclass
class Venta:
    """Modelo para ventas"""
    id: Optional[int] = None
    folio: str = ""
    cliente_id: Optional[int] = None
    subtotal: Decimal = Decimal('0.00')
    descuento: Decimal = Decimal('0.00')
    impuestos: Decimal = Decimal('0.00')
    total: Decimal = Decimal('0.00')
    metodo_pago: str = "efectivo"
    estado: str = "completada"
    fecha_venta: datetime = field(default_factory=datetime.now)
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    # Referencias y detalles
    cliente: Optional[Cliente] = None
    detalles: List[DetalleVenta] = field(default_factory=list)
    
    def calcular_totales(self):
        """Calcula los totales de la venta"""
        self.subtotal = sum(detalle.subtotal_linea for detalle in self.detalles)
        # Aplicar descuento general si existe
        subtotal_con_descuento = self.subtotal - self.descuento
        # Calcular impuestos (IVA 16%)
        self.impuestos = subtotal_con_descuento * Decimal('0.16')
        # Total final
        self.total = subtotal_con_descuento + self.impuestos
    
    @property
    def cantidad_productos(self) -> int:
        """Retorna la cantidad total de productos en la venta"""
        return sum(detalle.cantidad for detalle in self.detalles)

@dataclass
class Usuario:
    """Modelo para usuarios del sistema"""
    id: Optional[int] = None
    usuario: str = ""
    password_hash: str = ""
    nombre: str = ""
    email: str = ""
    rol: str = "vendedor"  # admin, vendedor, supervisor
    activo: bool = True
    ultimo_acceso: Optional[datetime] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)

@dataclass
class Configuracion:
    """Modelo para configuración del sistema"""
    id: Optional[int] = None
    clave: str = ""
    valor: str = ""
    descripcion: str = ""
    tipo: str = "string"  # string, int, float, bool, date
    fecha_modificacion: datetime = field(default_factory=datetime.now)

@dataclass
class LogEntry:
    """Modelo para entradas de log"""
    id: Optional[int] = None
    nivel: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    modulo: str = ""
    mensaje: str = ""
    usuario_id: Optional[int] = None
    ip_address: str = ""
    fecha_creacion: datetime = field(default_factory=datetime.now)

# Enumeraciones y constantes
class EstadoVenta:
    """Estados posibles de una venta"""
    BORRADOR = "borrador"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    DEVUELTA = "devuelta"

class MetodoPago:
    """Métodos de pago disponibles"""
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    CHEQUE = "cheque"
    CREDITO = "credito"

class RolUsuario:
    """Roles de usuario en el sistema"""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    VENDEDOR = "vendedor"
    CONSULTA = "consulta"

class UnidadMedida:
    """Unidades de medida para productos"""
    PIEZA = "pza"
    KILOGRAMO = "kg"
    LITRO = "lt"
    METRO = "mts"
    CAJA = "caja"
    PAQUETE = "paq"