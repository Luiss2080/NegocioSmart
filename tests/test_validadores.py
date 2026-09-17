"""
Tests de utils/validadores.py, incluyendo los casos que antes NO se
validaban en la interfaz (main.py) y que ahora sí pasan por aquí:
cantidades negativas en ajustes de stock, y precios/costos negativos
o con más de 2 decimales en el alta de productos.
"""

from decimal import Decimal

from utils.validadores import Validador, ValidadorFormularios


def test_validar_cantidad_rechaza_negativos():
    valido, mensaje, valor = Validador.validar_cantidad("-10")
    assert valido is False
    assert valor is None


def test_validar_cantidad_acepta_cero():
    valido, mensaje, valor = Validador.validar_cantidad("0")
    assert valido is True
    assert valor == 0


def test_validar_cantidad_rechaza_formato_invalido():
    valido, mensaje, valor = Validador.validar_cantidad("diez")
    assert valido is False


def test_validar_precio_rechaza_negativo():
    valido, mensaje, valor = Validador.validar_precio("-5.00")
    assert valido is False


def test_validar_precio_rechaza_mas_de_dos_decimales():
    valido, mensaje, valor = Validador.validar_precio("10.999")
    assert valido is False


def test_validar_precio_rechaza_valor_absurdo():
    valido, mensaje, valor = Validador.validar_precio("99999999")
    assert valido is False


def test_validar_precio_acepta_valor_normal():
    valido, mensaje, valor = Validador.validar_precio("19.99")
    assert valido is True
    assert valor == Decimal("19.99")


def test_simular_ajuste_de_stock_rechaza_entrada_negativa():
    """Reproduce el bug corregido en main.py::_ajustar_stock: antes,
    int("-5") en un movimiento de "Entrada (+)" se aceptaba y
    disminuía el stock en vez de aumentarlo (o dejaba stock negativo
    con "Ajuste a cantidad exacta")."""
    valido, mensaje, cantidad = Validador.validar_cantidad("-5")
    assert valido is False
    # La función que arma la venta jamás llega a ejecutar
    # producto['stock'] = cantidad con un valor negativo, porque la
    # validación corta el flujo antes.


def test_validar_producto_formulario_completo():
    datos = {
        "codigo": "PRO-001",
        "nombre": "Producto de prueba",
        "descripcion": "",
        "precio_compra": "5.00",
        "precio_venta": "-1.00",  # inválido a propósito
        "stock_actual": "10",
        "stock_minimo": "1",
    }
    valido, errores = ValidadorFormularios.validar_producto(datos)
    assert valido is False
    assert any("venta" in e.lower() for e in errores)
