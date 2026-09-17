"""
Consultas SQL Complejas - NegocioSmart
=======================================

Define consultas SQL complejas y procedimientos almacenados
para análisis, reportes y operaciones avanzadas.

Todas las consultas se devuelven como una tupla ``(sql, parametros)``
y usan siempre parámetros ligados (placeholders ``?``) en lugar de
interpolar valores directamente en el texto SQL. Esto evita
inyección SQL incluso si en el futuro alguno de estos valores
(fechas, ids, límites) llega a originarse en una entrada de usuario
(un campo de texto, un filtro de la interfaz, etc.).

Uso:
    sql, params = ConsultasSQL.productos_mas_vendidos(limite=5, dias=7)
    filas = db_manager.ejecutar_consulta(sql, params)

Autor: Sistema NegocioSmart
Fecha: 2025-10-04
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Alias de tipo: toda consulta se representa como (sql, parametros)
Consulta = Tuple[str, tuple]


class ConsultasSQL:
    """Colección de consultas SQL complejas para NegocioSmart.

    IMPORTANTE: ningún método interpola valores externos directamente en
    el texto SQL (nada de f-strings con datos variables). Los valores
    dinámicos siempre viajan como parámetros ligados (``?``) para que el
    driver de SQLite los escape correctamente y así prevenir inyección
    SQL, sin importar de dónde provenga el valor.
    """

    @staticmethod
    def productos_stock_bajo() -> Consulta:
        """Obtiene productos con stock bajo (no recibe parámetros externos)."""
        sql = """
        SELECT
            p.id,
            p.codigo,
            p.nombre,
            p.stock_actual,
            p.stock_minimo,
            c.nombre AS categoria,
            (p.stock_minimo - p.stock_actual) AS faltante
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.stock_actual <= p.stock_minimo
        AND p.activo = 1
        ORDER BY (p.stock_minimo - p.stock_actual) DESC
        """
        return sql, ()

    @staticmethod
    def productos_mas_vendidos(limite: int = 10, dias: int = 30) -> Consulta:
        """Obtiene los productos más vendidos en un período."""
        limite = ParametrosConsulta.validar_entero(limite, default=10, minimo=1, maximo=1000)
        dias = ParametrosConsulta.validar_entero(dias, default=30, minimo=1, maximo=3650)
        sql = """
        SELECT
            p.id,
            p.codigo,
            p.nombre,
            SUM(dv.cantidad) as total_vendido,
            SUM(dv.subtotal_linea) as ingresos_generados,
            COUNT(DISTINCT v.id) as num_ventas,
            AVG(dv.precio_unitario) as precio_promedio
        FROM productos p
        INNER JOIN detalle_ventas dv ON p.id = dv.producto_id
        INNER JOIN ventas v ON dv.venta_id = v.id
        WHERE v.fecha_venta >= date('now', '-' || ? || ' days')
        AND v.estado = 'completada'
        AND p.activo = 1
        GROUP BY p.id, p.codigo, p.nombre
        ORDER BY total_vendido DESC
        LIMIT ?
        """
        return sql, (dias, limite)

    @staticmethod
    def ventas_por_dia(fecha_inicio: str, fecha_fin: str) -> Consulta:
        """Obtiene ventas agrupadas por día."""
        fecha_inicio = ParametrosConsulta.validar_fecha(fecha_inicio)
        fecha_fin = ParametrosConsulta.validar_fecha(fecha_fin)
        sql = """
        SELECT
            DATE(v.fecha_venta) as fecha,
            COUNT(*) as num_ventas,
            SUM(v.total) as total_vendido,
            SUM(v.subtotal) as subtotal,
            SUM(v.impuestos) as total_impuestos,
            AVG(v.total) as venta_promedio
        FROM ventas v
        WHERE DATE(v.fecha_venta) BETWEEN ? AND ?
        AND v.estado = 'completada'
        GROUP BY DATE(v.fecha_venta)
        ORDER BY fecha DESC
        """
        return sql, (fecha_inicio, fecha_fin)

    @staticmethod
    def ventas_por_mes(anio: int) -> Consulta:
        """Obtiene ventas agrupadas por mes de un año dado."""
        anio = ParametrosConsulta.validar_entero(anio, default=datetime.now().year, minimo=1900, maximo=9999)
        # strftime('%Y', ...) siempre produce una cadena de 4 dígitos.
        anio_str = f"{anio:04d}"
        sql = """
        SELECT
            mes,
            año_mes,
            COUNT(*) as num_ventas,
            SUM(total) as total_vendido,
            AVG(total) as venta_promedio,
            SUM(cantidad_productos) as productos_vendidos
        FROM (
            SELECT
                v.id,
                v.total,
                strftime('%m', v.fecha_venta) as mes,
                strftime('%Y-%m', v.fecha_venta) as año_mes,
                (
                    SELECT SUM(dv.cantidad)
                    FROM detalle_ventas dv
                    WHERE dv.venta_id = v.id
                ) as cantidad_productos
            FROM ventas v
            WHERE strftime('%Y', v.fecha_venta) = ?
            AND v.estado = 'completada'
        )
        GROUP BY año_mes
        ORDER BY año_mes
        """
        return sql, (anio_str,)

    @staticmethod
    def clientes_frecuentes(limite: int = 20, dias: int = 90) -> Consulta:
        """Obtiene los clientes más frecuentes."""
        limite = ParametrosConsulta.validar_entero(limite, default=20, minimo=1, maximo=1000)
        dias = ParametrosConsulta.validar_entero(dias, default=90, minimo=1, maximo=3650)
        sql = """
        SELECT
            c.id,
            c.nombre,
            c.apellidos,
            c.email,
            c.telefono,
            COUNT(v.id) as num_compras,
            SUM(v.total) as total_comprado,
            AVG(v.total) as promedio_compra,
            MAX(v.fecha_venta) as ultima_compra,
            MIN(v.fecha_venta) as primera_compra
        FROM clientes c
        INNER JOIN ventas v ON c.id = v.cliente_id
        WHERE v.fecha_venta >= date('now', '-' || ? || ' days')
        AND v.estado = 'completada'
        AND c.activo = 1
        GROUP BY c.id, c.nombre, c.apellidos, c.email, c.telefono
        HAVING COUNT(v.id) > 1
        ORDER BY num_compras DESC, total_comprado DESC
        LIMIT ?
        """
        return sql, (dias, limite)

    @staticmethod
    def inventario_por_categoria() -> Consulta:
        """Obtiene el inventario agrupado por categoría (sin parámetros externos)."""
        sql = """
        SELECT
            c.id,
            c.nombre as categoria,
            COUNT(p.id) as num_productos,
            SUM(p.stock_actual) as stock_total,
            SUM(p.stock_actual * p.precio_compra) as valor_inventario_compra,
            SUM(p.stock_actual * p.precio_venta) as valor_inventario_venta,
            AVG(p.precio_venta) as precio_promedio,
            SUM(CASE WHEN p.stock_actual <= p.stock_minimo THEN 1 ELSE 0 END) as productos_stock_bajo
        FROM categorias c
        LEFT JOIN productos p ON c.id = p.categoria_id
        WHERE c.activa = 1
        AND (p.id IS NULL OR p.activo = 1)
        GROUP BY c.id, c.nombre
        ORDER BY valor_inventario_venta DESC
        """
        return sql, ()

    @staticmethod
    def resumen_ventas_hoy() -> Consulta:
        """Obtiene el resumen de ventas del día actual (sin parámetros externos)."""
        sql = """
        SELECT
            COUNT(*) as num_ventas,
            SUM(v.total) as total_vendido,
            AVG(v.total) as venta_promedio,
            SUM(dv_sum.cantidad_total) as productos_vendidos,
            MAX(v.total) as venta_mayor,
            MIN(v.total) as venta_menor
        FROM ventas v
        LEFT JOIN (
            SELECT
                venta_id,
                SUM(cantidad) as cantidad_total
            FROM detalle_ventas
            GROUP BY venta_id
        ) dv_sum ON v.id = dv_sum.venta_id
        WHERE DATE(v.fecha_venta) = DATE('now')
        AND v.estado = 'completada'
        """
        return sql, ()

    @staticmethod
    def productos_sin_movimiento(dias: int = 30) -> Consulta:
        """Obtiene productos sin movimiento en un período."""
        dias = ParametrosConsulta.validar_entero(dias, default=30, minimo=1, maximo=3650)
        sql = """
        SELECT
            p.id,
            p.codigo,
            p.nombre,
            p.stock_actual,
            p.precio_venta,
            c.nombre as categoria,
            p.fecha_modificacion as ultimo_movimiento,
            (p.stock_actual * p.precio_compra) as valor_inventario
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN detalle_ventas dv ON p.id = dv.producto_id
        LEFT JOIN ventas v ON dv.venta_id = v.id
            AND v.fecha_venta >= date('now', '-' || ? || ' days')
            AND v.estado = 'completada'
        WHERE v.id IS NULL
        AND p.activo = 1
        AND p.stock_actual > 0
        ORDER BY p.stock_actual DESC, valor_inventario DESC
        """
        return sql, (dias,)

    @staticmethod
    def analisis_margenes() -> Consulta:
        """Análisis de márgenes de ganancia por producto (sin parámetros externos)."""
        sql = """
        SELECT
            p.id,
            p.codigo,
            p.nombre,
            p.precio_compra,
            p.precio_venta,
            (p.precio_venta - p.precio_compra) as ganancia_unitaria,
            CASE
                WHEN p.precio_compra > 0
                THEN ROUND(((p.precio_venta - p.precio_compra) / p.precio_compra) * 100, 2)
                ELSE 0
            END as margen_porcentaje,
            p.stock_actual,
            (p.stock_actual * (p.precio_venta - p.precio_compra)) as ganancia_potencial,
            c.nombre as categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1
        AND p.precio_compra > 0
        ORDER BY margen_porcentaje DESC
        """
        return sql, ()

    @staticmethod
    def historico_ventas_cliente(cliente_id: int, limite: int = 50) -> Consulta:
        """Obtiene el histórico de ventas de un cliente."""
        cliente_id = ParametrosConsulta.validar_entero(cliente_id, default=0, minimo=0, maximo=2_147_483_647)
        limite = ParametrosConsulta.validar_entero(limite, default=50, minimo=1, maximo=1000)
        sql = """
        SELECT
            v.id,
            v.folio,
            v.fecha_venta,
            v.total,
            v.metodo_pago,
            v.estado,
            COUNT(dv.id) as num_productos,
            SUM(dv.cantidad) as cantidad_productos
        FROM ventas v
        LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
        WHERE v.cliente_id = ?
        GROUP BY v.id, v.folio, v.fecha_venta, v.total, v.metodo_pago, v.estado
        ORDER BY v.fecha_venta DESC
        LIMIT ?
        """
        return sql, (cliente_id, limite)

    @staticmethod
    def detalle_venta_completo(venta_id: int) -> Consulta:
        """Obtiene el detalle completo de una venta."""
        venta_id = ParametrosConsulta.validar_entero(venta_id, default=0, minimo=0, maximo=2_147_483_647)
        sql = """
        SELECT
            v.id as venta_id,
            v.folio,
            v.fecha_venta,
            v.subtotal,
            v.descuento,
            v.impuestos,
            v.total,
            v.metodo_pago,
            c.nombre as cliente_nombre,
            c.apellidos as cliente_apellidos,
            c.email as cliente_email,
            dv.id as detalle_id,
            p.codigo as producto_codigo,
            p.nombre as producto_nombre,
            dv.cantidad,
            dv.precio_unitario,
            dv.descuento_linea,
            dv.subtotal_linea
        FROM ventas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
        LEFT JOIN productos p ON dv.producto_id = p.id
        WHERE v.id = ?
        ORDER BY dv.id
        """
        return sql, (venta_id,)

    @staticmethod
    def estadisticas_generales() -> Consulta:
        """Obtiene estadísticas generales del sistema (sin parámetros externos)."""
        sql = """
        SELECT
            'productos_activos' as metrica,
            COUNT(*) as valor
        FROM productos
        WHERE activo = 1

        UNION ALL

        SELECT
            'productos_stock_bajo' as metrica,
            COUNT(*) as valor
        FROM productos
        WHERE stock_actual <= stock_minimo AND activo = 1

        UNION ALL

        SELECT
            'clientes_activos' as metrica,
            COUNT(*) as valor
        FROM clientes
        WHERE activo = 1

        UNION ALL

        SELECT
            'ventas_mes_actual' as metrica,
            COUNT(*) as valor
        FROM ventas
        WHERE strftime('%Y-%m', fecha_venta) = strftime('%Y-%m', 'now')
        AND estado = 'completada'

        UNION ALL

        SELECT
            'ingresos_mes_actual' as metrica,
            ROUND(COALESCE(SUM(total), 0), 2) as valor
        FROM ventas
        WHERE strftime('%Y-%m', fecha_venta) = strftime('%Y-%m', 'now')
        AND estado = 'completada'
        """
        return sql, ()


class ParametrosConsulta:
    """Clase para validar y preparar parámetros de consultas.

    Además de sanear las fechas/enteros que se usan como parámetros
    ligados, esto asegura que ningún valor fuera de rango (por ejemplo
    un ``LIMIT`` gigantesco o negativo) llegue a la base de datos.
    """

    @staticmethod
    def validar_fecha(fecha: Optional[str]) -> str:
        """Valida y formatea una fecha. Si no es válida, usa la fecha actual."""
        if not fecha:
            return datetime.now().strftime('%Y-%m-%d')
        try:
            fecha_obj = datetime.strptime(str(fecha), '%Y-%m-%d')
            return fecha_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            # Si falla, usar fecha actual en lugar de propagar un valor
            # potencialmente malicioso o inválido.
            return datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def validar_entero(valor: Any, default: int = 0, minimo: int = 0, maximo: int = 1000000) -> int:
        """Valida y limita un valor entero a un rango seguro."""
        try:
            valor_int = int(valor)
            return max(minimo, min(maximo, valor_int))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def preparar_fechas_periodo(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> tuple:
        """Prepara fechas para consultas de período."""
        if not fecha_inicio:
            # Por defecto, último mes
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            fecha_inicio = ParametrosConsulta.validar_fecha(fecha_inicio)

        if not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
        else:
            fecha_fin = ParametrosConsulta.validar_fecha(fecha_fin)

        return fecha_inicio, fecha_fin
