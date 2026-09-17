"""
Fixtures compartidas para la suite de tests de NegocioSmart.

Los tests de base de datos usan una instancia real de
`database.db_manager.DatabaseManager` apuntando a un archivo SQLite
temporal (nunca al `data/erp.db` real de desarrollo), inicializada con
el esquema real de producción (`inicializar_db`). Esto prueba el
comportamiento real contra SQLite en vez de simularlo con mocks, que
es lo que importa para las reglas de negocio de dinero/stock.
"""

import os
import sys

import pytest

# Asegura que el repo esté en sys.path sin importar desde dónde se
# invoque pytest.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager


@pytest.fixture()
def db(tmp_path):
    """DatabaseManager conectado a un SQLite temporal con el esquema real."""
    manager = DatabaseManager()
    manager.db_path = str(tmp_path / "test_negociosmart.db")
    ok = manager.inicializar_db()
    assert ok, "No se pudo inicializar el esquema de la base de datos de prueba"
    yield manager
    manager.desconectar()


def insertar_producto(db_manager, codigo="P1", nombre="Producto de prueba",
                       precio_compra="5.00", precio_venta="10.00",
                       stock_actual=10, stock_minimo=1):
    """Inserta un producto de prueba y devuelve su id."""
    cursor = db_manager.connection.execute(
        """
        INSERT INTO productos (codigo, nombre, precio_compra, precio_venta, stock_actual, stock_minimo)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (codigo, nombre, precio_compra, precio_venta, stock_actual, stock_minimo),
    )
    db_manager.connection.commit()
    return cursor.lastrowid
