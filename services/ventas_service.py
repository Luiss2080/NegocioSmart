"""
Servicio de Ventas - NegocioSmart
=================================

Procesa una venta completa (descuento de stock + registro de la venta
y su detalle) como UNA sola transacción atómica de SQLite.

Por qué existe este módulo
---------------------------
Antes de este cambio, el punto de venta (`main.py: _procesar_venta`)
sólo actualizaba estructuras en memoria (`self.productos`,
`self.ventas_hoy`): la app nunca escribía la venta ni el descuento de
stock en `data/erp.db`. Eso significa que:

  1. Todo el historial de ventas del día se perdía al cerrar la
     aplicación (sólo quedaba un respaldo JSON/CSV informativo, no una
     fuente de verdad consultable).
  2. No existía ningún control real de sobreventa: dos carritos
     construidos a partir de la misma foto en memoria del stock podían
     "vender" más unidades de las que existían, porque nada volvía a
     preguntarle a la base de datos cuánto stock quedaba en el
     instante de confirmar el cobro.

Este módulo resuelve ambos problemas:

  - Descuenta stock con una sentencia UPDATE condicionada
    (``WHERE stock_actual >= cantidad``), no con un "leer, restar en
    Python, escribir". Así, la propia base de datos garantiza que el
    stock nunca puede quedar negativo, sin importar qué crea que sabe
    el proceso Python sobre el stock actual.
  - Envuelve TODO (cada descuento de stock línea por línea + el INSERT
    de la venta + los INSERT de detalle) en una sola transacción de
    SQLite. Si cualquier parte falla (stock insuficiente en la línea 3
    de 5, un error de integridad, o el proceso se cae a la mitad),
    se hace ROLLBACK de todo: nunca queda stock descontado sin una
    venta asociada, ni una venta registrada con detalle a medias.

Uso típico (desde la interfaz)::

    from services.ventas_service import procesar_venta_atomica, StockInsuficienteError

    items = [
        {"producto_id": 1, "cantidad": 2, "precio_unitario": Decimal("25.99")},
        {"producto_id": 3, "cantidad": 1, "precio_unitario": Decimal("45.00")},
    ]
    try:
        resultado = procesar_venta_atomica(db_manager, items, cliente_id=None)
    except StockInsuficienteError as e:
        mostrar_error(str(e))
    else:
        mostrar_ok(resultado.folio, resultado.total)
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from database.modelos import DetalleVenta, Venta


class VentaServiceError(Exception):
    """Error base para el procesamiento de una venta."""


class CarritoVacioError(VentaServiceError):
    """La venta no tiene ninguna línea válida (cantidad > 0)."""


class StockInsuficienteError(VentaServiceError):
    """No hay stock suficiente para completar la venta.

    Se lanza dentro de la transacción, ANTES de hacer commit, por lo
    que toda la venta (incluyendo los descuentos de stock ya aplicados
    a otras líneas del mismo carrito) se revierte: o se vende el
    carrito completo, o no se vende nada.
    """

    def __init__(self, producto_id: int, nombre: Optional[str], solicitado: int, disponible: int):
        self.producto_id = producto_id
        self.nombre = nombre or f"producto #{producto_id}"
        self.solicitado = solicitado
        self.disponible = disponible
        super().__init__(
            f"Stock insuficiente para '{self.nombre}': se pidieron {solicitado} "
            f"unidades pero solo hay {disponible} disponibles. "
            "La venta completa fue cancelada (no se descontó ni un producto)."
        )


@dataclass
class ResultadoVenta:
    """Resultado de una venta procesada y persistida correctamente."""

    venta_id: int
    folio: str
    subtotal: Decimal
    descuento: Decimal
    impuestos: Decimal
    total: Decimal
    cantidad_items: int
    stock_restante: Dict[int, int] = field(default_factory=dict)


def _generar_folio() -> str:
    """Genera un folio único basado en fecha/hora con resolución de microsegundos.

    Es suficiente para una app de escritorio de un solo proceso: dos
    ventas no pueden compartir el mismo microsegundo. Si alguna vez
    llegara a colisionar (por reloj del sistema manipulado, etc.), la
    restricción UNIQUE de la columna `folio` lo detectaría y la
    transacción completa se revertiría en vez de corromper datos.
    """
    return f"V-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


def procesar_venta_atomica(
    db_manager,
    items: List[Dict[str, Any]],
    cliente_id: Optional[int] = None,
    metodo_pago: str = "efectivo",
    descuento: Decimal = Decimal("0.00"),
    tasa_impuesto: Decimal = Decimal("0.16"),
) -> ResultadoVenta:
    """Procesa y persiste una venta completa de forma atómica.

    Args:
        db_manager: instancia conectada de ``database.db_manager.DatabaseManager``.
        items: lista de dicts con al menos ``producto_id``, ``cantidad``
            y ``precio_unitario`` (Decimal, str o float). ``descuento_linea``
            es opcional.
        cliente_id: id del cliente (None = venta de mostrador).
        metodo_pago: método de pago registrado en la venta.
        descuento: descuento general de la venta (se limita al subtotal).
        tasa_impuesto: tasa de impuesto a aplicar (por defecto 16%).

    Returns:
        ResultadoVenta con los totales exactos (Decimal) y el stock
        restante de cada producto involucrado, tal como quedó en la
        base de datos tras el commit.

    Raises:
        CarritoVacioError: si no hay líneas con cantidad > 0.
        StockInsuficienteError: si algún producto no tiene stock
            suficiente. La transacción completa se revierte antes de
            propagar el error: no queda ningún efecto parcial.
        VentaServiceError: cualquier otro error de base de datos
            durante la transacción (también se revierte por completo).
    """
    # 1) Validar y normalizar las líneas del carrito antes de tocar la BD.
    lineas: List[DetalleVenta] = []
    cantidades_por_producto: Dict[int, int] = {}
    for item in items:
        cantidad = int(item.get("cantidad", 0) or 0)
        if cantidad <= 0:
            # Una línea con cantidad <= 0 no representa una venta real;
            # se ignora en vez de restar stock o dinero.
            continue
        producto_id = int(item["producto_id"])
        precio_unitario = Decimal(str(item.get("precio_unitario", "0")))
        descuento_linea = Decimal(str(item.get("descuento_linea", "0") or "0"))

        detalle = DetalleVenta(
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            descuento_linea=descuento_linea,
        )
        detalle.calcular_subtotal()
        lineas.append(detalle)
        cantidades_por_producto[producto_id] = cantidades_por_producto.get(producto_id, 0) + cantidad

    if not lineas:
        raise CarritoVacioError("La venta no tiene productos con cantidad válida (mayor a 0)")

    venta = Venta(
        folio=_generar_folio(),
        cliente_id=cliente_id,
        metodo_pago=metodo_pago,
        descuento=descuento if descuento > 0 else Decimal("0.00"),
        detalles=lineas,
    )
    venta.calcular_totales(tasa_impuesto=tasa_impuesto)

    connection = db_manager.connection
    if connection is None:
        if not db_manager.conectar():
            raise VentaServiceError("No se pudo conectar a la base de datos para procesar la venta")
        connection = db_manager.connection

    stock_restante: Dict[int, int] = {}

    try:
        # Todas las sentencias de aquí en adelante forman una única
        # transacción: sqlite3 abre la transacción implícitamente en el
        # primer UPDATE/INSERT y no la cierra hasta commit()/rollback().
        for producto_id, cantidad_total in cantidades_por_producto.items():
            cursor = connection.execute(
                """
                UPDATE productos
                SET stock_actual = stock_actual - ?,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = ? AND activo = 1 AND stock_actual >= ?
                """,
                (cantidad_total, producto_id, cantidad_total),
            )

            if cursor.rowcount != 1:
                # No se pudo aplicar el descuento: o el producto no
                # existe/está inactivo, o no hay stock suficiente en
                # este preciso momento (aunque la UI pensara que sí).
                fila = connection.execute(
                    "SELECT nombre, stock_actual FROM productos WHERE id = ?",
                    (producto_id,),
                ).fetchone()
                nombre = fila["nombre"] if fila else None
                disponible = fila["stock_actual"] if fila else 0
                raise StockInsuficienteError(producto_id, nombre, cantidad_total, disponible)

            fila_stock = connection.execute(
                "SELECT stock_actual FROM productos WHERE id = ?", (producto_id,)
            ).fetchone()
            stock_restante[producto_id] = fila_stock["stock_actual"] if fila_stock else None

        cursor_venta = connection.execute(
            """
            INSERT INTO ventas (folio, cliente_id, subtotal, descuento, impuestos, total, metodo_pago, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'completada')
            """,
            (
                venta.folio,
                venta.cliente_id,
                str(venta.subtotal),
                str(venta.descuento),
                str(venta.impuestos),
                str(venta.total),
                venta.metodo_pago,
            ),
        )
        venta_id = cursor_venta.lastrowid

        for detalle in lineas:
            connection.execute(
                """
                INSERT INTO detalle_ventas
                    (venta_id, producto_id, cantidad, precio_unitario, descuento_linea, subtotal_linea)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    venta_id,
                    detalle.producto_id,
                    detalle.cantidad,
                    str(detalle.precio_unitario),
                    str(detalle.descuento_linea),
                    str(detalle.subtotal_linea),
                ),
            )

        connection.commit()

    except StockInsuficienteError:
        connection.rollback()
        raise
    except Exception as exc:  # noqa: BLE001 - se re-lanza como error de dominio
        connection.rollback()
        raise VentaServiceError(f"No se pudo procesar la venta: {exc}") from exc

    return ResultadoVenta(
        venta_id=venta_id,
        folio=venta.folio,
        subtotal=venta.subtotal,
        descuento=venta.descuento,
        impuestos=venta.impuestos,
        total=venta.total,
        cantidad_items=sum(d.cantidad for d in lineas),
        stock_restante=stock_restante,
    )
