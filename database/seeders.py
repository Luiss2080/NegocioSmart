"""
Seeders - Datos de Prueba e Iniciales - VentaPro
================================================

Proporciona datos de prueba y configuración inicial para el sistema.
Útil para desarrollo, testing y demostración.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

import sqlite3
from decimal import Decimal
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from utils.logger import Logger

class Seeder:
    """Clase base para seeders"""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.logger = Logger()
    
    def ejecutar(self) -> bool:
        """Ejecuta el seeder (debe ser implementado por subclases)"""
        raise NotImplementedError("Debe implementar el método ejecutar()")

class SeederManager:
    """Gestor de seeders"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.connection = db_connection
        self.logger = Logger()
        self.seeders: List[Seeder] = []
        
        # Registrar todos los seeders
        self._registrar_seeders()
    
    def _registrar_seeders(self):
        """Registra todos los seeders disponibles"""
        self.seeders = [
            SeederConfiguracion(self.connection),
            SeederCategorias(self.connection),
            SeederProductos(self.connection),
            SeederClientes(self.connection),
            SeederUsuarios(self.connection)
        ]
    
    def ejecutar_todos(self, solo_configuracion: bool = False) -> bool:
        """Ejecuta todos los seeders"""
        try:
            self.logger.info("🌱 Iniciando carga de datos iniciales...")
            
            for seeder in self.seeders:
                # Si solo queremos configuración, ejecutar solo ese
                if solo_configuracion and not isinstance(seeder, SeederConfiguracion):
                    continue
                
                self.logger.info(f"🌱 Ejecutando {seeder.__class__.__name__}...")
                
                if seeder.ejecutar():
                    self.logger.info(f"✅ {seeder.__class__.__name__} completado")
                else:
                    self.logger.error(f"❌ Error en {seeder.__class__.__name__}")
                    return False
            
            self.connection.commit()
            self.logger.info("✅ Todos los seeders completados")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando seeders: {str(e)}")
            self.connection.rollback()
            return False
    
    def ejecutar_seeder(self, nombre_seeder: str) -> bool:
        """Ejecuta un seeder específico"""
        try:
            seeder = next((s for s in self.seeders if s.__class__.__name__ == nombre_seeder), None)
            if not seeder:
                self.logger.error(f"Seeder {nombre_seeder} no encontrado")
                return False
            
            self.logger.info(f"🌱 Ejecutando {nombre_seeder}...")
            
            if seeder.ejecutar():
                self.connection.commit()
                self.logger.info(f"✅ {nombre_seeder} completado")
                return True
            else:
                self.connection.rollback()
                self.logger.error(f"❌ Error en {nombre_seeder}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando {nombre_seeder}: {str(e)}")
            self.connection.rollback()
            return False

class SeederConfiguracion(Seeder):
    """Seeder para configuración inicial del sistema"""
    
    def ejecutar(self) -> bool:
        try:
            configuraciones = [
                # Configuración del negocio
                ('negocio_nombre', 'Mi Negocio Demo', 'Nombre del negocio', 'string'),
                ('negocio_direccion', 'Av. Principal 123, Centro, Ciudad', 'Dirección del negocio', 'string'),
                ('negocio_telefono', '+52 55 1234-5678', 'Teléfono del negocio', 'string'),
                ('negocio_email', 'ventas@minegocio.com', 'Email del negocio', 'string'),
                ('negocio_rfc', 'XAXX010101000', 'RFC del negocio', 'string'),
                
                # Configuración de facturación
                ('factura_prefijo', 'F-', 'Prefijo para folios de facturas', 'string'),
                ('factura_numero_siguiente', '1', 'Siguiente número de factura', 'int'),
                ('factura_iva', '16', 'Porcentaje de IVA', 'float'),
                ('factura_pie', 'Gracias por su compra', 'Pie de página en facturas', 'string'),
                
                # Configuración de inventario
                ('stock_alerta_habilitada', 'true', 'Habilitar alertas de stock bajo', 'bool'),
                ('stock_umbral_default', '5', 'Umbral por defecto para stock bajo', 'int'),
                ('descontar_stock_auto', 'true', 'Descontar stock automáticamente en ventas', 'bool'),
                
                # Configuración de sistema
                ('moneda_simbolo', '$', 'Símbolo de moneda', 'string'),
                ('moneda_codigo', 'MXN', 'Código de moneda', 'string'),
                ('backup_auto', 'true', 'Backup automático habilitado', 'bool'),
                ('backup_intervalo', '24', 'Intervalo de backup en horas', 'int')
            ]
            
            for clave, valor, descripcion, tipo in configuraciones:
                self.connection.execute("""
                    INSERT OR REPLACE INTO configuracion (clave, valor, descripcion, tipo)
                    VALUES (?, ?, ?, ?)
                """, (clave, valor, descripcion, tipo))
            
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error en SeederConfiguracion: {str(e)}")
            return False

class SeederCategorias(Seeder):
    """Seeder para categorías de productos"""
    
    def ejecutar(self) -> bool:
        try:
            categorias = [
                ('Abarrotes', 'Productos de consumo básico y alimentos', '#28a745', 'shopping-cart'),
                ('Bebidas', 'Refrescos, aguas, jugos y bebidas en general', '#17a2b8', 'glass-water'),
                ('Panadería', 'Pan, pasteles y productos de panadería', '#ffc107', 'bread-slice'),
                ('Lácteos', 'Leche, quesos, yogurt y derivados lácteos', '#6f42c1', 'cheese'),
                ('Carnes', 'Carnes rojas, blancas y embutidos', '#dc3545', 'drumstick-bite'),
                ('Frutas y Verduras', 'Productos frescos del campo', '#20c997', 'apple-alt'),
                ('Limpieza', 'Productos de limpieza y hogar', '#fd7e14', 'spray-can'),
                ('Cuidado Personal', 'Higiene personal y cuidado', '#e83e8c', 'user-check'),
                ('Dulces y Botanas', 'Golosinas, chocolates y snacks', '#6610f2', 'candy-cane'),
                ('Cigarros', 'Cigarrillos y productos de tabaco', '#6c757d', 'smoking')
            ]
            
            for nombre, descripcion, color, icono in categorias:
                self.connection.execute("""
                    INSERT OR IGNORE INTO categorias (nombre, descripcion, color, icono)
                    VALUES (?, ?, ?, ?)
                """, (nombre, descripcion, color, icono))
            
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error en SeederCategorias: {str(e)}")
            return False

class SeederProductos(Seeder):
    """Seeder para productos de ejemplo"""
    
    def ejecutar(self) -> bool:
        try:
            # Primero obtener las categorías creadas
            cursor = self.connection.execute("SELECT id, nombre FROM categorias")
            categorias = {nombre: id for id, nombre in cursor.fetchall()}
            
            productos = [
                # Abarrotes
                ('PROD001', 'Arroz San Rafael 1kg', 'Arroz blanco de primera calidad', categorias.get('Abarrotes', 1), 18.50, 25.00, 50, 10, 'kg'),
                ('PROD002', 'Frijol Negro 1kg', 'Frijol negro seleccionado', categorias.get('Abarrotes', 1), 22.00, 32.00, 30, 8, 'kg'),
                ('PROD003', 'Aceite Capullo 1L', 'Aceite vegetal comestible', categorias.get('Abarrotes', 1), 28.00, 42.00, 25, 5, 'lt'),
                
                # Bebidas
                ('PROD004', 'Coca Cola 600ml', 'Refresco de cola', categorias.get('Bebidas', 1), 8.50, 15.00, 100, 20, 'pza'),
                ('PROD005', 'Agua Bonafont 1.5L', 'Agua purificada natural', categorias.get('Bebidas', 1), 7.00, 12.00, 80, 15, 'pza'),
                ('PROD006', 'Jugo Del Valle Naranja 1L', 'Jugo de naranja natural', categorias.get('Bebidas', 1), 15.00, 22.00, 40, 10, 'pza'),
                
                # Panadería
                ('PROD007', 'Pan Blanco Bimbo', 'Pan de caja blanco grande', categorias.get('Panadería', 1), 18.00, 28.00, 20, 5, 'pza'),
                ('PROD008', 'Tortillas de Harina 1kg', 'Tortillas de harina de trigo', categorias.get('Panadería', 1), 12.00, 20.00, 15, 3, 'kg'),
                
                # Lácteos
                ('PROD009', 'Leche Lala 1L', 'Leche entera pasteurizada', categorias.get('Lácteos', 1), 16.50, 24.00, 35, 8, 'lt'),
                ('PROD010', 'Queso Oaxaca 500g', 'Queso oaxaca artesanal', categorias.get('Lácteos', 1), 45.00, 65.00, 12, 3, 'pza'),
                
                # Limpieza
                ('PROD011', 'Detergente Ariel 1kg', 'Detergente en polvo', categorias.get('Limpieza', 1), 32.00, 48.00, 25, 5, 'kg'),
                ('PROD012', 'Jabón Zote 200g', 'Jabón para lavar ropa', categorias.get('Limpieza', 1), 8.00, 14.00, 50, 10, 'pza'),
                
                # Cuidado Personal
                ('PROD013', 'Shampoo Head & Shoulders 400ml', 'Shampoo anticaspa', categorias.get('Cuidado Personal', 1), 45.00, 68.00, 15, 3, 'pza'),
                ('PROD014', 'Pasta Colgate 100ml', 'Pasta dental con flúor', categorias.get('Cuidado Personal', 1), 18.00, 28.00, 30, 8, 'pza'),
                
                # Dulces y Botanas
                ('PROD015', 'Sabritas Original 45g', 'Papas fritas sabor original', categorias.get('Dulces y Botanas', 1), 6.50, 12.00, 60, 15, 'pza'),
                ('PROD016', 'Chocolate Carlos V', 'Chocolate con leche', categorias.get('Dulces y Botanas', 1), 3.50, 6.00, 100, 25, 'pza')
            ]
            
            for codigo, nombre, descripcion, categoria_id, precio_compra, precio_venta, stock, stock_min, unidad in productos:
                self.connection.execute("""
                    INSERT OR IGNORE INTO productos 
                    (codigo, nombre, descripcion, categoria_id, precio_compra, precio_venta, 
                     stock_actual, stock_minimo, unidad_medida)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, descripcion, categoria_id, precio_compra, precio_venta, stock, stock_min, unidad))
            
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error en SeederProductos: {str(e)}")
            return False

class SeederClientes(Seeder):
    """Seeder para clientes de ejemplo"""
    
    def ejecutar(self) -> bool:
        try:
            clientes = [
                ('CLI001', 'María', 'González López', 'maria.gonzalez@email.com', '55-1234-5678', 'Calle 5 de Mayo #123', 'GOML850315'),
                ('CLI002', 'Juan Carlos', 'Pérez Martínez', 'juan.perez@email.com', '55-2345-6789', 'Av. Juárez #456', 'PEMJ780922'),
                ('CLI003', 'Ana Laura', 'Rodríguez Sánchez', 'ana.rodriguez@email.com', '55-3456-7890', 'Calle Morelos #789', 'ROSA920614'),
                ('CLI004', 'Roberto', 'Hernández García', 'roberto.hernandez@email.com', '55-4567-8901', 'Av. Revolución #101', 'HEGR751203'),
                ('CLI005', 'Patricia', 'López Fernández', 'patricia.lopez@email.com', '55-5678-9012', 'Calle Hidalgo #202', 'LOFP880425'),
                ('GENERAL', 'Cliente', 'General', '', '', '', ''),
                ('CLI006', 'Carlos Eduardo', 'Ramírez Torres', 'carlos.ramirez@email.com', '55-6789-0123', 'Av. Independencia #303', 'RATC830817'),
                ('CLI007', 'Lucía', 'Morales Jiménez', 'lucia.morales@email.com', '55-7890-1234', 'Calle Allende #404', 'MOJL901108'),
                ('CLI008', 'Fernando', 'Castillo Vargas', 'fernando.castillo@email.com', '55-8901-2345', 'Av. Constitución #505', 'CAVF770330'),
                ('CLI009', 'Isabel', 'Guerrero Mendoza', 'isabel.guerrero@email.com', '55-9012-3456', 'Calle Zaragoza #606', 'GUMI850712'),
                ('CLI010', 'Alejandro', 'Vásquez Ruiz', 'alejandro.vasquez@email.com', '55-0123-4567', 'Av. Reforma #707', 'VARA791024')
            ]
            
            for codigo, nombre, apellidos, email, telefono, direccion, rfc in clientes:
                self.connection.execute("""
                    INSERT OR IGNORE INTO clientes 
                    (codigo, nombre, apellidos, email, telefono, direccion, rfc)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, apellidos, email, telefono, direccion, rfc))
            
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error en SeederClientes: {str(e)}")
            return False

class SeederUsuarios(Seeder):
    """Seeder para usuarios del sistema"""
    
    def ejecutar(self) -> bool:
        try:
            # Nota: En producción, las contraseñas deberían estar hasheadas
            usuarios = [
                ('admin', 'admin123', 'Administrador del Sistema', 'admin@ventapro.com', 'admin'),
                ('vendedor1', 'vendedor123', 'Juan Vendedor', 'vendedor1@ventapro.com', 'vendedor'),
                ('supervisor1', 'supervisor123', 'María Supervisora', 'supervisor@ventapro.com', 'supervisor'),
                ('cajero1', 'cajero123', 'Pedro Cajero', 'cajero1@ventapro.com', 'vendedor')
            ]
            
            for usuario, password, nombre, email, rol in usuarios:
                self.connection.execute("""
                    INSERT OR IGNORE INTO usuarios 
                    (usuario, password_hash, nombre, email, rol)
                    VALUES (?, ?, ?, ?, ?)
                """, (usuario, password, nombre, email, rol))
            
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error en SeederUsuarios: {str(e)}")
            return False

class SeederVentasDemo(Seeder):
    """Seeder para generar ventas de demostración"""
    
    def ejecutar(self) -> bool:
        try:
            # Obtener productos y clientes disponibles
            cursor = self.connection.execute("SELECT id FROM productos WHERE activo = 1 LIMIT 10")
            productos = [row[0] for row in cursor.fetchall()]
            
            cursor = self.connection.execute("SELECT id FROM clientes WHERE activo = 1 LIMIT 5")
            clientes = [row[0] for row in cursor.fetchall()]
            
            if not productos or not clientes:
                self.logger.warning("No hay productos o clientes para generar ventas demo")
                return True
            
            # Generar 20 ventas de los últimos 30 días
            for i in range(1, 21):
                fecha_venta = datetime.now() - timedelta(days=random.randint(0, 30))
                folio = f"F-{str(i).zfill(6)}"
                cliente_id = random.choice(clientes)
                
                # Insertar venta
                cursor = self.connection.execute("""
                    INSERT INTO ventas (folio, cliente_id, fecha_venta, metodo_pago, estado)
                    VALUES (?, ?, ?, ?, 'completada')
                """, (folio, cliente_id, fecha_venta, random.choice(['efectivo', 'tarjeta', 'transferencia'])))
                
                venta_id = cursor.lastrowid
                
                # Agregar productos a la venta
                num_productos = random.randint(1, 5)
                subtotal = 0
                
                for _ in range(num_productos):
                    producto_id = random.choice(productos)
                    cantidad = random.randint(1, 3)
                    
                    # Obtener precio del producto
                    cursor = self.connection.execute(
                        "SELECT precio_venta FROM productos WHERE id = ?", 
                        (producto_id,)
                    )
                    precio = cursor.fetchone()[0]
                    subtotal_linea = precio * cantidad
                    subtotal += subtotal_linea
                    
                    # Insertar detalle
                    self.connection.execute("""
                        INSERT INTO detalle_ventas 
                        (venta_id, producto_id, cantidad, precio_unitario, subtotal_linea)
                        VALUES (?, ?, ?, ?, ?)
                    """, (venta_id, producto_id, cantidad, precio, subtotal_linea))
                
                # Actualizar totales de la venta
                impuestos = subtotal * 0.16
                total = subtotal + impuestos
                
                self.connection.execute("""
                    UPDATE ventas 
                    SET subtotal = ?, impuestos = ?, total = ?
                    WHERE id = ?
                """, (subtotal, impuestos, total, venta_id))
            
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error en SeederVentasDemo: {str(e)}")
            return False