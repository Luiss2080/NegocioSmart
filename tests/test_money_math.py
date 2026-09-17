"""
Tests de matemática de dinero (database/modelos.py).

Esta es la parte más crítica de una app de punto de venta: si los
totales pueden quedar mal por un centavo de deriva de punto flotante,
o negativos por un descuento mal aplicado, el negocio pierde dinero o
factura de más a un cliente. Todo aquí se hace con Decimal, nunca con
float, y se prueban explícitamente los casos límite pedidos en la
auditoría: 100% de descuento, descuento mayor al precio, cantidades
negativas y cantidades en cero.
"""

from decimal import Decimal

from database.modelos import DetalleVenta, Venta


def test_multi_item_sale_no_float_drift():
    """3 líneas de 0.10 deben sumar EXACTAMENTE 0.30, no 0.30000000000000004."""
    detalle = DetalleVenta(producto_id=1, cantidad=3, precio_unitario=Decimal("0.10"))
    detalle.calcular_subtotal()
    assert detalle.subtotal_linea == Decimal("0.30")


def test_linea_100_por_ciento_descuento():
    detalle = DetalleVenta(
        producto_id=1, cantidad=2, precio_unitario=Decimal("50.00"),
        descuento_linea=Decimal("100.00"),
    )
    detalle.calcular_subtotal()
    assert detalle.subtotal_linea == Decimal("0.00")


def test_descuento_mayor_al_precio_de_linea_no_da_negativo():
    detalle = DetalleVenta(
        producto_id=1, cantidad=1, precio_unitario=Decimal("10.00"),
        descuento_linea=Decimal("999.00"),
    )
    detalle.calcular_subtotal()
    assert detalle.subtotal_linea == Decimal("0.00")


def test_cantidad_negativa_no_genera_venta_negativa():
    detalle = DetalleVenta(producto_id=1, cantidad=-5, precio_unitario=Decimal("20.00"))
    detalle.calcular_subtotal()
    assert detalle.subtotal_linea == Decimal("0.00")


def test_cantidad_cero():
    detalle = DetalleVenta(producto_id=1, cantidad=0, precio_unitario=Decimal("20.00"))
    detalle.calcular_subtotal()
    assert detalle.subtotal_linea == Decimal("0.00")


def test_venta_multi_item_con_descuento_e_impuesto_es_exacta():
    """Traza una venta realista de varios items + descuento + impuesto
    y verifica que el total sea exacto, no aproximado."""
    venta = Venta(folio="F-TEST")
    linea_a = DetalleVenta(producto_id=1, cantidad=3, precio_unitario=Decimal("19.99"))
    linea_a.calcular_subtotal()
    linea_b = DetalleVenta(producto_id=2, cantidad=7, precio_unitario=Decimal("0.10"))
    linea_b.calcular_subtotal()

    venta.detalles = [linea_a, linea_b]
    venta.descuento = Decimal("5.00")
    venta.calcular_totales(tasa_impuesto=Decimal("0.13"))  # IVA Bolivia 13%

    subtotal_esperado = Decimal("19.99") * 3 + Decimal("0.10") * 7
    assert venta.subtotal == subtotal_esperado

    subtotal_con_descuento = venta.subtotal - venta.descuento
    impuestos_esperados = (subtotal_con_descuento * Decimal("0.13")).quantize(Decimal("0.01"))
    assert venta.impuestos == impuestos_esperados
    assert venta.total == subtotal_con_descuento + venta.impuestos


def test_descuento_de_venta_mayor_al_subtotal_se_limita():
    venta = Venta(folio="F-TEST2")
    linea = DetalleVenta(producto_id=1, cantidad=1, precio_unitario=Decimal("10.00"))
    linea.calcular_subtotal()
    venta.detalles = [linea]
    venta.descuento = Decimal("999999.00")

    venta.calcular_totales()

    assert venta.descuento == Decimal("10.00")  # se limita al subtotal
    assert venta.total == Decimal("0.00")  # nunca negativo


def test_venta_sin_detalles_da_totales_en_cero():
    venta = Venta(folio="F-VACIA")
    venta.calcular_totales()
    assert venta.subtotal == Decimal("0.00")
    assert venta.total == Decimal("0.00")
