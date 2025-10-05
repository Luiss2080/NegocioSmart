"""
Gestor Principal de Base de Datos - VentaPro
===========================================

Maneja todas las operaciones de base de datos SQLite para el sistema VentaPro.
Incluye creación de tablas, conexiones, transacciones y mantenimiento.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from utils.logger import Logger
from utils.config_manager import ConfigManager

class DatabaseManager:
    """Gestor principal de la base de datos SQLite"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = Logger()
        self.db_path = self.config.get('DATABASE', 'db_path', 'data/erp.db')
        self.connection: Optional[sqlite3.Connection] = None
        
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def conectar(self) -> bool:
        """Establece conexión con la base de datos"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
            
            # Habilitar foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Configurar WAL mode para mejor concurrencia
            self.connection.execute("PRAGMA journal_mode = WAL")
            
            self.logger.info("✅ Conexión establecida con la base de datos")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"❌ Error al conectar con la base de datos: {str(e)}")
            return False
    
    def desconectar(self):
        """Cierra la conexión con la base de datos"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("🔌 Conexión cerrada con la base de datos")
    
    def inicializar_db(self) -> bool:
        """Inicializa la base de datos creando todas las tablas necesarias"""
        if not self.conectar():
            return False
        
        try:
            self.logger.info("🔧 Inicializando estructura de base de datos...")
            
            # Crear todas las tablas
            self._crear_tabla_categorias()
            self._crear_tabla_productos()
            self._crear_tabla_clientes()
            self._crear_tabla_ventas()
            self._crear_tabla_detalle_ventas()
            self._crear_tabla_usuarios()
            self._crear_tabla_configuracion()
            self._crear_tabla_logs()
            
            # Crear índices para optimizar consultas
            self._crear_indices()
            
            # Insertar datos iniciales
            self._insertar_datos_iniciales()
            
            self.connection.commit()
            self.logger.info("✅ Base de datos inicializada correctamente")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"❌ Error al inicializar la base de datos: {str(e)}")
            self.connection.rollback()
            return False
    
    def _crear_tabla_categorias(self):
        """Crea la tabla de categorías de productos"""
        sql = """
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            descripcion TEXT,
            activa BOOLEAN DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.connection.execute(sql)
    
    def _crear_tabla_productos(self):
        """Crea la tabla de productos"""
        sql = """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo VARCHAR(50) UNIQUE NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            descripcion TEXT,
            categoria_id INTEGER,
            precio_compra DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            precio_venta DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            stock_actual INTEGER NOT NULL DEFAULT 0,
            stock_minimo INTEGER NOT NULL DEFAULT 0,
            unidad_medida VARCHAR(20) DEFAULT 'pza',
            imagen VARCHAR(255),
            activo BOOLEAN DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
        """
        self.connection.execute(sql)
    
    def _crear_tabla_clientes(self):
        """Crea la tabla de clientes"""
        sql = """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo VARCHAR(50) UNIQUE,
            nombre VARCHAR(200) NOT NULL,
            apellidos VARCHAR(200),
            email VARCHAR(100),
            telefono VARCHAR(20),
            direccion TEXT,
            rfc VARCHAR(20),
            activo BOOLEAN DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.connection.execute(sql)
    
    def _crear_tabla_ventas(self):
        """Crea la tabla de ventas (cabecera)"""
        sql = """
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio VARCHAR(50) UNIQUE NOT NULL,
            cliente_id INTEGER,
            subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            descuento DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            impuestos DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            metodo_pago VARCHAR(50) NOT NULL DEFAULT 'efectivo',
            estado VARCHAR(20) DEFAULT 'completada',
            fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
        """
        self.connection.execute(sql)
    
    def _crear_tabla_detalle_ventas(self):
        """Crea la tabla de detalle de ventas"""
        sql = """
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            descuento_linea DECIMAL(10,2) DEFAULT 0.00,
            subtotal_linea DECIMAL(10,2) NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (venta_id) REFERENCES ventas (id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
        """
        self.connection.execute(sql)
    
    def _crear_tabla_usuarios(self):
        """Crea la tabla de usuarios del sistema"""
        sql = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            email VARCHAR(100),
            rol VARCHAR(20) DEFAULT 'vendedor',
            activo BOOLEAN DEFAULT 1,
            ultimo_acceso TIMESTAMP,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.connection.execute(sql)
    
    def _crear_tabla_configuracion(self):
        """Crea la tabla de configuración del sistema"""
        sql = """
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clave VARCHAR(100) UNIQUE NOT NULL,
            valor TEXT,
            descripcion TEXT,
            tipo VARCHAR(20) DEFAULT 'string',
            fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.connection.execute(sql)
    
    def _crear_tabla_logs(self):
        """Crea la tabla de logs del sistema"""
        sql = """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nivel VARCHAR(10) NOT NULL,
            modulo VARCHAR(50),
            mensaje TEXT NOT NULL,
            usuario_id INTEGER,
            ip_address VARCHAR(45),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
        """
        self.connection.execute(sql)
    
    def _crear_indices(self):
        """Crea índices para optimizar las consultas"""
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos (codigo)",
            "CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos (nombre)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_folio ON ventas (folio)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas (fecha_venta)",
            "CREATE INDEX IF NOT EXISTS idx_detalle_venta_id ON detalle_ventas (venta_id)",
            "CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes (nombre)",
            "CREATE INDEX IF NOT EXISTS idx_logs_fecha ON logs (fecha_creacion)"
        ]
        
        for indice in indices:
            self.connection.execute(indice)
    
    def _insertar_datos_iniciales(self):
        """Inserta datos iniciales necesarios"""
        # Categoría por defecto
        self.connection.execute("""
            INSERT OR IGNORE INTO categorias (nombre, descripcion)
            VALUES ('General', 'Categoría general para productos sin clasificar')
        """)
        
        # Cliente genérico
        self.connection.execute("""
            INSERT OR IGNORE INTO clientes (codigo, nombre)
            VALUES ('GENERAL', 'Cliente General')
        """)
        
        # Usuario administrador por defecto (si no existe)
        self.connection.execute("""
            INSERT OR IGNORE INTO usuarios (usuario, password_hash, nombre, rol)
            VALUES ('admin', 'admin123', 'Administrador', 'admin')
        """)
    
    def ejecutar_consulta(self, sql: str, parametros: tuple = ()) -> Optional[List[sqlite3.Row]]:
        """Ejecuta una consulta SELECT y retorna los resultados"""
        try:
            cursor = self.connection.execute(sql, parametros)
            return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Error en consulta: {str(e)}")
            return None
    
    def ejecutar_comando(self, sql: str, parametros: tuple = ()) -> bool:
        """Ejecuta un comando INSERT, UPDATE o DELETE"""
        try:
            self.connection.execute(sql, parametros)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error en comando: {str(e)}")
            self.connection.rollback()
            return False
    
    def crear_backup(self) -> bool:
        """Crea un respaldo de la base de datos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backups/erp_backup_{timestamp}.db"
            
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Crear backup
            shutil.copy2(self.db_path, backup_path)
            
            self.logger.info(f"✅ Backup creado: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error al crear backup: {str(e)}")
            return False
    
    def __enter__(self):
        """Context manager: entrada"""
        self.conectar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: salida"""
        self.desconectar()