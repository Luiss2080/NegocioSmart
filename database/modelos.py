"""
Modelos de Datos - NegocioSmart
===========================

Define las clases/modelos de datos que representan las entidades
del sistema de gestión de ventas e inventario.

Autor: Sistema NegocioSmart
Fecha: 2025-10-04
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List

CENTAVO = Decimal('0.01')


def _redondear_centavos(valor: Decimal) -> Decimal:
    """Redondea un Decimal a 2 decimales (centavos) con HALF_UP.

    Usar Decimal.quantize en cada punto en que un monto se "cierra"
    (subtotal de línea, impuestos, total) evita que se arrastren
    residuos binarios como los que produce el float nativo de Python
    (p. ej. 0.1 + 0.2 == 0.30000000000000004). Con Decimal + quantize
    el resultado siempre es exacto a 2 decimales.
    """
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)

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
        """Calcula el subtotal de la línea.

        Casos límite manejados explícitamente para que una venta nunca
        quede con montos inconsistentes:

        - Cantidad negativa o cero: no representa una venta real (una
          cantidad negativa "vendería al revés" y devolvería dinero sin
          pasar por un flujo de devolución explícito), así que se trata
          como 0 unidades.
        - Descuento de línea mayor al importe de la línea (por ejemplo
          un descuento del 150%, o un error de captura): se limita
          ("clampa") al importe bruto de la línea para que el subtotal
          nunca sea negativo. Un descuento igual al importe bruto
          (100%) es válido y da subtotal 0.
        """
        cantidad = self.cantidad if self.cantidad > 0 else 0
        importe_bruto = self.precio_unitario * cantidad
        descuento = self.descuento_linea if self.descuento_linea > 0 else Decimal('0.00')
        descuento_aplicado = min(descuento, importe_bruto)

        subtotal = _redondear_centavos(importe_bruto - descuento_aplicado)
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
    
    def calcular_totales(self, tasa_impuesto: Decimal = Decimal('0.16')):
        """Calcula los totales de la venta.

        Args:
            tasa_impuesto: tasa de impuesto a aplicar sobre el subtotal
                con descuento (por defecto 16%, IVA típico). Se recibe
                como parámetro en vez de quedar fijo en el código para
                que quien arme la venta pueda usar la tasa configurada
                del negocio (ver ``configuracion``/``config.ini``:
                ``tax_rate``) en lugar de un valor hardcodeado.

        Casos límite manejados:
        - Un descuento general mayor al subtotal (p. ej. una promoción
          mal aplicada, o 100%+ de descuento) se limita al subtotal:
          nunca se cobran impuestos sobre un monto negativo, y el total
          nunca puede quedar por debajo de 0.
        - Todos los montos intermedios se redondean a centavos con
          Decimal.quantize (ROUND_HALF_UP) para que el total sea
          siempre exacto, sin arrastre de errores de punto flotante.
        """
        self.subtotal = _redondear_centavos(
            sum((detalle.subtotal_linea for detalle in self.detalles), Decimal('0.00'))
        )

        # Un descuento general nunca puede exceder el subtotal ni ser negativo.
        descuento = self.descuento if self.descuento > 0 else Decimal('0.00')
        self.descuento = min(descuento, self.subtotal)

        subtotal_con_descuento = self.subtotal - self.descuento
        self.impuestos = _redondear_centavos(subtotal_con_descuento * tasa_impuesto)
        self.total = _redondear_centavos(subtotal_con_descuento + self.impuestos)
    
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