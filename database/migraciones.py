"""
Migraciones de Base de Datos - VentaPro
=======================================

Maneja las migraciones y actualizaciones de esquema de base de datos.
Permite evolucionar la estructura sin perder datos.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

from typing import List, Dict, Any
from datetime import datetime
import sqlite3
from utils.logger import Logger

class Migration:
    """Clase base para una migración"""
    
    def __init__(self, version: str, descripcion: str):
        self.version = version
        self.descripcion = descripcion
        self.fecha_creacion = datetime.now()
    
    def up(self, connection: sqlite3.Connection) -> bool:
        """Ejecuta la migración (debe ser implementado por subclases)"""
        raise NotImplementedError("Debe implementar el método up()")
    
    def down(self, connection: sqlite3.Connection) -> bool:
        """Revierte la migración (debe ser implementado por subclases)"""
        raise NotImplementedError("Debe implementar el método down()")

class MigrationManager:
    """Gestor de migraciones de base de datos"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.connection = db_connection
        self.logger = Logger()
        self.migraciones: List[Migration] = []
        
        # Crear tabla de migraciones si no existe
        self._crear_tabla_migraciones()
        
        # Registrar todas las migraciones
        self._registrar_migraciones()
    
    def _crear_tabla_migraciones(self):
        """Crea la tabla para trackear migraciones ejecutadas"""
        sql = """
        CREATE TABLE IF NOT EXISTS migraciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version VARCHAR(50) UNIQUE NOT NULL,
            descripcion TEXT,
            fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            exitosa BOOLEAN DEFAULT 1
        )
        """
        self.connection.execute(sql)
        self.connection.commit()
    
    def _registrar_migraciones(self):
        """Registra todas las migraciones disponibles"""
        self.migraciones = [
            MigracionInicial("1.0.0", "Estructura inicial de base de datos"),
            MigracionIndicesOptimizacion("1.0.1", "Índices para optimización de consultas"),
            MigracionCamposAdicionales("1.0.2", "Campos adicionales en productos y clientes"),
            MigracionTablaCategorias("1.0.3", "Mejoras en tabla de categorías"),
            MigracionSistemaBackup("1.0.4", "Sistema de backup y auditoria")
        ]
    
    def ejecutar_migraciones_pendientes(self) -> bool:
        """Ejecuta todas las migraciones pendientes"""
        try:
            migraciones_ejecutadas = self._obtener_migraciones_ejecutadas()
            
            for migracion in self.migraciones:
                if migracion.version not in migraciones_ejecutadas:
                    self.logger.info(f"🔧 Ejecutando migración {migracion.version}: {migracion.descripcion}")
                    
                    if self._ejecutar_migracion(migracion):
                        self.logger.info(f"✅ Migración {migracion.version} completada")
                    else:
                        self.logger.error(f"❌ Error en migración {migracion.version}")
                        return False
            
            self.logger.info("✅ Todas las migraciones completadas")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando migraciones: {str(e)}")
            return False
    
    def _obtener_migraciones_ejecutadas(self) -> List[str]:
        """Obtiene lista de migraciones ya ejecutadas"""
        try:
            cursor = self.connection.execute(
                "SELECT version FROM migraciones WHERE exitosa = 1 ORDER BY fecha_ejecucion"
            )
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def _ejecutar_migracion(self, migracion: Migration) -> bool:
        """Ejecuta una migración específica"""
        try:
            # Comenzar transacción
            self.connection.execute("BEGIN")
            
            # Ejecutar migración
            if migracion.up(self.connection):
                # Registrar migración exitosa
                self.connection.execute("""
                    INSERT INTO migraciones (version, descripcion, exitosa)
                    VALUES (?, ?, 1)
                """, (migracion.version, migracion.descripcion))
                
                # Confirmar transacción
                self.connection.commit()
                return True
            else:
                # Revertir en caso de error
                self.connection.rollback()
                return False
                
        except Exception as e:
            # Revertir en caso de error
            self.connection.rollback()
            self.logger.error(f"Error en migración {migracion.version}: {str(e)}")
            return False
    
    def revertir_migracion(self, version: str) -> bool:
        """Revierte una migración específica"""
        try:
            migracion = next((m for m in self.migraciones if m.version == version), None)
            if not migracion:
                self.logger.error(f"Migración {version} no encontrada")
                return False
            
            self.logger.info(f"🔄 Revirtiendo migración {version}")
            
            # Comenzar transacción
            self.connection.execute("BEGIN")
            
            # Revertir migración
            if migracion.down(self.connection):
                # Marcar como revertida
                self.connection.execute(
                    "UPDATE migraciones SET exitosa = 0 WHERE version = ?",
                    (version,)
                )
                
                # Confirmar transacción
                self.connection.commit()
                self.logger.info(f"✅ Migración {version} revertida")
                return True
            else:
                # Revertir en caso de error
                self.connection.rollback()
                return False
                
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Error revirtiendo migración {version}: {str(e)}")
            return False

# Migraciones específicas

class MigracionInicial(Migration):
    """Migración inicial - estructura básica"""
    
    def up(self, connection: sqlite3.Connection) -> bool:
        """Esta migración no hace nada porque las tablas se crean en db_manager"""
        return True
    
    def down(self, connection: sqlite3.Connection) -> bool:
        """Elimina todas las tablas"""
        try:
            tablas = [
                'detalle_ventas', 'ventas', 'productos', 'categorias', 
                'clientes', 'usuarios', 'configuracion', 'logs'
            ]
            
            for tabla in tablas:
                connection.execute(f"DROP TABLE IF EXISTS {tabla}")
            
            return True
        except sqlite3.Error:
            return False

class MigracionIndicesOptimizacion(Migration):
    """Agrega índices para optimización"""
    
    def up(self, connection: sqlite3.Connection) -> bool:
        try:
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_productos_stock_bajo ON productos (stock_actual, stock_minimo)",
                "CREATE INDEX IF NOT EXISTS idx_ventas_estado ON ventas (estado)",
                "CREATE INDEX IF NOT EXISTS idx_ventas_metodo_pago ON ventas (metodo_pago)",
                "CREATE INDEX IF NOT EXISTS idx_detalle_producto_id ON detalle_ventas (producto_id)",
                "CREATE INDEX IF NOT EXISTS idx_clientes_activo ON clientes (activo)"
            ]
            
            for indice in indices:
                connection.execute(indice)
            
            return True
        except sqlite3.Error:
            return False
    
    def down(self, connection: sqlite3.Connection) -> bool:
        try:
            indices = [
                "DROP INDEX IF EXISTS idx_productos_stock_bajo",
                "DROP INDEX IF EXISTS idx_ventas_estado", 
                "DROP INDEX IF EXISTS idx_ventas_metodo_pago",
                "DROP INDEX IF EXISTS idx_detalle_producto_id",
                "DROP INDEX IF EXISTS idx_clientes_activo"
            ]
            
            for indice in indices:
                connection.execute(indice)
            
            return True
        except sqlite3.Error:
            return False

class MigracionCamposAdicionales(Migration):
    """Agrega campos adicionales a tablas existentes"""
    
    def up(self, connection: sqlite3.Connection) -> bool:
        try:
            # Agregar campos a productos si no existen
            try:
                connection.execute("ALTER TABLE productos ADD COLUMN codigo_barras VARCHAR(50)")
            except sqlite3.Error:
                pass  # Campo ya existe
            
            try:
                connection.execute("ALTER TABLE productos ADD COLUMN peso DECIMAL(8,3)")
            except sqlite3.Error:
                pass
            
            # Agregar campos a clientes si no existen
            try:
                connection.execute("ALTER TABLE clientes ADD COLUMN fecha_nacimiento DATE")
            except sqlite3.Error:
                pass
            
            try:
                connection.execute("ALTER TABLE clientes ADD COLUMN limite_credito DECIMAL(10,2) DEFAULT 0.00")
            except sqlite3.Error:
                pass
            
            return True
        except sqlite3.Error:
            return False
    
    def down(self, connection: sqlite3.Connection) -> bool:
        # SQLite no soporta DROP COLUMN directamente
        # Se requeriría recrear la tabla, lo cual es complejo
        # Por ahora, solo marcamos como revertida
        return True

class MigracionTablaCategorias(Migration):
    """Mejoras en la tabla de categorías"""
    
    def up(self, connection: sqlite3.Connection) -> bool:
        try:
            # Agregar campos adicionales a categorías
            try:
                connection.execute("ALTER TABLE categorias ADD COLUMN color VARCHAR(7) DEFAULT '#007bff'")
            except sqlite3.Error:
                pass
            
            try:
                connection.execute("ALTER TABLE categorias ADD COLUMN icono VARCHAR(50) DEFAULT 'categoria'")
            except sqlite3.Error:
                pass
            
            return True
        except sqlite3.Error:
            return False
    
    def down(self, connection: sqlite3.Connection) -> bool:
        return True

class MigracionSistemaBackup(Migration):
    """Sistema de backup y auditoria"""
    
    def up(self, connection: sqlite3.Connection) -> bool:
        try:
            # Crear tabla de auditoría
            sql_auditoria = """
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tabla VARCHAR(50) NOT NULL,
                accion VARCHAR(20) NOT NULL,
                registro_id INTEGER,
                valores_anteriores TEXT,
                valores_nuevos TEXT,
                usuario_id INTEGER,
                fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
            connection.execute(sql_auditoria)
            
            # Crear tabla de configuración de backup
            sql_backup = """
            CREATE TABLE IF NOT EXISTS backup_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                ruta_destino TEXT NOT NULL,
                frecuencia INTEGER DEFAULT 24,
                activo BOOLEAN DEFAULT 1,
                ultimo_backup TIMESTAMP,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            connection.execute(sql_backup)
            
            return True
        except sqlite3.Error:
            return False
    
    def down(self, connection: sqlite3.Connection) -> bool:
        try:
            connection.execute("DROP TABLE IF EXISTS auditoria")
            connection.execute("DROP TABLE IF EXISTS backup_config")
            return True
        except sqlite3.Error:
            return False