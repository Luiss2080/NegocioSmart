"""
Modelos de Datos Universales - VentaPro
=======================================

Modelos de base de datos adaptables a cualquier tipo de negocio.
Diseño flexible que se ajusta desde tiendas de abarrotes hasta talleres especializados.

Características Universales:
- ✅ Campos adaptables por industria
- ✅ Categorías personalizables  
- ✅ Múltiples unidades de medida
- ✅ Atributos dinámicos por producto
- ✅ Precios flexibles (unitario, por peso, por servicio)
- ✅ Control de stock avanzado
- ✅ Trazabilidad completa

Autor: Sistema VentaPro Universal
Fecha: 2025-01-04
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
import json

# Enums para tipos universales
class TipoNegocio(Enum):
    ABARROTES = "Tienda de Abarrotes"
    FERRETERIA = "Ferretería" 
    PAPELERIA = "Papelería"
    BOUTIQUE = "Boutique de Ropa"
    LIBRERIA = "Librería"
    FARMACIA = "Farmacia"
    RESTAURANTE = "Restaurante"
    TALLER = "Taller Mecánico"
    DISTRIBUIDORA = "Distribuidora"
    PANADERIA = "Panadería"
    VETERINARIA = "Veterinaria"
    ZAPATERIA = "Zapatería"
    PERFUMERIA = "Perfumería"
    ELECTRODOMESTICOS = "Electrodomésticos"
    JUGUETERIA = "Juguetería"
    GENERAL = "Tienda General"
    OTRO = "Otro"

class TipoProducto(Enum):
    FISICO = "Producto Físico"
    SERVICIO = "Servicio"
    DIGITAL = "Producto Digital"
    COMBO = "Combo/Paquete"
    CONSUMIBLE = "Consumible"
    PERECEDERO = "Perecedero"

class UnidadMedida(Enum):
    UNIDAD = "Unidad"
    KILOGRAMO = "Kilogramo"
    GRAMO = "Gramo"
    LITRO = "Litro"
    MILILITRO = "Mililitro"
    METRO = "Metro"
    CENTIMETRO = "Centímetro"
    CAJA = "Caja"
    PAQUETE = "Paquete"
    DOCENA = "Docena"
    HORA = "Hora"
    MINUTO = "Minuto"
    SERVICIO = "Servicio"
    LIBRA = "Libra"
    ONZA = "Onza"

class EstadoVenta(Enum):
    PENDIENTE = "Pendiente"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"
    DEVUELVE = "Devuelta"
    CREDITO = "A Crédito"

class MetodoPago(Enum):
    EFECTIVO = "Efectivo"
    TARJETA_CREDITO = "Tarjeta de Crédito"
    TARJETA_DEBITO = "Tarjeta de Débito"
    TRANSFERENCIA = "Transferencia"
    CHEQUE = "Cheque"
    CREDITO = "A Crédito"
    VALE = "Vale/Cupón"
    DIGITAL = "Pago Digital"

@dataclass
class ConfiguracionNegocio:
    """Configuración universal del negocio"""
    id: int = 0
    nombre: str = "Mi Negocio"
    tipo_negocio: TipoNegocio = TipoNegocio.GENERAL
    rfc_ruc: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    sitio_web: Optional[str] = None
    
    # Configuración monetaria
    moneda: str = "$"
    simbolo_moneda: str = "$"
    decimales: int = 2
    
    # Configuraciones del sistema
    usar_stock: bool = True
    usar_categorias: bool = True
    usar_proveedores: bool = True
    usar_clientes: bool = True
    usar_servicios: bool = False
    usar_codigo_barras: bool = True
    usar_fechas_vencimiento: bool = False
    usar_lotes: bool = False
    usar_ubicaciones: bool = False
    
    # Configuraciones de facturación
    serie_factura: str = "F"
    numero_inicial: int = 1
    incluir_iva: bool = True
    porcentaje_iva: float = 16.0
    
    # Configuraciones específicas por industria
    configuraciones_especiales: str = "{}"  # JSON con configs específicas
    
    fecha_creacion: datetime = datetime.now()
    fecha_modificacion: datetime = datetime.now()

@dataclass
class Categoria:
    """Categorías universales adaptables"""
    id: int = 0
    nombre: str = ""
    descripcion: Optional[str] = None
    categoria_padre_id: Optional[int] = None  # Para subcategorías
    icono: Optional[str] = None
    color: Optional[str] = None
    
    # Configuraciones específicas por categoría
    requiere_receta: bool = False  # Para farmacias
    es_perecedero: bool = False   # Para abarrotes
    tiempo_garantia_dias: Optional[int] = None  # Para electrónicos
    es_servicio: bool = False     # Para talleres/servicios
    
    activa: bool = True
    fecha_creacion: datetime = datetime.now()

@dataclass
class Proveedor:
    """Proveedores universales"""
    id: int = 0
    nombre: str = ""
    nombre_comercial: Optional[str] = None
    rfc_ruc: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    contacto_principal: Optional[str] = None
    
    # Condiciones comerciales
    dias_credito: int = 0
    descuento_por_volumen: float = 0.0
    moneda_preferida: str = "$"
    
    # Categorías que maneja
    especialidades: str = "[]"  # JSON array con categorías
    
    activo: bool = True
    fecha_creacion: datetime = datetime.now()
    fecha_ultima_compra: Optional[datetime] = None

@dataclass
class Producto:
    """Producto universal adaptable a cualquier negocio"""
    id: int = 0
    
    # Información básica
    nombre: str = ""
    descripcion: Optional[str] = None
    codigo_interno: Optional[str] = None
    codigo_barras: Optional[str] = None
    sku: Optional[str] = None
    
    # Clasificación
    categoria_id: Optional[int] = None
    tipo_producto: TipoProducto = TipoProducto.FISICO
    unidad_medida: UnidadMedida = UnidadMedida.UNIDAD
    
    # Precios (adaptable a diferentes modelos de negocio)
    precio_compra: float = 0.0
    precio_venta: float = 0.0
    precio_mayoreo: Optional[float] = None
    cantidad_mayoreo: Optional[int] = None
    precio_por_peso: Optional[float] = None  # Para productos por peso
    precio_por_tiempo: Optional[float] = None  # Para servicios por tiempo
    
    # Inventario
    stock_actual: int = 0
    stock_minimo: int = 0
    stock_maximo: Optional[int] = None
    ubicacion: Optional[str] = None  # Pasillo, estante, etc.
    
    # Información específica por industria
    # Farmacia/Médico
    principio_activo: Optional[str] = None
    requiere_receta: bool = False
    fecha_vencimiento: Optional[date] = None
    lote: Optional[str] = None
    
    # Ropa/Calzado
    talla: Optional[str] = None
    color: Optional[str] = None
    marca: Optional[str] = None
    temporada: Optional[str] = None
    material: Optional[str] = None
    
    # Libros
    isbn: Optional[str] = None
    autor: Optional[str] = None
    editorial: Optional[str] = None
    año_publicacion: Optional[int] = None
    
    # Electrónicos/Técnicos
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    garantia_meses: Optional[int] = None
    especificaciones_tecnicas: Optional[str] = None
    
    # Alimentos
    es_perecedero: bool = False
    calorias_por_100g: Optional[float] = None
    ingredientes: Optional[str] = None
    
    # Servicios
    duracion_estimada_minutos: Optional[int] = None
    requiere_cita: bool = False
    
    # Campos dinámicos adicionales (JSON)
    atributos_extra: str = "{}"  # JSON con campos específicos del negocio
    
    # Proveedor y compras
    proveedor_id: Optional[int] = None
    precio_ultima_compra: Optional[float] = None
    fecha_ultima_compra: Optional[datetime] = None
    
    # Estados
    activo: bool = True
    visible_en_pos: bool = True
    permite_descuento: bool = True
    
    # Imágenes y multimedia
    imagen_url: Optional[str] = None
    imagenes_adicionales: str = "[]"  # JSON array con URLs
    
    # Auditoría
    fecha_creacion: datetime = datetime.now()
    fecha_modificacion: datetime = datetime.now()
    creado_por: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para JSON"""
        data = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, (datetime, date)):
                data[field_name] = field_value.isoformat() if field_value else None
            elif isinstance(field_value, Enum):
                data[field_name] = field_value.value
            else:
                data[field_name] = field_value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Producto':
        """Crear producto desde diccionario"""
        # Convertir fechas
        for date_field in ['fecha_vencimiento', 'fecha_ultima_compra', 'fecha_creacion', 'fecha_modificacion']:
            if data.get(date_field):
                if date_field == 'fecha_vencimiento':
                    data[date_field] = datetime.fromisoformat(data[date_field]).date()
                else:
                    data[date_field] = datetime.fromisoformat(data[date_field])
        
        # Convertir enums
        if data.get('tipo_producto'):
            data['tipo_producto'] = TipoProducto(data['tipo_producto'])
        if data.get('unidad_medida'):
            data['unidad_medida'] = UnidadMedida(data['unidad_medida'])
        
        return cls(**data)

@dataclass
class Cliente:
    """Cliente universal"""
    id: int = 0
    
    # Información básica
    nombre: str = ""
    apellidos: Optional[str] = None
    nombre_comercial: Optional[str] = None  # Para empresas
    tipo_cliente: str = "Individual"  # Individual, Empresa, Mayorista
    
    # Contacto
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    
    # Información fiscal
    rfc_ruc: Optional[str] = None
    razon_social: Optional[str] = None
    
    # Información comercial
    limite_credito: float = 0.0
    dias_credito: int = 0
    descuento_autorizado: float = 0.0
    
    # Programa de lealtad
    puntos_acumulados: int = 0
    nivel_cliente: str = "Regular"  # Regular, VIP, Mayorista
    
    # Preferencias específicas por industria
    # Veterinaria - Información de mascotas
    mascotas: str = "[]"  # JSON array con info de mascotas
    
    # Restaurante - Preferencias alimentarias
    alergias: Optional[str] = None
    preferencias_dieta: Optional[str] = None
    
    # Salud - Información médica básica (con privacidad)
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    
    # Campos dinámicos
    informacion_extra: str = "{}"  # JSON con campos específicos
    
    # Estados
    activo: bool = True
    recibe_promociones: bool = True
    
    # Auditoría
    fecha_registro: datetime = datetime.now()
    fecha_ultima_compra: Optional[datetime] = None
    total_compras: float = 0.0
    numero_compras: int = 0

@dataclass
class Venta:
    """Venta universal adaptable"""
    id: int = 0
    numero_venta: str = ""
    
    # Información básica
    fecha_venta: datetime = datetime.now()
    cliente_id: Optional[int] = None
    vendedor: Optional[str] = None
    
    # Totales
    subtotal: float = 0.0
    impuesto: float = 0.0
    descuento: float = 0.0
    total: float = 0.0
    
    # Pago
    metodo_pago: MetodoPago = MetodoPago.EFECTIVO
    monto_pagado: float = 0.0
    cambio: float = 0.0
    
    # Estado
    estado: EstadoVenta = EstadoVenta.COMPLETADA
    
    # Información específica por industria
    # Restaurante
    mesa: Optional[str] = None
    mesero: Optional[str] = None
    tipo_servicio: Optional[str] = None  # Mesa, Llevar, Domicilio
    
    # Taller/Servicios
    orden_trabajo: Optional[str] = None
    vehiculo_info: Optional[str] = None  # JSON con info del vehículo
    fecha_entrega_estimada: Optional[datetime] = None
    
    # Farmacia
    receta_numero: Optional[str] = None
    medico: Optional[str] = None
    
    # Campos dinámicos
    informacion_extra: str = "{}"
    
    # Observaciones
    notas: Optional[str] = None
    
    # Auditoría
    fecha_creacion: datetime = datetime.now()
    
@dataclass
class DetalleVenta:
    """Detalle de venta universal"""
    id: int = 0
    venta_id: int = 0
    producto_id: int = 0
    
    # Información del producto al momento de la venta
    nombre_producto: str = ""
    codigo_producto: Optional[str] = None
    
    # Cantidad y precios
    cantidad: float = 0.0
    precio_unitario: float = 0.0
    descuento_linea: float = 0.0
    subtotal: float = 0.0
    
    # Información específica
    # Para productos por peso
    peso_real: Optional[float] = None
    
    # Para servicios
    tiempo_servicio_minutos: Optional[int] = None
    tecnico_asignado: Optional[str] = None
    
    # Para productos con lote/vencimiento
    lote_utilizado: Optional[str] = None
    fecha_vencimiento_producto: Optional[date] = None
    
    # Campos dinámicos
    detalles_extra: str = "{}"

@dataclass
class MovimientoInventario:
    """Movimientos de inventario universales"""
    id: int = 0
    producto_id: int = 0
    
    # Tipo de movimiento
    tipo_movimiento: str = ""  # ENTRADA, SALIDA, AJUSTE, MERMA, DEVOLUCION
    motivo: str = ""
    
    # Cantidades
    cantidad_anterior: int = 0
    cantidad_movimiento: int = 0
    cantidad_actual: int = 0
    
    # Información del movimiento
    referencia: Optional[str] = None  # Número de venta, compra, etc.
    costo_unitario: Optional[float] = None
    
    # Información específica por industria
    # Para perecederos
    lote_afectado: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    
    # Para ubicaciones físicas
    ubicacion_origen: Optional[str] = None
    ubicacion_destino: Optional[str] = None
    
    # Responsable
    usuario: Optional[str] = None
    observaciones: Optional[str] = None
    
    # Auditoría
    fecha_movimiento: datetime = datetime.now()

@dataclass
class ReporteVentas:
    """Estructura para reportes universales"""
    periodo: str = ""
    fecha_inicio: date = date.today()
    fecha_fin: date = date.today()
    
    # Métricas generales
    total_ventas: float = 0.0
    numero_transacciones: int = 0
    ticket_promedio: float = 0.0
    productos_vendidos: int = 0
    
    # Métricas por método de pago
    ventas_por_metodo: Dict[str, float] = None
    
    # Productos más vendidos
    top_productos: List[Dict[str, Any]] = None
    
    # Análisis por cliente
    clientes_nuevos: int = 0
    clientes_frecuentes: int = 0
    
    # Métricas específicas por industria
    metricas_industria: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.ventas_por_metodo is None:
            self.ventas_por_metodo = {}
        if self.top_productos is None:
            self.top_productos = []
        if self.metricas_industria is None:
            self.metricas_industria = {}

# Funciones de utilidad para adaptación por industria
def obtener_campos_por_industria(tipo_negocio: TipoNegocio) -> Dict[str, List[str]]:
    """Obtener campos específicos requeridos por tipo de negocio"""
    campos_industria = {
        TipoNegocio.FARMACIA: {
            "producto": ["principio_activo", "requiere_receta", "fecha_vencimiento", "lote"],
            "venta": ["receta_numero", "medico"],
            "cliente": ["fecha_nacimiento", "alergias"]
        },
        TipoNegocio.BOUTIQUE: {
            "producto": ["talla", "color", "marca", "temporada", "material"],
            "cliente": ["talla_preferida", "estilo_preferido"],
        },
        TipoNegocio.RESTAURANTE: {
            "producto": ["calorias_por_100g", "ingredientes", "duracion_estimada_minutos"],
            "venta": ["mesa", "mesero", "tipo_servicio"],
            "cliente": ["alergias", "preferencias_dieta"]
        },
        TipoNegocio.TALLER: {
            "producto": ["duracion_estimada_minutos", "requiere_cita", "garantia_meses"],
            "venta": ["orden_trabajo", "vehiculo_info", "fecha_entrega_estimada"],
            "cliente": ["vehiculos_info"]
        },
        TipoNegocio.LIBRERIA: {
            "producto": ["isbn", "autor", "editorial", "año_publicacion"],
        },
        TipoNegocio.VETERINARIA: {
            "producto": ["principio_activo", "especie_destino", "requiere_receta"],
            "cliente": ["mascotas"],
            "venta": ["mascota_tratada", "peso_mascota"]
        }
    }
    
    return campos_industria.get(tipo_negocio, {})

def validar_producto_por_industria(producto: Producto, tipo_negocio: TipoNegocio) -> List[str]:
    """Validar que un producto tenga los campos requeridos según la industria"""
    errores = []
    campos_requeridos = obtener_campos_por_industria(tipo_negocio).get("producto", [])
    
    for campo in campos_requeridos:
        if not getattr(producto, campo, None):
            errores.append(f"Campo {campo} es requerido para {tipo_negocio.value}")
    
    return errores

def configurar_negocio_por_industria(tipo_negocio: TipoNegocio) -> ConfiguracionNegocio:
    """Configurar automáticamente un negocio según su industria"""
    config = ConfiguracionNegocio(tipo_negocio=tipo_negocio)
    
    # Configuraciones específicas por industria
    if tipo_negocio == TipoNegocio.FARMACIA:
        config.usar_fechas_vencimiento = True
        config.usar_lotes = True
        config.usar_codigo_barras = True
        
    elif tipo_negocio == TipoNegocio.RESTAURANTE:
        config.usar_servicios = True
        config.usar_stock = True  # Para ingredientes
        
    elif tipo_negocio == TipoNegocio.TALLER:
        config.usar_servicios = True
        config.usar_stock = False  # Principalmente servicios
        
    elif tipo_negocio == TipoNegocio.BOUTIQUE:
        config.usar_ubicaciones = True  # Para organizar por tallas/colores
        
    elif tipo_negocio == TipoNegocio.ABARROTES:
        config.usar_fechas_vencimiento = True
        config.usar_codigo_barras = True
        config.usar_lotes = False
    
    return config