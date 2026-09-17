"""
Tests de database/consultas.py: cada consulta debe ejecutar sin error
contra el esquema real, y los valores dinámicos deben viajar como
parámetros ligados (nunca interpolados en el SQL), de forma que un
payload de inyección SQL quede neutralizado en vez de ejecutado.
"""

from database.consultas import ConsultasSQL, ParametrosConsulta
from tests.conftest import insertar_producto


def test_todas_las_consultas_devuelven_sql_y_parametros_separados():
    for metodo in (
        ConsultasSQL.productos_stock_bajo,
        ConsultasSQL.inventario_por_categoria,
        ConsultasSQL.resumen_ventas_hoy,
        ConsultasSQL.analisis_margenes,
        ConsultasSQL.estadisticas_generales,
    ):
        sql, params = metodo()
        assert isinstance(sql, str)
        assert isinstance(params, tuple)


def test_consultas_ejecutan_contra_el_esquema_real(db):
    producto_id = insertar_producto(db, stock_actual=0, stock_minimo=5)

    sql, params = ConsultasSQL.productos_stock_bajo()
    filas = db.ejecutar_consulta(sql, params)
    assert any(f["id"] == producto_id for f in filas)

    sql, params = ConsultasSQL.productos_mas_vendidos(limite=5, dias=30)
    assert db.ejecutar_consulta(sql, params) is not None

    sql, params = ConsultasSQL.ventas_por_dia("2020-01-01", "2030-01-01")
    assert db.ejecutar_consulta(sql, params) is not None

    sql, params = ConsultasSQL.historico_ventas_cliente(1, limite=10)
    assert db.ejecutar_consulta(sql, params) is not None

    sql, params = ConsultasSQL.estadisticas_generales()
    filas = db.ejecutar_consulta(sql, params)
    assert len(filas) == 5  # 5 filas de metrica/valor por UNION ALL


def test_payload_de_inyeccion_en_cliente_id_no_hace_dano(db):
    """Antes de la corrección, `historico_ventas_cliente` interpolaba
    cliente_id crudo en el SQL. Un payload como este habría permitido
    inyección. Ahora ParametrosConsulta.validar_entero lo reduce a un
    entero inocuo (0) y de todas formas viaja parametrizado."""
    payload = "1 OR 1=1; DROP TABLE ventas; --"
    sql, params = ConsultasSQL.historico_ventas_cliente(payload, limite=10)

    assert "DROP TABLE" not in sql
    assert params[0] == 0  # se sanea a un entero por defecto

    db.ejecutar_consulta(sql, params)

    # La tabla ventas debe seguir intacta.
    filas = db.ejecutar_consulta("SELECT COUNT(*) as total FROM ventas")
    assert filas is not None


def test_payload_de_inyeccion_en_fechas_se_normaliza():
    payload = "2020-01-01'; DROP TABLE productos; --"
    sql, params = ConsultasSQL.ventas_por_dia(payload, "2030-01-01")
    assert "DROP TABLE" not in sql
    # Fecha inválida -> ParametrosConsulta cae de vuelta a la fecha de hoy
    assert params[0] != payload


def test_parametros_consulta_limita_enteros_fuera_de_rango():
    assert ParametrosConsulta.validar_entero(-50, default=0, minimo=0, maximo=100) == 0
    assert ParametrosConsulta.validar_entero(99999, default=0, minimo=0, maximo=100) == 100
    assert ParametrosConsulta.validar_entero("no-es-numero", default=7) == 7


def test_parametros_consulta_fecha_invalida_cae_a_hoy():
    from datetime import datetime
    resultado = ParametrosConsulta.validar_fecha("fecha-invalida")
    assert resultado == datetime.now().strftime("%Y-%m-%d")
