"""
Sistema de Backup Automático - VentaPro Universal
================================================

Gestiona backups automáticos de todos los datos del sistema en archivos JSON/CSV
separados por tipo de información dentro de la carpeta backups.

Autor: Sistema VentaPro
Fecha: 2025-10-05
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

class BackupManager:
    """Gestor de backups automáticos del sistema"""
    
    def __init__(self):
        self.backup_dir = "data/backups"
        self.ensure_backup_directory()
        
    def ensure_backup_directory(self):
        """Asegurar que existe el directorio de backups"""
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Crear subdirectorios por tipo de datos
        subdirs = [
            "productos", "clientes", "ventas", "reportes", 
            "configuracion", "sesiones", "logs_actividad"
        ]
        
        for subdir in subdirs:
            Path(f"{self.backup_dir}/{subdir}").mkdir(exist_ok=True)
    
    def generar_timestamp(self) -> str:
        """Generar timestamp único para archivos"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generar_fecha_legible(self) -> str:
        """Generar fecha legible para reportes"""
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # =================== BACKUP DE PRODUCTOS ===================
    
    def backup_producto_nuevo(self, producto_data: Dict[str, Any]) -> str:
        """Backup cuando se registra un nuevo producto"""
        timestamp = self.generar_timestamp()
        filename = f"{self.backup_dir}/productos/producto_{timestamp}.json"
        
        backup_data = {
            "tipo": "nuevo_producto",
            "timestamp": timestamp,
            "fecha_legible": self.generar_fecha_legible(),
            "accion": "Registro de nuevo producto",
            "datos": producto_data,
            "metadatos": {
                "usuario": "sistema",
                "version": "1.0",
                "origen": "formulario_registro"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # También crear backup CSV
        self._backup_producto_csv(producto_data, "nuevo")
        
        return filename
    
    def backup_producto_modificado(self, producto_anterior: Dict, producto_nuevo: Dict) -> str:
        """Backup cuando se modifica un producto"""
        timestamp = self.generar_timestamp()
        filename = f"{self.backup_dir}/productos/modificacion_{timestamp}.json"
        
        backup_data = {
            "tipo": "producto_modificado",
            "timestamp": timestamp,
            "fecha_legible": self.generar_fecha_legible(),
            "accion": "Modificación de producto",
            "datos_anteriores": producto_anterior,
            "datos_nuevos": producto_nuevo,
            "cambios_detectados": self._detectar_cambios(producto_anterior, producto_nuevo),
            "metadatos": {
                "usuario": "sistema",
                "version": "1.0",
                "origen": "formulario_edicion"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def _backup_producto_csv(self, producto_data: Dict, accion: str):
        """Backup en formato CSV para productos"""
        csv_file = f"{self.backup_dir}/productos/productos_log.csv"
        
        # Headers del CSV
        headers = [
            'timestamp', 'fecha', 'accion', 'codigo', 'nombre', 
            'categoria', 'precio_compra', 'precio_venta', 'stock', 
            'stock_minimo', 'activo'
        ]
        
        # Verificar si el archivo existe
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Escribir headers solo si es un archivo nuevo
            if not file_exists:
                writer.writerow(headers)
            
            # Escribir datos del producto
            row = [
                self.generar_timestamp(),
                self.generar_fecha_legible(),
                accion,
                producto_data.get('codigo', ''),
                producto_data.get('nombre', ''),
                producto_data.get('categoria', ''),
                producto_data.get('precio_compra', 0),
                producto_data.get('precio_venta', 0),
                producto_data.get('stock', 0),
                producto_data.get('stock_minimo', 0),
                producto_data.get('activo', True)
            ]
            writer.writerow(row)
    
    # =================== BACKUP DE CLIENTES ===================
    
    def backup_cliente_nuevo(self, cliente_data: Dict[str, Any]) -> str:
        """Backup cuando se registra un nuevo cliente"""
        timestamp = self.generar_timestamp()
        filename = f"{self.backup_dir}/clientes/cliente_{timestamp}.json"
        
        backup_data = {
            "tipo": "nuevo_cliente",
            "timestamp": timestamp,
            "fecha_legible": self.generar_fecha_legible(),
            "accion": "Registro de nuevo cliente",
            "datos": cliente_data,
            "metadatos": {
                "usuario": "sistema",
                "version": "1.0",
                "origen": "formulario_registro"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # También crear backup CSV
        self._backup_cliente_csv(cliente_data, "nuevo")
        
        return filename
    
    def _backup_cliente_csv(self, cliente_data: Dict, accion: str):
        """Backup en formato CSV para clientes"""
        csv_file = f"{self.backup_dir}/clientes/clientes_log.csv"
        
        headers = [
            'timestamp', 'fecha', 'accion', 'codigo', 'nombre', 
            'apellidos', 'email', 'telefono', 'direccion', 
            'rfc', 'activo'
        ]
        
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(headers)
            
            row = [
                self.generar_timestamp(),
                self.generar_fecha_legible(),
                accion,
                cliente_data.get('codigo', ''),
                cliente_data.get('nombre', ''),
                cliente_data.get('apellidos', ''),
                cliente_data.get('email', ''),
                cliente_data.get('telefono', ''),
                cliente_data.get('direccion', ''),
                cliente_data.get('rfc', ''),
                cliente_data.get('activo', True)
            ]
            writer.writerow(row)
    
    # =================== BACKUP DE VENTAS ===================
    
    def backup_venta_procesada(self, venta_data: Dict[str, Any], carrito: List[Dict]) -> str:
        """Backup cuando se procesa una venta"""
        timestamp = self.generar_timestamp()
        filename = f"{self.backup_dir}/ventas/venta_{timestamp}.json"
        
        backup_data = {
            "tipo": "venta_procesada",
            "timestamp": timestamp,
            "fecha_legible": self.generar_fecha_legible(),
            "accion": "Procesamiento de venta",
            "venta": venta_data,
            "productos_vendidos": carrito,
            "totales": {
                "subtotal": sum(item.get('subtotal', 0) for item in carrito),
                "total_items": len(carrito),
                "cantidad_productos": sum(item.get('cantidad', 0) for item in carrito)
            },
            "metadatos": {
                "usuario": "sistema",
                "version": "1.0",
                "origen": "punto_venta"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # También crear backup CSV
        self._backup_venta_csv(venta_data, carrito)
        
        return filename
    
    def _backup_venta_csv(self, venta_data: Dict, carrito: List[Dict]):
        """Backup en formato CSV para ventas"""
        # CSV de ventas generales
        ventas_csv = f"{self.backup_dir}/ventas/ventas_log.csv"
        headers_venta = [
            'timestamp', 'fecha', 'venta_id', 'total', 'items', 
            'cliente', 'metodo_pago'
        ]
        
        file_exists = os.path.exists(ventas_csv)
        
        with open(ventas_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(headers_venta)
            
            row = [
                self.generar_timestamp(),
                self.generar_fecha_legible(),
                venta_data.get('id', ''),
                venta_data.get('total', 0),
                venta_data.get('items', 0),
                venta_data.get('cliente', 'Mostrador'),
                venta_data.get('metodo_pago', 'efectivo')
            ]
            writer.writerow(row)
        
        # CSV de detalles de venta
        detalle_csv = f"{self.backup_dir}/ventas/detalle_ventas_log.csv"
        headers_detalle = [
            'timestamp', 'fecha', 'venta_id', 'producto_id', 
            'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal'
        ]
        
        file_exists_detalle = os.path.exists(detalle_csv)
        
        with open(detalle_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists_detalle:
                writer.writerow(headers_detalle)
            
            for item in carrito:
                row = [
                    self.generar_timestamp(),
                    self.generar_fecha_legible(),
                    venta_data.get('id', ''),
                    item.get('id', ''),
                    item.get('nombre', ''),
                    item.get('cantidad', 0),
                    item.get('precio', 0),
                    item.get('subtotal', 0)
                ]
                writer.writerow(row)
    
    # =================== BACKUP DE REPORTES ===================
    
    def backup_reporte_generado(self, tipo_reporte: str, datos_reporte: Dict) -> str:
        """Backup cuando se genera un reporte"""
        timestamp = self.generar_timestamp()
        filename = f"{self.backup_dir}/reportes/reporte_{tipo_reporte}_{timestamp}.json"
        
        backup_data = {
            "tipo": f"reporte_{tipo_reporte}",
            "timestamp": timestamp,
            "fecha_legible": self.generar_fecha_legible(),
            "accion": f"Generación de reporte: {tipo_reporte}",
            "datos_reporte": datos_reporte,
            "metadatos": {
                "usuario": "sistema",
                "version": "1.0",
                "origen": "centro_reportes"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    # =================== BACKUP DE SESIONES ===================
    
    def backup_sesion_actividad(self, actividades: List[Dict]) -> str:
        """Backup de actividades de la sesión"""
        timestamp = self.generar_timestamp()
        filename = f"{self.backup_dir}/sesiones/sesion_{timestamp}.json"
        
        backup_data = {
            "tipo": "sesion_actividad",
            "timestamp": timestamp,
            "fecha_legible": self.generar_fecha_legible(),
            "accion": "Registro de actividades de sesión",
            "actividades": actividades,
            "estadisticas": {
                "total_actividades": len(actividades),
                "duracion_sesion": "calculada_automaticamente"
            },
            "metadatos": {
                "usuario": "sistema",
                "version": "1.0",
                "origen": "sesion_usuario"
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    # =================== UTILIDADES ===================
    
    def _detectar_cambios(self, datos_anteriores: Dict, datos_nuevos: Dict) -> List[str]:
        """Detectar qué campos cambiaron entre dos versiones de datos"""
        cambios = []
        
        for campo in datos_nuevos.keys():
            if campo in datos_anteriores:
                if datos_anteriores[campo] != datos_nuevos[campo]:
                    cambios.append(f"{campo}: '{datos_anteriores[campo]}' → '{datos_nuevos[campo]}'")
            else:
                cambios.append(f"{campo}: nuevo campo con valor '{datos_nuevos[campo]}'")
        
        return cambios
    
    def listar_backups_por_tipo(self, tipo: str) -> List[str]:
        """Listar todos los backups de un tipo específico"""
        tipo_dir = f"{self.backup_dir}/{tipo}"
        
        if os.path.exists(tipo_dir):
            return [f for f in os.listdir(tipo_dir) if f.endswith('.json')]
        
        return []
    
    def obtener_estadisticas_backups(self) -> Dict[str, Any]:
        """Obtener estadísticas generales de backups"""
        stats = {
            "fecha_consulta": self.generar_fecha_legible(),
            "directorio_backups": self.backup_dir,
            "tipos_backup": {}
        }
        
        subdirs = ["productos", "clientes", "ventas", "reportes", "configuracion", "sesiones"]
        
        for subdir in subdirs:
            path = f"{self.backup_dir}/{subdir}"
            if os.path.exists(path):
                archivos = os.listdir(path)
                stats["tipos_backup"][subdir] = {
                    "total_archivos": len(archivos),
                    "archivos_json": len([f for f in archivos if f.endswith('.json')]),
                    "archivos_csv": len([f for f in archivos if f.endswith('.csv')])
                }
        
        return stats