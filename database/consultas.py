"""
Consultas SQL Complejas - VentaPro
==================================

Define consultas SQL complejas y procedimientos almacenados
para análisis, reportes y operaciones avanzadas.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class ConsultasSQL:
    """Colección de consultas SQL complejas para VentaPro"""
    
    @staticmethod
    def productos_stock_bajo() -> str:
        """Obtiene productos con stock bajo"""
        return """
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
    
    @staticmethod
    def productos_mas_vendidos(limite: int = 10, dias: int = 30) -> str:
        """Obtiene los productos más vendidos en un período"""
        return f"""
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
        WHERE v.fecha_venta >= date('now', '-{dias} days')
        AND v.estado = 'completada'
        AND p.activo = 1
        GROUP BY p.id, p.codigo, p.nombre
        ORDER BY total_vendido DESC
        LIMIT {limite}
        """
    
    @staticmethod
    def ventas_por_dia(fecha_inicio: str, fecha_fin: str) -> str:
        """Obtiene ventas agrupadas por día"""
        return f"""
        SELECT 
            DATE(v.fecha_venta) as fecha,
            COUNT(*) as num_ventas,
            SUM(v.total) as total_vendido,
            SUM(v.subtotal) as subtotal,
            SUM(v.impuestos) as total_impuestos,
            AVG(v.total) as venta_promedio
        FROM ventas v
        WHERE DATE(v.fecha_venta) BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
        AND v.estado = 'completada'
        GROUP BY DATE(v.fecha_venta)
        ORDER BY fecha DESC
        """
    
    @staticmethod
    def ventas_por_mes(año: int) -> str:
        """Obtiene ventas agrupadas por mes"""
        return f"""
        SELECT 
            strftime('%m', v.fecha_venta) as mes,
            strftime('%Y-%m', v.fecha_venta) as año_mes,
            COUNT(*) as num_ventas,
            SUM(v.total) as total_vendido,
            AVG(v.total) as venta_promedio,
            SUM(v.cantidad_productos) as productos_vendidos
        FROM (
            SELECT 
                v.*,
                SUM(dv.cantidad) as cantidad_productos
            FROM ventas v
            LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
            WHERE strftime('%Y', v.fecha_venta) = '{año}'
            AND v.estado = 'completada'
            GROUP BY v.id
        ) v
        GROUP BY strftime('%Y-%m', v.fecha_venta)
        ORDER BY año_mes
        """
    
    @staticmethod
    def clientes_frecuentes(limite: int = 20, dias: int = 90) -> str:
        """Obtiene los clientes más frecuentes"""
        return f"""
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
        WHERE v.fecha_venta >= date('now', '-{dias} days')
        AND v.estado = 'completada'
        AND c.activo = 1
        GROUP BY c.id, c.nombre, c.apellidos, c.email, c.telefono
        HAVING COUNT(v.id) > 1
        ORDER BY num_compras DESC, total_comprado DESC
        LIMIT {limite}
        """
    
    @staticmethod
    def inventario_por_categoria() -> str:
        """Obtiene el inventario agrupado por categoría"""
        return """
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
    
    @staticmethod
    def resumen_ventas_hoy() -> str:
        """Obtiene el resumen de ventas del día actual"""
        return """
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
    
    @staticmethod
    def productos_sin_movimiento(dias: int = 30) -> str:
        """Obtiene productos sin movimiento en un período"""
        return f"""
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
            AND v.fecha_venta >= date('now', '-{dias} days')
            AND v.estado = 'completada'
        WHERE v.id IS NULL
        AND p.activo = 1
        AND p.stock_actual > 0
        ORDER BY p.stock_actual DESC, valor_inventario DESC
        """
    
    @staticmethod
    def analisis_margenes() -> str:
        """Análisis de márgenes de ganancia por producto"""
        return """
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
    
    @staticmethod
    def historico_ventas_cliente(cliente_id: int, limite: int = 50) -> str:
        """Obtiene el histórico de ventas de un cliente"""
        return f"""
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
        WHERE v.cliente_id = {cliente_id}
        GROUP BY v.id, v.folio, v.fecha_venta, v.total, v.metodo_pago, v.estado
        ORDER BY v.fecha_venta DESC
        LIMIT {limite}
        """
    
    @staticmethod
    def detalle_venta_completo(venta_id: int) -> str:
        """Obtiene el detalle completo de una venta"""
        return f"""
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
        WHERE v.id = {venta_id}
        ORDER BY dv.id
        """
    
    @staticmethod
    def estadisticas_generales() -> str:
        """Obtiene estadísticas generales del sistema"""
        return """
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

class ParametrosConsulta:
    """Clase para validar y preparar parámetros de consultas"""
    
    @staticmethod
    def validar_fecha(fecha: str) -> str:
        """Valida y formatea una fecha"""
        try:
            # Intentar parsear la fecha
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            return fecha_obj.strftime('%Y-%m-%d')
        except ValueError:
            # Si falla, usar fecha actual
            return datetime.now().strftime('%Y-%m-%d')
    
    @staticmethod
    def validar_entero(valor: Any, default: int = 0, minimo: int = 0, maximo: int = 1000000) -> int:
        """Valida y limita un valor entero"""
        try:
            valor_int = int(valor)
            return max(minimo, min(maximo, valor_int))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def preparar_fechas_periodo(fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> tuple:
        """Prepara fechas para consultas de período"""
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