"""
Tests de services/ventas_service.py: procesamiento atómico de ventas.

Esta es la prueba de integridad de inventario más importante de la
suite: verifica que la base de datos, no el proceso Python, es quien
decide si hay stock suficiente, y que una venta con cualquier línea
fallida se revierte POR COMPLETO (nunca queda stock descontado sin
venta asociada, ni al revés).
"""

from decimal import Decimal

import pytest

from services.ventas_service import (
    CarritoVacioError,
    StockInsuficienteError,
    procesar_venta_atomica,
)
from tests.conftest import insertar_producto


def _stock_de(db, producto_id):
    fila = db.connection.execute(
        "SELECT stock_actual FROM productos WHERE id = ?", (producto_id,)
    ).fetchone()
    return fila["stock_actual"]


def test_venta_normal_descuenta_stock_y_persiste(db):
    producto_id = insertar_producto(db, stock_actual=5)

    resultado = procesar_venta_atomica(
        db, [{"producto_id": producto_id, "cantidad": 3, "precio_unitario": Decimal("10.00")}]
    )

    assert resultado.subtotal == Decimal("30.00")
    assert resultado.impuestos == Decimal("4.80")  # 16% de 30.00
    assert resultado.total == Decimal("34.80")
    assert _stock_de(db, producto_id) == 2

    venta_row = db.connection.execute(
        "SELECT * FROM ventas WHERE folio = ?", (resultado.folio,)
    ).fetchone()
    assert venta_row is not None

    detalle_rows = db.connection.execute(
        "SELECT * FROM detalle_ventas WHERE venta_id = ?", (venta_row["id"],)
    ).fetchall()
    assert len(detalle_rows) == 1
    assert detalle_rows[0]["cantidad"] == 3


def test_no_se_puede_sobrevender_un_producto(db):
    producto_id = insertar_producto(db, stock_actual=2)

    with pytest.raises(StockInsuficienteError):
        procesar_venta_atomica(
            db, [{"producto_id": producto_id, "cantidad": 5, "precio_unitario": Decimal("10.00")}]
        )

    # El stock no debe haber cambiado ni un poco tras el intento fallido.
    assert _stock_de(db, producto_id) == 2
    total_ventas = db.connection.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    assert total_ventas == 0


def test_carrito_mixto_con_una_linea_sin_stock_revierte_todo(db):
    """Caso crítico: el carrito tiene 2 líneas. La primera SÍ tiene
    stock suficiente y "podría" venderse; la segunda no. Ninguna de
    las dos debe aplicarse: la venta es todo-o-nada."""
    producto_ok = insertar_producto(db, codigo="OK", stock_actual=10)
    producto_sin_stock = insertar_producto(db, codigo="SIN-STOCK", stock_actual=1)

    with pytest.raises(StockInsuficienteError):
        procesar_venta_atomica(
            db,
            [
                {"producto_id": producto_ok, "cantidad": 2, "precio_unitario": Decimal("10.00")},
                {"producto_id": producto_sin_stock, "cantidad": 99, "precio_unitario": Decimal("10.00")},
            ],
        )

    # La línea que sí tenía stock NO debe haber quedado descontada:
    # es la prueba de que la transacción se revierte completa.
    assert _stock_de(db, producto_ok) == 10
    assert _stock_de(db, producto_sin_stock) == 1
    assert db.connection.execute("SELECT COUNT(*) FROM ventas").fetchone()[0] == 0


def test_dos_ventas_secuenciales_no_pueden_superar_el_stock_total(db):
    """Simula dos "cobros" seguidos (como si dos cajeros vendieran del
    mismo producto uno después del otro) contra un stock que sólo
    alcanza para uno de los dos."""
    producto_id = insertar_producto(db, stock_actual=3)

    # Primera venta: se lleva 3 unidades, agota el stock.
    procesar_venta_atomica(
        db, [{"producto_id": producto_id, "cantidad": 3, "precio_unitario": Decimal("10.00")}]
    )
    assert _stock_de(db, producto_id) == 0

    # Segunda venta inmediatamente después: ya no queda nada que vender.
    with pytest.raises(StockInsuficienteError):
        procesar_venta_atomica(
            db, [{"producto_id": producto_id, "cantidad": 1, "precio_unitario": Decimal("10.00")}]
        )
    assert _stock_de(db, producto_id) == 0  # sigue en 0, nunca negativo


def test_carrito_vacio_no_escribe_nada(db):
    with pytest.raises(CarritoVacioError):
        procesar_venta_atomica(db, [])

    assert db.connection.execute("SELECT COUNT(*) FROM ventas").fetchone()[0] == 0


def test_lineas_con_cantidad_cero_se_ignoran_sin_error(db):
    producto_id = insertar_producto(db, stock_actual=5)
    resultado = procesar_venta_atomica(
        db,
        [
            {"producto_id": producto_id, "cantidad": 0, "precio_unitario": Decimal("10.00")},
            {"producto_id": producto_id, "cantidad": 2, "precio_unitario": Decimal("10.00")},
        ],
    )
    assert resultado.cantidad_items == 2
    assert _stock_de(db, producto_id) == 3
