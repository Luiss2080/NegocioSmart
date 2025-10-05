"""
Constantes del Sistema - VentaPro
================================

Define todas las constantes utilizadas en el sistema.
Centraliza valores como códigos de estado, mensajes, configuraciones por defecto, etc.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

# Información de la aplicación
APP_NAME = "VentaPro"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Sistema de Gestión de Ventas e Inventario"
APP_AUTHOR = "VentaPro Team"
APP_WEBSITE = "https://ventapro.com"

# Configuración de base de datos
DEFAULT_DB_PATH = "data/erp.db"
BACKUP_PATH = "data/backups/"
DB_TIMEOUT = 30.0

# Configuración de archivos
LOG_PATH = "logs/"
REPORTS_PATH = "reports/"
ASSETS_PATH = "assets/"
TEMPLATES_PATH = "templates/"

# Estados de venta
class EstadoVenta:
    BORRADOR = "borrador"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    DEVUELTA = "devuelta"
    PENDIENTE = "pendiente"

# Métodos de pago
class MetodoPago:
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    CHEQUE = "cheque"
    CREDITO = "credito"
    OTROS = "otros"

# Roles de usuario
class RolUsuario:
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    VENDEDOR = "vendedor"
    CONSULTA = "consulta"

# Unidades de medida
class UnidadMedida:
    PIEZA = "pza"
    KILOGRAMO = "kg"
    GRAMO = "gr"
    LITRO = "lt"
    MILILITRO = "ml"
    METRO = "mts"
    CENTIMETRO = "cms"
    CAJA = "caja"
    PAQUETE = "paq"
    DOCENA = "dza"
    PAR = "par"

# Categorías por defecto
CATEGORIAS_DEFAULT = [
    "General",
    "Abarrotes", 
    "Bebidas",
    "Panadería",
    "Lácteos",
    "Carnes",
    "Frutas y Verduras",
    "Limpieza",
    "Cuidado Personal",
    "Dulces y Botanas"
]

# Configuración de facturación
FACTURA_PREFIJO_DEFAULT = "F-"
IVA_DEFAULT = 0.16
MONEDA_DEFAULT = "MXN"
MONEDA_SIMBOLO_DEFAULT = "$"

# Configuración de inventario
STOCK_MINIMO_DEFAULT = 5
ALERTA_STOCK_BAJO = True

# Configuración de interfaz
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 800

# Colores del tema
class Colores:
    PRIMARIO = "#1f538d"
    SECUNDARIO = "#28a745"
    EXITO = "#28a745"
    PELIGRO = "#dc3545"
    ADVERTENCIA = "#ffc107"
    INFO = "#17a2b8"
    GRIS = "#6c757d"
    GRIS_CLARO = "#f8f9fa"

# Configuración de logging
class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

LOG_FORMAT = "%(asctime)s | %(levelname)8s | %(module)15s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Configuración de reportes
FECHA_FORMATO_REPORTE = "%d/%m/%Y"
FECHA_FORMATO_ARCHIVO = "%Y%m%d_%H%M%S"

# Configuración de backup
BACKUP_INTERVALO_DEFAULT = 24  # horas
MAX_BACKUPS_DEFAULT = 30
BACKUP_COMPRESION = True

# Mensajes del sistema
class Mensajes:
    # Éxito
    PRODUCTO_GUARDADO = "✅ Producto guardado correctamente"
    VENTA_COMPLETADA = "✅ Venta realizada con éxito"
    CLIENTE_GUARDADO = "✅ Cliente guardado correctamente"
    BACKUP_CREADO = "✅ Respaldo creado exitosamente"
    
    # Errores
    ERROR_BD_CONEXION = "❌ Error de conexión con la base de datos"
    ERROR_PRODUCTO_NO_ENCONTRADO = "❌ Producto no encontrado"
    ERROR_STOCK_INSUFICIENTE = "❌ Stock insuficiente para la venta"
    ERROR_DATOS_INVALIDOS = "❌ Los datos ingresados no son válidos"
    ERROR_BACKUP_FALLO = "❌ Error al crear el respaldo"
    
    # Advertencias
    ADVERTENCIA_STOCK_BAJO = "⚠️ Stock bajo detectado"
    ADVERTENCIA_PRODUCTO_DUPLICADO = "⚠️ Ya existe un producto con este código"
    ADVERTENCIA_CLIENTE_DUPLICADO = "⚠️ Ya existe un cliente con este RFC/Email"
    
    # Información
    INFO_CARGANDO = "ℹ️ Cargando datos..."
    INFO_GUARDANDO = "ℹ️ Guardando información..."
    INFO_PROCESANDO = "ℹ️ Procesando solicitud..."

# Validaciones
class Validacion:
    # Longitudes mínimas y máximas
    CODIGO_MIN_LENGTH = 3
    CODIGO_MAX_LENGTH = 50
    NOMBRE_MIN_LENGTH = 2
    NOMBRE_MAX_LENGTH = 200
    DESCRIPCION_MAX_LENGTH = 500
    
    # Patrones de validación
    PATRON_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PATRON_TELEFONO = r'^[+]?[0-9\s\-()]{10,15}$'
    PATRON_RFC = r'^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$'
    PATRON_CODIGO_BARRAS = r'^[0-9]{8,14}$'

# Configuración de la ventana principal
class VentanaConfig:
    TITULO = "VentaPro - Sistema de Gestión de Ventas e Inventario"
    ICONO = "assets/images/icon.ico"
    MENU_WIDTH = 250
    TOOLBAR_HEIGHT = 80
    STATUSBAR_HEIGHT = 30

# Configuración de exportación
class Exportacion:
    EXCEL_EXTENSION = ".xlsx"
    PDF_EXTENSION = ".pdf"
    CSV_EXTENSION = ".csv"
    
    # Formatos de fecha para exportación
    FECHA_EXCEL = "DD/MM/YYYY"
    FECHA_PDF = "DD de MMMM de YYYY"

# URLs y endpoints (para futuras integraciones)
class URLs:
    SAT_CONSULTA_RFC = "https://agsc.siat.sat.gob.mx/"
    BANXICO_TIPO_CAMBIO = "https://www.banxico.org.mx/SieAPIRest/"

# Códigos de país y moneda
CODIGO_PAIS = "MX"
ZONA_HORARIA = "America/Mexico_City"

# Límites del sistema
MAX_PRODUCTOS = 100000
MAX_CLIENTES = 50000
MAX_VENTAS_POR_DIA = 10000

# Configuración de impresión
class Impresion:
    PAPEL_A4 = "A4"
    PAPEL_CARTA = "Letter"
    PAPEL_TICKET = "80mm"
    
    ORIENTACION_VERTICAL = "portrait"
    ORIENTACION_HORIZONTAL = "landscape"

# Tipos de archivo soportados
TIPOS_IMAGEN = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
TIPOS_DOCUMENTO = [".pdf", ".docx", ".txt"]
TIPOS_EXCEL = [".xlsx", ".xls", ".csv"]