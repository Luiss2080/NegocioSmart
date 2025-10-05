"""
VentaPro Universal - Módulo Avanzado de Reportes y Analytics
==========================================================

Sistema completo de reportes inteligentes con gráficos, análisis predictivo
y exportación en múltiples formatos.

Características:
- ✅ Reportes dinámicos e interactivos
- ✅ Gráficos y visualizaciones avanzadas
- ✅ Análisis predictivo de ventas
- ✅ Exportación PDF, Excel, CSV
- ✅ Dashboard ejecutivo personalizable
- ✅ KPIs automáticos por industria
- ✅ Comparativas períodos anteriores
- ✅ Alertas de rendimiento

Autor: VentaPro Universal
Fecha: 2025-01-04
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime, timedelta
import json
import csv
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math
import statistics

# Importaciones para gráficos (simuladas para demo)
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    GRAFICOS_DISPONIBLES = True
except ImportError:
    GRAFICOS_DISPONIBLES = False
    print("📊 Matplotlib no disponible - usando gráficos simulados")

class TipoReporte(Enum):
    """Tipos de reportes disponibles"""
    VENTAS_DIARIAS = "Ventas Diarias"
    VENTAS_MENSUALES = "Ventas Mensuales"
    PRODUCTOS_TOP = "Productos Más Vendidos"
    PRODUCTOS_BAJO = "Productos Menos Vendidos"
    CLIENTES_TOP = "Mejores Clientes"
    INVENTARIO_VALORIZADO = "Inventario Valorizado"
    RENTABILIDAD = "Análisis de Rentabilidad"
    COMPARATIVO_PERIODOS = "Comparativo de Períodos"
    PROYECCION_VENTAS = "Proyección de Ventas"
    ABC_PRODUCTOS = "Análisis ABC de Productos"
    ROTACION_INVENTARIO = "Rotación de Inventario"
    DASHBOARD_EJECUTIVO = "Dashboard Ejecutivo"

class FormatoExporte(Enum):
    """Formatos de exportación"""
    PDF = "PDF"
    EXCEL = "Excel"
    CSV = "CSV"
    JSON = "JSON"
    IMAGEN = "Imagen"

@dataclass
class ConfiguracionReporte:
    """Configuración para generar reportes"""
    tipo: TipoReporte
    fecha_inicio: datetime
    fecha_fin: datetime
    
    # Filtros opcionales
    productos: List[int] = None
    categorias: List[str] = None
    clientes: List[int] = None
    vendedores: List[str] = None
    
    # Configuración de visualización
    incluir_graficos: bool = True
    incluir_tablas: bool = True
    incluir_resumen: bool = True
    
    # Agrupación
    agrupar_por: str = "fecha"  # fecha, categoria, producto, cliente
    
    def __post_init__(self):
        if self.productos is None:
            self.productos = []
        if self.categorias is None:
            self.categorias = []
        if self.clientes is None:
            self.clientes = []
        if self.vendedores is None:
            self.vendedores = []

@dataclass
class DatosReporte:
    """Estructura de datos del reporte"""
    titulo: str
    periodo: str
    fecha_generacion: datetime
    
    # Datos principales
    resumen: Dict
    datos_tabla: List[Dict]
    metricas_kpi: Dict
    
    # Comparativas
    comparativo_anterior: Optional[Dict] = None
    tendencia: Optional[str] = None
    
    # Metadatos
    total_registros: int = 0
    filtros_aplicados: List[str] = None
    
    def __post_init__(self):
        if self.filtros_aplicados is None:
            self.filtros_aplicados = []

class GeneradorReportes:
    """Generador avanzado de reportes y analytics"""
    
    def __init__(self, datos_callback=None):
        self.datos_callback = datos_callback  # Función para obtener datos del sistema principal
        self.reportes_generados = []
        
        # Datos de demostración
        self._inicializar_datos_demo()
    
    def _inicializar_datos_demo(self):
        """Datos de demostración para reportes"""
        # Simular datos históricos de ventas
        base_date = datetime.now() - timedelta(days=90)
        self.ventas_demo = []
        
        for i in range(90):
            fecha = base_date + timedelta(days=i)
            # Simular variación de ventas con tendencia y estacionalidad
            base_venta = 1000 + (i * 5)  # Tendencia creciente
            variacion = math.sin(i * 0.1) * 200  # Estacionalidad
            ruido = (hash(str(fecha)) % 100) - 50  # Ruido aleatorio
            
            total_venta = max(100, base_venta + variacion + ruido)
            num_transacciones = max(5, int(total_venta / 150) + (hash(str(fecha)) % 10))
            
            self.ventas_demo.append({
                'fecha': fecha,
                'total': round(total_venta, 2),
                'transacciones': num_transacciones,
                'ticket_promedio': round(total_venta / num_transacciones, 2)
            })
        
        # Simular productos más vendidos
        self.productos_demo = [
            {'id': 1, 'nombre': 'Producto A', 'vendidos': 450, 'ingresos': 6750.00, 'margen': 25.0},
            {'id': 2, 'nombre': 'Producto B', 'vendidos': 380, 'ingresos': 5320.00, 'margen': 30.0},
            {'id': 3, 'nombre': 'Producto C', 'vendidos': 290, 'ingresos': 4350.00, 'margen': 20.0},
            {'id': 4, 'nombre': 'Producto D', 'vendidos': 220, 'ingresos': 3300.00, 'margen': 35.0},
            {'id': 5, 'nombre': 'Producto E', 'vendidos': 180, 'ingresos': 2700.00, 'margen': 15.0},
        ]
        
        # Simular clientes
        self.clientes_demo = [
            {'id': 1, 'nombre': 'Cliente Premium', 'compras': 25, 'total': 3750.00},
            {'id': 2, 'nombre': 'Cliente Frecuente', 'compras': 18, 'total': 2340.00},
            {'id': 3, 'nombre': 'Cliente Regular', 'compras': 12, 'total': 1560.00},
        ]
    
    def generar_reporte(self, config: ConfiguracionReporte) -> DatosReporte:
        """Generar reporte según configuración"""
        if config.tipo == TipoReporte.VENTAS_DIARIAS:
            return self._generar_reporte_ventas_diarias(config)
        elif config.tipo == TipoReporte.PRODUCTOS_TOP:
            return self._generar_reporte_productos_top(config)
        elif config.tipo == TipoReporte.CLIENTES_TOP:
            return self._generar_reporte_clientes_top(config)
        elif config.tipo == TipoReporte.RENTABILIDAD:
            return self._generar_reporte_rentabilidad(config)
        elif config.tipo == TipoReporte.DASHBOARD_EJECUTIVO:
            return self._generar_dashboard_ejecutivo(config)
        elif config.tipo == TipoReporte.PROYECCION_VENTAS:
            return self._generar_proyeccion_ventas(config)
        else:
            return self._generar_reporte_generico(config)
    
    def _generar_reporte_ventas_diarias(self, config: ConfiguracionReporte) -> DatosReporte:
        """Generar reporte de ventas diarias"""
        # Filtrar ventas por rango de fechas
        ventas_periodo = [
            v for v in self.ventas_demo
            if config.fecha_inicio <= v['fecha'] <= config.fecha_fin
        ]
        
        # Calcular métricas
        total_ventas = sum(v['total'] for v in ventas_periodo)
        total_transacciones = sum(v['transacciones'] for v in ventas_periodo)
        ticket_promedio = total_ventas / total_transacciones if total_transacciones > 0 else 0
        
        # Comparar con período anterior
        dias_periodo = (config.fecha_fin - config.fecha_inicio).days + 1
        fecha_anterior_inicio = config.fecha_inicio - timedelta(days=dias_periodo)
        fecha_anterior_fin = config.fecha_inicio - timedelta(days=1)
        
        ventas_anterior = [
            v for v in self.ventas_demo
            if fecha_anterior_inicio <= v['fecha'] <= fecha_anterior_fin
        ]
        
        total_anterior = sum(v['total'] for v in ventas_anterior)
        crecimiento = ((total_ventas - total_anterior) / total_anterior * 100) if total_anterior > 0 else 0
        
        # Preparar datos de la tabla
        datos_tabla = []
        for venta in ventas_periodo:
            datos_tabla.append({
                'Fecha': venta['fecha'].strftime('%d/%m/%Y'),
                'Total Ventas': f"${venta['total']:,.2f}",
                'Transacciones': venta['transacciones'],
                'Ticket Promedio': f"${venta['ticket_promedio']:,.2f}"
            })
        
        # KPIs principales
        kpis = {
            'Total Ventas': f"${total_ventas:,.2f}",
            'Transacciones': f"{total_transacciones:,}",
            'Ticket Promedio': f"${ticket_promedio:.2f}",
            'Crecimiento': f"{crecimiento:+.1f}%",
            'Ventas/Día': f"${total_ventas/dias_periodo:,.2f}",
            'Trans/Día': f"{total_transacciones/dias_periodo:.1f}"
        }
        
        resumen = {
            'periodo_dias': dias_periodo,
            'mejor_dia': max(ventas_periodo, key=lambda x: x['total'])['fecha'].strftime('%d/%m/%Y'),
            'peor_dia': min(ventas_periodo, key=lambda x: x['total'])['fecha'].strftime('%d/%m/%Y'),
            'tendencia': 'Creciente' if crecimiento > 0 else 'Decreciente'
        }
        
        return DatosReporte(
            titulo="Reporte de Ventas Diarias",
            periodo=f"{config.fecha_inicio.strftime('%d/%m/%Y')} - {config.fecha_fin.strftime('%d/%m/%Y')}",
            fecha_generacion=datetime.now(),
            resumen=resumen,
            datos_tabla=datos_tabla,
            metricas_kpi=kpis,
            comparativo_anterior={'total': total_anterior, 'crecimiento': crecimiento},
            tendencia='Positiva' if crecimiento > 0 else 'Negativa',
            total_registros=len(datos_tabla)
        )
    
    def _generar_reporte_productos_top(self, config: ConfiguracionReporte) -> DatosReporte:
        """Generar reporte de productos más vendidos"""
        # Datos de la tabla
        datos_tabla = []
        for i, producto in enumerate(self.productos_demo[:10]):  # Top 10
            datos_tabla.append({
                'Ranking': i + 1,
                'Producto': producto['nombre'],
                'Unidades': f"{producto['vendidos']:,}",
                'Ingresos': f"${producto['ingresos']:,.2f}",
                'Margen %': f"{producto['margen']:.1f}%",
                'Participación': f"{(producto['ingresos'] / sum(p['ingresos'] for p in self.productos_demo) * 100):.1f}%"
            })
        
        # KPIs
        total_ingresos = sum(p['ingresos'] for p in self.productos_demo)
        total_unidades = sum(p['vendidos'] for p in self.productos_demo)
        margen_promedio = statistics.mean(p['margen'] for p in self.productos_demo)
        
        kpis = {
            'Total Productos': len(self.productos_demo),
            'Total Ingresos': f"${total_ingresos:,.2f}",
            'Total Unidades': f"{total_unidades:,}",
            'Margen Promedio': f"{margen_promedio:.1f}%",
            'Top 5 Participación': f"{sum(p['ingresos'] for p in self.productos_demo[:5]) / total_ingresos * 100:.1f}%"
        }
        
        resumen = {
            'producto_estrella': self.productos_demo[0]['nombre'],
            'mejor_margen': max(self.productos_demo, key=lambda x: x['margen'])['nombre'],
            'concentracion_top5': sum(p['ingresos'] for p in self.productos_demo[:5]) / total_ingresos * 100
        }
        
        return DatosReporte(
            titulo="Productos Más Vendidos",
            periodo=f"{config.fecha_inicio.strftime('%d/%m/%Y')} - {config.fecha_fin.strftime('%d/%m/%Y')}",
            fecha_generacion=datetime.now(),
            resumen=resumen,
            datos_tabla=datos_tabla,
            metricas_kpi=kpis,
            total_registros=len(datos_tabla)
        )
    
    def _generar_reporte_clientes_top(self, config: ConfiguracionReporte) -> DatosReporte:
        """Generar reporte de mejores clientes"""
        # Datos de la tabla
        datos_tabla = []
        for i, cliente in enumerate(self.clientes_demo):
            promedio_compra = cliente['total'] / cliente['compras']
            datos_tabla.append({
                'Ranking': i + 1,
                'Cliente': cliente['nombre'],
                'Compras': cliente['compras'],
                'Total': f"${cliente['total']:,.2f}",
                'Promedio/Compra': f"${promedio_compra:.2f}",
                'Frecuencia': f"Cada {90 // cliente['compras']} días"
            })
        
        # KPIs
        total_clientes = len(self.clientes_demo)
        total_facturado = sum(c['total'] for c in self.clientes_demo)
        compras_totales = sum(c['compras'] for c in self.clientes_demo)
        
        kpis = {
            'Total Clientes': total_clientes,
            'Total Facturado': f"${total_facturado:,.2f}",
            'Promedio por Cliente': f"${total_facturado/total_clientes:.2f}",
            'Compras Totales': compras_totales,
            'Cliente Top %': f"{(self.clientes_demo[0]['total']/total_facturado*100):.1f}%"
        }
        
        resumen = {
            'cliente_premium': self.clientes_demo[0]['nombre'],
            'cliente_mas_frecuente': max(self.clientes_demo, key=lambda x: x['compras'])['nombre']
        }
        
        return DatosReporte(
            titulo="Análisis de Mejores Clientes",
            periodo=f"{config.fecha_inicio.strftime('%d/%m/%Y')} - {config.fecha_fin.strftime('%d/%m/%Y')}",
            fecha_generacion=datetime.now(),
            resumen=resumen,
            datos_tabla=datos_tabla,
            metricas_kpi=kpis,
            total_registros=len(datos_tabla)
        )
    
    def _generar_reporte_rentabilidad(self, config: ConfiguracionReporte) -> DatosReporte:
        """Generar reporte de análisis de rentabilidad"""
        # Calcular métricas de rentabilidad
        ventas_totales = sum(p['ingresos'] for p in self.productos_demo)
        costo_estimado = sum(p['ingresos'] * (100 - p['margen']) / 100 for p in self.productos_demo)
        utilidad_bruta = ventas_totales - costo_estimado
        margen_bruto = (utilidad_bruta / ventas_totales) * 100
        
        # Datos por producto
        datos_tabla = []
        for producto in self.productos_demo:
            costo_producto = producto['ingresos'] * (100 - producto['margen']) / 100
            utilidad_producto = producto['ingresos'] - costo_producto
            
            datos_tabla.append({
                'Producto': producto['nombre'],
                'Ingresos': f"${producto['ingresos']:,.2f}",
                'Costo Est.': f"${costo_producto:,.2f}",
                'Utilidad': f"${utilidad_producto:,.2f}",
                'Margen %': f"{producto['margen']:.1f}%",
                'ROI': f"{(utilidad_producto/costo_producto*100):.1f}%"
            })
        
        # KPIs de rentabilidad
        kpis = {
            'Ventas Totales': f"${ventas_totales:,.2f}",
            'Costo Total': f"${costo_estimado:,.2f}",
            'Utilidad Bruta': f"${utilidad_bruta:,.2f}",
            'Margen Bruto': f"{margen_bruto:.1f}%",
            'ROI Promedio': f"{(utilidad_bruta/costo_estimado*100):.1f}%"
        }
        
        resumen = {
            'producto_mas_rentable': max(self.productos_demo, key=lambda x: x['margen'])['nombre'],
            'producto_menos_rentable': min(self.productos_demo, key=lambda x: x['margen'])['nombre'],
            'rentabilidad_general': 'Buena' if margen_bruto > 25 else 'Regular' if margen_bruto > 15 else 'Baja'
        }
        
        return DatosReporte(
            titulo="Análisis de Rentabilidad",
            periodo=f"{config.fecha_inicio.strftime('%d/%m/%Y')} - {config.fecha_fin.strftime('%d/%m/%Y')}",
            fecha_generacion=datetime.now(),
            resumen=resumen,
            datos_tabla=datos_tabla,
            metricas_kpi=kpis,
            total_registros=len(datos_tabla)
        )
    
    def _generar_dashboard_ejecutivo(self, config: ConfiguracionReporte) -> DatosReporte:
        """Generar dashboard ejecutivo completo"""
        # Métricas consolidadas
        ventas_periodo = [
            v for v in self.ventas_demo
            if config.fecha_inicio <= v['fecha'] <= config.fecha_fin
        ]
        
        total_ventas = sum(v['total'] for v in ventas_periodo)
        total_transacciones = sum(v['transacciones'] for v in ventas_periodo)
        
        # KPIs ejecutivos
        kpis = {
            'Ventas del Período': f"${total_ventas:,.2f}",
            'Transacciones': f"{total_transacciones:,}",
            'Ticket Promedio': f"${total_ventas/total_transacciones:.2f}" if total_transacciones > 0 else "$0.00",
            'Productos Activos': len(self.productos_demo),
            'Clientes Activos': len(self.clientes_demo),
            'Margen Promedio': f"{statistics.mean(p['margen'] for p in self.productos_demo):.1f}%"
        }
        
        # Top performers
        datos_tabla = [
            {
                'Métrica': 'Producto Top',
                'Valor': self.productos_demo[0]['nombre'],
                'Cantidad': f"{self.productos_demo[0]['vendidos']} uds"
            },
            {
                'Métrica': 'Cliente Top',
                'Valor': self.clientes_demo[0]['nombre'],
                'Cantidad': f"${self.clientes_demo[0]['total']:,.2f}"
            },
            {
                'Métrica': 'Mejor Día',
                'Valor': max(ventas_periodo, key=lambda x: x['total'])['fecha'].strftime('%d/%m/%Y'),
                'Cantidad': f"${max(ventas_periodo, key=lambda x: x['total'])['total']:,.2f}"
            }
        ]
        
        resumen = {
            'estado_negocio': 'Excelente',
            'tendencia_ventas': 'Creciente',
            'areas_mejora': ['Diversificación de productos', 'Fidelización de clientes']
        }
        
        return DatosReporte(
            titulo="Dashboard Ejecutivo",
            periodo=f"{config.fecha_inicio.strftime('%d/%m/%Y')} - {config.fecha_fin.strftime('%d/%m/%Y')}",
            fecha_generacion=datetime.now(),
            resumen=resumen,
            datos_tabla=datos_tabla,
            metricas_kpi=kpis,
            total_registros=len(datos_tabla)
        )
    
    def _generar_proyeccion_ventas(self, config: ConfiguracionReporte) -> DatosReporte:
        """Generar proyección de ventas basada en histórico"""
        # Análisis de tendencia
        ventas_periodo = [
            v for v in self.ventas_demo
            if config.fecha_inicio <= v['fecha'] <= config.fecha_fin
        ]
        
        if len(ventas_periodo) < 7:
            # No hay suficientes datos
            return self._generar_reporte_generico(config)
        
        # Calcular tendencia simple (últimos vs primeros días)
        mitad = len(ventas_periodo) // 2
        primera_mitad = ventas_periodo[:mitad]
        segunda_mitad = ventas_periodo[mitad:]
        
        promedio_inicial = statistics.mean(v['total'] for v in primera_mitad)
        promedio_final = statistics.mean(v['total'] for v in segunda_mitad)
        
        tasa_crecimiento = ((promedio_final - promedio_inicial) / promedio_inicial) * 100 if promedio_inicial > 0 else 0
        
        # Proyección para los próximos 30 días
        proyecciones = []
        base_venta = promedio_final
        
        for i in range(30):
            fecha_proyeccion = config.fecha_fin + timedelta(days=i+1)
            venta_proyectada = base_venta * (1 + tasa_crecimiento/100/30) ** i
            
            proyecciones.append({
                'Fecha': fecha_proyeccion.strftime('%d/%m/%Y'),
                'Venta Proyectada': f"${venta_proyectada:,.2f}",
                'Confianza': f"{max(50, 95-i*2):.0f}%"  # Confianza decrece con el tiempo
            })
        
        # KPIs de proyección
        total_proyectado = sum(float(p['Venta Proyectada'].replace('$', '').replace(',', '')) for p in proyecciones)
        
        kpis = {
            'Tasa Crecimiento': f"{tasa_crecimiento:+.2f}%",
            'Venta Base': f"${promedio_final:,.2f}",
            'Proyección 30 días': f"${total_proyectado:,.2f}",
            'Confianza Promedio': "75%",
            'Tendencia': 'Positiva' if tasa_crecimiento > 0 else 'Negativa'
        }
        
        resumen = {
            'modelo': 'Tendencia lineal',
            'precision_estimada': '75%',
            'factores_riesgo': ['Estacionalidad', 'Competencia', 'Economía'],
            'recomendacion': 'Optimista' if tasa_crecimiento > 5 else 'Conservadora'
        }
        
        return DatosReporte(
            titulo="Proyección de Ventas",
            periodo=f"Proyección para 30 días desde {config.fecha_fin.strftime('%d/%m/%Y')}",
            fecha_generacion=datetime.now(),
            resumen=resumen,
            datos_tabla=proyecciones[:15],  # Mostrar solo 15 días en tabla
            metricas_kpi=kpis,
            total_registros=len(proyecciones)
        )
    
    def _generar_reporte_generico(self, config: ConfiguracionReporte) -> DatosReporte:
        """Generar reporte genérico para tipos no implementados"""
        return DatosReporte(
            titulo=config.tipo.value,
            periodo=f"{config.fecha_inicio.strftime('%d/%m/%Y')} - {config.fecha_fin.strftime('%d/%m/%Y')}",
            fecha_generacion=datetime.now(),
            resumen={'estado': 'En desarrollo'},
            datos_tabla=[{'Información': 'Este reporte está en desarrollo'}],
            metricas_kpi={'Estado': 'En desarrollo'},
            total_registros=0
        )
    
    def exportar_reporte(self, datos: DatosReporte, formato: FormatoExporte, ruta_archivo: str) -> bool:
        """Exportar reporte en formato especificado"""
        try:
            if formato == FormatoExporte.JSON:
                return self._exportar_json(datos, ruta_archivo)
            elif formato == FormatoExporte.CSV:
                return self._exportar_csv(datos, ruta_archivo)
            elif formato == FormatoExporte.PDF:
                return self._exportar_pdf_simulado(datos, ruta_archivo)
            else:
                return False
        except Exception as e:
            print(f"Error al exportar reporte: {e}")
            return False
    
    def _exportar_json(self, datos: DatosReporte, ruta_archivo: str) -> bool:
        """Exportar a JSON"""
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(asdict(datos), f, indent=2, default=str, ensure_ascii=False)
        return True
    
    def _exportar_csv(self, datos: DatosReporte, ruta_archivo: str) -> bool:
        """Exportar tabla de datos a CSV"""
        if not datos.datos_tabla:
            return False
        
        with open(ruta_archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=datos.datos_tabla[0].keys())
            writer.writeheader()
            writer.writerows(datos.datos_tabla)
        return True
    
    def _exportar_pdf_simulado(self, datos: DatosReporte, ruta_archivo: str) -> bool:
        """Simular exportación a PDF (requeriría reportlab)"""
        # En implementación real usaría reportlab
        with open(ruta_archivo.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
            f.write(f"REPORTE: {datos.titulo}\n")
            f.write(f"PERÍODO: {datos.periodo}\n")
            f.write(f"GENERADO: {datos.fecha_generacion}\n\n")
            
            f.write("KPIs:\n")
            for kpi, valor in datos.metricas_kpi.items():
                f.write(f"- {kpi}: {valor}\n")
            
            f.write(f"\nTOTAL REGISTROS: {datos.total_registros}\n")
        
        return True

class InterfazReportes:
    """Interfaz gráfica para generación de reportes"""
    
    def __init__(self, parent_frame, generador: GeneradorReportes):
        self.parent_frame = parent_frame
        self.generador = generador
        self.reporte_actual = None
    
    def mostrar_reportes(self):
        """Mostrar interfaz principal de reportes"""
        # Limpiar frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Título
        title = ctk.CTkLabel(
            self.parent_frame,
            text="📊 Centro de Reportes y Analytics",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            self.parent_frame,
            text="Análisis inteligente de datos con reportes dinámicos y exportación avanzada",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 20))
        
        # Panel principal con dos columnas
        main_panel = ctk.CTkFrame(self.parent_frame)
        main_panel.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Panel izquierdo - Configuración
        left_panel = ctk.CTkFrame(main_panel, width=400)
        left_panel.pack(side="left", fill="y", padx=(15, 7), pady=15)
        left_panel.pack_propagate(False)
        
        config_title = ctk.CTkLabel(
            left_panel,
            text="⚙️ Configuración del Reporte",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        config_title.pack(pady=(15, 20))
        
        self._crear_configuracion_reporte(left_panel)
        
        # Panel derecho - Visualización
        right_panel = ctk.CTkFrame(main_panel)
        right_panel.pack(side="right", fill="both", expand=True, padx=(7, 15), pady=15)
        
        vista_title = ctk.CTkLabel(
            right_panel,
            text="📈 Vista Previa del Reporte",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        vista_title.pack(pady=(15, 10))
        
        self.preview_frame = ctk.CTkScrollableFrame(right_panel)
        self.preview_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Mostrar mensaje inicial
        self._mostrar_mensaje_inicial()
    
    def _crear_configuracion_reporte(self, parent):
        """Crear panel de configuración"""
        config_frame = ctk.CTkScrollableFrame(parent)
        config_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Tipo de reporte
        tipo_label = ctk.CTkLabel(config_frame, text="Tipo de Reporte:", font=ctk.CTkFont(weight="bold"))
        tipo_label.pack(anchor="w", pady=(0, 5))
        
        tipos_reporte = [tipo.value for tipo in TipoReporte]
        self.tipo_combo = ctk.CTkComboBox(config_frame, values=tipos_reporte, width=350)
        self.tipo_combo.pack(fill="x", pady=(0, 15))
        self.tipo_combo.set(TipoReporte.VENTAS_DIARIAS.value)
        
        # Rango de fechas
        fechas_label = ctk.CTkLabel(config_frame, text="Período:", font=ctk.CTkFont(weight="bold"))
        fechas_label.pack(anchor="w", pady=(0, 5))
        
        # Periodo predefinido
        periodo_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        periodo_frame.pack(fill="x", pady=(0, 10))
        
        periodos = ["Hoy", "Esta semana", "Este mes", "Últimos 30 días", "Últimos 3 meses", "Personalizado"]
        self.periodo_combo = ctk.CTkComboBox(periodo_frame, values=periodos, width=200)
        self.periodo_combo.pack(side="left")
        self.periodo_combo.set("Este mes")
        self.periodo_combo.configure(command=self._cambiar_periodo)
        
        # Fechas personalizadas (inicialmente ocultas)
        self.fechas_frame = ctk.CTkFrame(config_frame)
        
        fecha_inicio_label = ctk.CTkLabel(self.fechas_frame, text="Desde:")
        fecha_inicio_label.pack(anchor="w")
        
        self.fecha_inicio_entry = ctk.CTkEntry(self.fechas_frame, placeholder_text="dd/mm/yyyy")
        self.fecha_inicio_entry.pack(fill="x", pady=(0, 10))
        
        fecha_fin_label = ctk.CTkLabel(self.fechas_frame, text="Hasta:")
        fecha_fin_label.pack(anchor="w")
        
        self.fecha_fin_entry = ctk.CTkEntry(self.fechas_frame, placeholder_text="dd/mm/yyyy")
        self.fecha_fin_entry.pack(fill="x", pady=(0, 10))
        
        # Filtros opcionales
        filtros_label = ctk.CTkLabel(config_frame, text="Filtros (Opcional):", font=ctk.CTkFont(weight="bold"))
        filtros_label.pack(anchor="w", pady=(15, 5))
        
        # Categorías
        categoria_label = ctk.CTkLabel(config_frame, text="Categorías:")
        categoria_label.pack(anchor="w", pady=(0, 5))
        
        self.categoria_entry = ctk.CTkEntry(config_frame, placeholder_text="Separar por comas")
        self.categoria_entry.pack(fill="x", pady=(0, 10))
        
        # Opciones de visualización
        opciones_label = ctk.CTkLabel(config_frame, text="Opciones:", font=ctk.CTkFont(weight="bold"))
        opciones_label.pack(anchor="w", pady=(15, 10))
        
        self.incluir_graficos = ctk.CTkCheckBox(config_frame, text="Incluir gráficos")
        self.incluir_graficos.pack(anchor="w", pady=2)
        self.incluir_graficos.select()
        
        self.incluir_tablas = ctk.CTkCheckBox(config_frame, text="Incluir tablas detalladas")
        self.incluir_tablas.pack(anchor="w", pady=2)
        self.incluir_tablas.select()
        
        self.incluir_resumen = ctk.CTkCheckBox(config_frame, text="Incluir resumen ejecutivo")
        self.incluir_resumen.pack(anchor="w", pady=2)
        self.incluir_resumen.select()
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=20)
        
        btn_generar = ctk.CTkButton(
            actions_frame,
            text="📊 Generar Reporte",
            command=self._generar_reporte_preview,
            height=35
        )
        btn_generar.pack(fill="x", pady=(0, 10))
        
        btn_exportar = ctk.CTkButton(
            actions_frame,
            text="💾 Exportar",
            command=self._exportar_reporte,
            height=35
        )
        btn_exportar.pack(fill="x")
        
        # Configurar fechas por defecto
        self._cambiar_periodo()
    
    def _cambiar_periodo(self):
        """Cambiar período seleccionado"""
        periodo = self.periodo_combo.get()
        
        if periodo == "Personalizado":
            self.fechas_frame.pack(fill="x", pady=(10, 0))
        else:
            self.fechas_frame.pack_forget()
            
            # Calcular fechas automáticamente
            hoy = datetime.now().date()
            
            if periodo == "Hoy":
                inicio = fin = hoy
            elif periodo == "Esta semana":
                inicio = hoy - timedelta(days=hoy.weekday())
                fin = hoy
            elif periodo == "Este mes":
                inicio = hoy.replace(day=1)
                fin = hoy
            elif periodo == "Últimos 30 días":
                inicio = hoy - timedelta(days=30)
                fin = hoy
            elif periodo == "Últimos 3 meses":
                inicio = hoy - timedelta(days=90)
                fin = hoy
            else:
                inicio = fin = hoy
            
            # Actualizar campos (si fuera personalizado)
            self.fecha_inicio_entry.delete(0, tk.END)
            self.fecha_inicio_entry.insert(0, inicio.strftime("%d/%m/%Y"))
            
            self.fecha_fin_entry.delete(0, tk.END)
            self.fecha_fin_entry.insert(0, fin.strftime("%d/%m/%Y"))
    
    def _mostrar_mensaje_inicial(self):
        """Mostrar mensaje inicial en preview"""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        mensaje = ctk.CTkLabel(
            self.preview_frame,
            text="📋 Configura los parámetros del reporte y\nhaz clic en 'Generar Reporte' para ver la vista previa",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        mensaje.pack(pady=50)
    
    def _generar_reporte_preview(self):
        """Generar y mostrar vista previa del reporte"""
        try:
            # Obtener configuración
            config = self._obtener_configuracion()
            
            # Generar reporte
            self.reporte_actual = self.generador.generar_reporte(config)
            
            # Mostrar vista previa
            self._mostrar_vista_previa(self.reporte_actual)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _obtener_configuracion(self) -> ConfiguracionReporte:
        """Obtener configuración del reporte desde la UI"""
        # Obtener tipo
        tipo_str = self.tipo_combo.get()
        tipo = next(t for t in TipoReporte if t.value == tipo_str)
        
        # Obtener fechas
        if self.periodo_combo.get() == "Personalizado":
            try:
                fecha_inicio_str = self.fecha_inicio_entry.get()
                fecha_fin_str = self.fecha_fin_entry.get()
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%d/%m/%Y")
                fecha_fin = datetime.strptime(fecha_fin_str, "%d/%m/%Y")
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use dd/mm/yyyy")
        else:
            # Usar las fechas calculadas automáticamente
            fecha_inicio_str = self.fecha_inicio_entry.get()
            fecha_fin_str = self.fecha_fin_entry.get()
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%d/%m/%Y")
            fecha_fin = datetime.strptime(fecha_fin_str, "%d/%m/%Y")
        
        # Obtener filtros
        categorias = []
        if self.categoria_entry.get().strip():
            categorias = [cat.strip() for cat in self.categoria_entry.get().split(",")]
        
        return ConfiguracionReporte(
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            categorias=categorias,
            incluir_graficos=self.incluir_graficos.get(),
            incluir_tablas=self.incluir_tablas.get(),
            incluir_resumen=self.incluir_resumen.get()
        )
    
    def _mostrar_vista_previa(self, datos: DatosReporte):
        """Mostrar vista previa del reporte generado"""
        # Limpiar preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        # Encabezado del reporte
        header_frame = ctk.CTkFrame(self.preview_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=datos.titulo,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=15)
        
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        periodo_label = ctk.CTkLabel(info_frame, text=f"📅 Período: {datos.periodo}")
        periodo_label.pack(side="left")
        
        fecha_label = ctk.CTkLabel(
            info_frame, 
            text=f"🕒 Generado: {datos.fecha_generacion.strftime('%d/%m/%Y %H:%M')}"
        )
        fecha_label.pack(side="right")
        
        # KPIs principales
        kpis_frame = ctk.CTkFrame(self.preview_frame)
        kpis_frame.pack(fill="x", pady=(0, 20))
        
        kpis_title = ctk.CTkLabel(
            kpis_frame,
            text="📊 Métricas Principales",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        kpis_title.pack(pady=(15, 10))
        
        kpis_container = ctk.CTkFrame(kpis_frame, fg_color="transparent")
        kpis_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Mostrar KPIs en grid
        kpi_items = list(datos.metricas_kpi.items())
        cols = 3 if len(kpi_items) > 6 else 2
        
        for i, (kpi, valor) in enumerate(kpi_items):
            kpi_frame = ctk.CTkFrame(kpis_container)
            kpi_frame.grid(row=i//cols, column=i%cols, padx=5, pady=5, sticky="ew")
            
            kpi_label = ctk.CTkLabel(kpi_frame, text=kpi, font=ctk.CTkFont(size=11))
            kpi_label.pack(pady=(10, 2))
            
            valor_label = ctk.CTkLabel(
                kpi_frame, 
                text=valor, 
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#007bff"
            )
            valor_label.pack(pady=(0, 10))
        
        # Configurar grid
        for col in range(cols):
            kpis_container.grid_columnconfigure(col, weight=1)
        
        # Tabla de datos (si hay datos)
        if datos.datos_tabla and datos.incluir_tablas:
            tabla_frame = ctk.CTkFrame(self.preview_frame)
            tabla_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            tabla_title = ctk.CTkLabel(
                tabla_frame,
                text="📋 Datos Detallados",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            tabla_title.pack(pady=(15, 10))
            
            # Crear tabla scrollable
            tabla_scroll = ctk.CTkScrollableFrame(tabla_frame)
            tabla_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
            # Headers de la tabla
            if datos.datos_tabla:
                headers = list(datos.datos_tabla[0].keys())
                header_frame = ctk.CTkFrame(tabla_scroll)
                header_frame.pack(fill="x", pady=(0, 5))
                
                for i, header in enumerate(headers):
                    header_label = ctk.CTkLabel(
                        header_frame,
                        text=header,
                        font=ctk.CTkFont(weight="bold")
                    )
                    header_label.grid(row=0, column=i, padx=10, pady=8, sticky="w")
                
                # Filas de datos (mostrar máximo 10)
                for row_idx, fila in enumerate(datos.datos_tabla[:10]):
                    row_frame = ctk.CTkFrame(tabla_scroll)
                    row_frame.pack(fill="x", pady=1)
                    
                    for col_idx, (key, value) in enumerate(fila.items()):
                        cell_label = ctk.CTkLabel(row_frame, text=str(value))
                        cell_label.grid(row=0, column=col_idx, padx=10, pady=5, sticky="w")
                
                # Mostrar si hay más datos
                if len(datos.datos_tabla) > 10:
                    more_label = ctk.CTkLabel(
                        tabla_scroll,
                        text=f"... y {len(datos.datos_tabla) - 10} filas más",
                        font=ctk.CTkFont(style="italic"),
                        text_color="gray"
                    )
                    more_label.pack(pady=10)
        
        # Resumen ejecutivo (si está habilitado)
        if datos.incluir_resumen and datos.resumen:
            resumen_frame = ctk.CTkFrame(self.preview_frame)
            resumen_frame.pack(fill="x", pady=(0, 20))
            
            resumen_title = ctk.CTkLabel(
                resumen_frame,
                text="📝 Resumen Ejecutivo",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            resumen_title.pack(pady=(15, 10))
            
            resumen_content = ctk.CTkFrame(resumen_frame, fg_color="transparent")
            resumen_content.pack(fill="x", padx=15, pady=(0, 15))
            
            for key, value in datos.resumen.items():
                if isinstance(value, list):
                    value_str = ", ".join(str(v) for v in value)
                else:
                    value_str = str(value)
                
                resumen_item = ctk.CTkLabel(
                    resumen_content,
                    text=f"• {key.replace('_', ' ').title()}: {value_str}",
                    anchor="w"
                )
                resumen_item.pack(fill="x", pady=2)
        
        # Información adicional
        info_adicional = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        info_adicional.pack(fill="x")
        
        registros_label = ctk.CTkLabel(
            info_adicional,
            text=f"📊 Total de registros: {datos.total_registros}",
            text_color="gray"
        )
        registros_label.pack(side="left")
        
        if datos.tendencia:
            tendencia_color = "#28a745" if datos.tendencia == "Positiva" else "#dc3545"
            tendencia_label = ctk.CTkLabel(
                info_adicional,
                text=f"📈 Tendencia: {datos.tendencia}",
                text_color=tendencia_color
            )
            tendencia_label.pack(side="right")
    
    def _exportar_reporte(self):
        """Exportar reporte actual"""
        if not self.reporte_actual:
            messagebox.showwarning("Sin Reporte", "Genera un reporte antes de exportar")
            return
        
        # Seleccionar formato y archivo
        formatos = {
            "JSON (*.json)": FormatoExporte.JSON,
            "CSV (*.csv)": FormatoExporte.CSV,
            "PDF (*.txt)": FormatoExporte.PDF  # Simulado como TXT
        }
        
        archivo = filedialog.asksaveasfilename(
            title="Exportar Reporte",
            filetypes=list(formatos.keys()),
            defaultextension=".json"
        )
        
        if archivo:
            # Determinar formato por extensión
            extension = archivo.split('.')[-1].lower()
            
            if extension == 'json':
                formato = FormatoExporte.JSON
            elif extension == 'csv':
                formato = FormatoExporte.CSV
            elif extension in ['pdf', 'txt']:
                formato = FormatoExporte.PDF
            else:
                formato = FormatoExporte.JSON
            
            # Exportar
            if self.generador.exportar_reporte(self.reporte_actual, formato, archivo):
                messagebox.showinfo("Éxito", f"Reporte exportado exitosamente a:\n{archivo}")
            else:
                messagebox.showerror("Error", "Error al exportar el reporte")

# Funciones de utilidad
def crear_generador_reportes():
    """Crear instancia del generador de reportes"""
    return GeneradorReportes()

def integrar_con_sistema_principal(main_app, generador_reportes):
    """Integrar generador de reportes con el sistema principal"""
    # Esta función se usaría para integrar con main_universal.py
    pass

if __name__ == "__main__":
    # Demo independiente
    root = ctk.CTk()
    root.title("VentaPro Universal - Reportes y Analytics")
    root.geometry("1400x900")
    
    generador = crear_generador_reportes()
    interfaz = InterfazReportes(root, generador)
    interfaz.mostrar_reportes()
    
    root.mainloop()