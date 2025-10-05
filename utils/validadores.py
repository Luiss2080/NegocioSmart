"""
Validadores - VentaPro
======================

Funciones de validación para datos del sistema.
Valida emails, teléfonos, códigos, precios, etc.

Autor: Sistema VentaPro
Fecha: 2025-10-04
"""

import re
from typing import Optional, Union, List, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime
from utils.constantes import Validacion

class Validador:
    """Clase principal para validaciones del sistema"""
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """
        Valida formato de email
        
        Args:
            email: Email a validar
            
        Returns:
            Tuple con (es_valido, mensaje)
        """
        if not email or not email.strip():
            return False, "El email es requerido"
        
        email = email.strip()
        
        if len(email) > 100:
            return False, "El email es demasiado largo (máximo 100 caracteres)"
        
        if not re.match(Validacion.PATRON_EMAIL, email):
            return False, "Formato de email inválido"
        
        return True, "Email válido"
    
    @staticmethod
    def validar_telefono(telefono: str) -> Tuple[bool, str]:
        """
        Valida formato de teléfono
        
        Args:
            telefono: Teléfono a validar
            
        Returns:
            Tuple con (es_valido, mensaje)
        """
        if not telefono or not telefono.strip():
            return True, "Teléfono opcional"  # El teléfono es opcional
        
        telefono = telefono.strip()
        
        if len(telefono) < 10:
            return False, "El teléfono debe tener al menos 10 dígitos"
        
        if len(telefono) > 15:
            return False, "El teléfono es demasiado largo (máximo 15 caracteres)"
        
        if not re.match(Validacion.PATRON_TELEFONO, telefono):
            return False, "Formato de teléfono inválido"
        
        return True, "Teléfono válido"
    
    @staticmethod
    def validar_rfc(rfc: str) -> Tuple[bool, str]:
        """
        Valida formato de RFC mexicano
        
        Args:
            rfc: RFC a validar
            
        Returns:
            Tuple con (es_valido, mensaje)
        """
        if not rfc or not rfc.strip():
            return True, "RFC opcional"  # El RFC es opcional
        
        rfc = rfc.strip().upper()
        
        if len(rfc) not in [12, 13]:
            return False, "El RFC debe tener 12 o 13 caracteres"
        
        if not re.match(Validacion.PATRON_RFC, rfc):
            return False, "Formato de RFC inválido"
        
        return True, "RFC válido"
    
    @staticmethod
    def validar_codigo_producto(codigo: str) -> Tuple[bool, str]:
        """
        Valida código de producto
        
        Args:
            codigo: Código a validar
            
        Returns:
            Tuple con (es_valido, mensaje)
        """
        if not codigo or not codigo.strip():
            return False, "El código es requerido"
        
        codigo = codigo.strip()
        
        if len(codigo) < Validacion.CODIGO_MIN_LENGTH:
            return False, f"El código debe tener al menos {Validacion.CODIGO_MIN_LENGTH} caracteres"
        
        if len(codigo) > Validacion.CODIGO_MAX_LENGTH:
            return False, f"El código es demasiado largo (máximo {Validacion.CODIGO_MAX_LENGTH} caracteres)"
        
        # Solo permitir letras, números, guiones y guiones bajos
        if not re.match(r'^[A-Za-z0-9\-_]+$', codigo):
            return False, "El código solo puede contener letras, números, guiones y guiones bajos"
        
        return True, "Código válido"
    
    @staticmethod
    def validar_nombre(nombre: str, campo: str = "nombre") -> Tuple[bool, str]:
        """
        Valida nombres (productos, clientes, etc.)
        
        Args:
            nombre: Nombre a validar
            campo: Nombre del campo para el mensaje de error
            
        Returns:
            Tuple con (es_valido, mensaje)
        """
        if not nombre or not nombre.strip():
            return False, f"El {campo} es requerido"
        
        nombre = nombre.strip()
        
        if len(nombre) < Validacion.NOMBRE_MIN_LENGTH:
            return False, f"El {campo} debe tener al menos {Validacion.NOMBRE_MIN_LENGTH} caracteres"
        
        if len(nombre) > Validacion.NOMBRE_MAX_LENGTH:
            return False, f"El {campo} es demasiado largo (máximo {Validacion.NOMBRE_MAX_LENGTH} caracteres)"
        
        return True, f"{campo.capitalize()} válido"
    
    @staticmethod
    def validar_precio(precio: Union[str, float, Decimal]) -> Tuple[bool, str, Optional[Decimal]]:
        """
        Valida precio monetario
        
        Args:
            precio: Precio a validar
            
        Returns:
            Tuple con (es_valido, mensaje, precio_decimal)
        """
        if precio is None:
            return False, "El precio es requerido", None
        
        try:
            if isinstance(precio, str):
                precio = precio.strip().replace(',', '')
            
            precio_decimal = Decimal(str(precio))
            
            if precio_decimal < 0:
                return False, "El precio no puede ser negativo", None
            
            if precio_decimal > Decimal('999999.99'):
                return False, "El precio es demasiado alto", None
            
            # Verificar que no tenga más de 2 decimales
            exponent = precio_decimal.as_tuple().exponent
            if isinstance(exponent, int) and exponent < -2:
                return False, "El precio no puede tener más de 2 decimales", None
            
            return True, "Precio válido", precio_decimal
            
        except (InvalidOperation, ValueError):
            return False, "Formato de precio inválido", None
    
    @staticmethod
    def validar_cantidad(cantidad: Union[str, int]) -> Tuple[bool, str, Optional[int]]:
        """
        Valida cantidad entera
        
        Args:
            cantidad: Cantidad a validar
            
        Returns:
            Tuple con (es_valido, mensaje, cantidad_int)
        """
        if cantidad is None:
            return False, "La cantidad es requerida", None
        
        try:
            if isinstance(cantidad, str):
                cantidad = cantidad.strip()
            
            cantidad_int = int(cantidad)
            
            if cantidad_int < 0:
                return False, "La cantidad no puede ser negativa", None
            
            if cantidad_int > 999999:
                return False, "La cantidad es demasiado alta", None
            
            return True, "Cantidad válida", cantidad_int
            
        except (ValueError, TypeError):
            return False, "Formato de cantidad inválido", None
    
    @staticmethod
    def validar_codigo_barras(codigo_barras: str) -> Tuple[bool, str]:
        """
        Valida código de barras
        
        Args:
            codigo_barras: Código de barras a validar
            
        Returns:
            Tuple con (es_valido, mensaje)
        """
        if not codigo_barras or not codigo_barras.strip():
            return True, "Código de barras opcional"
        
        codigo_barras = codigo_barras.strip()
        
        if not re.match(Validacion.PATRON_CODIGO_BARRAS, codigo_barras):
            return False, "El código de barras debe contener entre 8 y 14 dígitos"
        
        return True, "Código de barras válido"
    
    @staticmethod
    def validar_descripcion(descripcion: str) -> Tuple[bool, str]:
        """
        Valida descripción (opcional)
        
        Args:
            descripcion: Descripción a validar
            
        Returns:
            Tuple con (es_valido, mensaje)
        """
        if not descripcion:
            return True, "Descripción opcional"
        
        descripcion = descripcion.strip()
        
        if len(descripcion) > Validacion.DESCRIPCION_MAX_LENGTH:
            return False, f"La descripción es demasiado larga (máximo {Validacion.DESCRIPCION_MAX_LENGTH} caracteres)"
        
        return True, "Descripción válida"

class ValidadorFormularios:
    """Validador específico para formularios completos"""
    
    @staticmethod
    def validar_producto(datos: dict) -> Tuple[bool, List[str]]:
        """
        Valida todos los datos de un producto
        
        Args:
            datos: Diccionario con datos del producto
            
        Returns:
            Tuple con (es_valido, lista_errores)
        """
        errores = []
        
        # Validar código
        valido, mensaje = Validador.validar_codigo_producto(datos.get('codigo', ''))
        if not valido:
            errores.append(mensaje)
        
        # Validar nombre
        valido, mensaje = Validador.validar_nombre(datos.get('nombre', ''), 'nombre del producto')
        if not valido:
            errores.append(mensaje)
        
        # Validar descripción
        valido, mensaje = Validador.validar_descripcion(datos.get('descripcion', ''))
        if not valido:
            errores.append(mensaje)
        
        # Validar precio de compra
        precio_compra = datos.get('precio_compra')
        if precio_compra is not None:
            valido, mensaje, _ = Validador.validar_precio(precio_compra)
            if not valido:
                errores.append(f"Precio de compra: {mensaje}")
        
        # Validar precio de venta
        precio_venta = datos.get('precio_venta')
        if precio_venta is not None:
            valido, mensaje, _ = Validador.validar_precio(precio_venta)
            if not valido:
                errores.append(f"Precio de venta: {mensaje}")
        
        # Validar stock actual
        valido, mensaje, _ = Validador.validar_cantidad(datos.get('stock_actual', 0))
        if not valido:
            errores.append(f"Stock actual: {mensaje}")
        
        # Validar stock mínimo
        valido, mensaje, _ = Validador.validar_cantidad(datos.get('stock_minimo', 0))
        if not valido:
            errores.append(f"Stock mínimo: {mensaje}")
        
        # Validar código de barras
        valido, mensaje = Validador.validar_codigo_barras(datos.get('codigo_barras', ''))
        if not valido:
            errores.append(mensaje)
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validar_cliente(datos: dict) -> Tuple[bool, List[str]]:
        """
        Valida todos los datos de un cliente
        
        Args:
            datos: Diccionario con datos del cliente
            
        Returns:
            Tuple con (es_valido, lista_errores)
        """
        errores = []
        
        # Validar nombre
        valido, mensaje = Validador.validar_nombre(datos.get('nombre', ''), 'nombre')
        if not valido:
            errores.append(mensaje)
        
        # Validar email
        if datos.get('email'):
            valido, mensaje = Validador.validar_email(datos.get('email', ''))
            if not valido:
                errores.append(mensaje)
        
        # Validar teléfono
        if datos.get('telefono'):
            valido, mensaje = Validador.validar_telefono(datos.get('telefono', ''))
            if not valido:
                errores.append(mensaje)
        
        # Validar RFC
        if datos.get('rfc'):
            valido, mensaje = Validador.validar_rfc(datos.get('rfc', ''))
            if not valido:
                errores.append(mensaje)
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validar_venta(datos: dict) -> Tuple[bool, List[str]]:
        """
        Valida los datos de una venta
        
        Args:
            datos: Diccionario con datos de la venta
            
        Returns:
            Tuple con (es_valido, lista_errores)
        """
        errores = []
        
        # Validar que tenga productos
        if not datos.get('productos') or len(datos.get('productos', [])) == 0:
            errores.append("La venta debe tener al menos un producto")
        
        # Validar total
        valido, mensaje, _ = Validador.validar_precio(datos.get('total', 0))
        if not valido:
            errores.append(f"Total de venta: {mensaje}")
        
        # Validar método de pago
        if not datos.get('metodo_pago'):
            errores.append("Debe seleccionar un método de pago")
        
        return len(errores) == 0, errores

# Funciones de utilidad para validaciones comunes

def es_numero_positivo(valor: Union[str, int, float]) -> bool:
    """Verifica si un valor es un número positivo"""
    try:
        num = float(valor)
        return num > 0
    except (ValueError, TypeError):
        return False

def es_entero_positivo(valor: Union[str, int]) -> bool:
    """Verifica si un valor es un entero positivo"""
    try:
        num = int(valor)
        return num > 0
    except (ValueError, TypeError):
        return False

def limpiar_texto(texto: str) -> str:
    """Limpia y normaliza texto"""
    if not texto:
        return ""
    
    # Remover espacios extra y caracteres especiales peligrosos
    texto = texto.strip()
    texto = re.sub(r'\s+', ' ', texto)  # Múltiples espacios por uno
    
    return texto

def normalizar_codigo(codigo: str) -> str:
    """Normaliza un código para consistencia"""
    if not codigo:
        return ""
    
    return codigo.strip().upper().replace(' ', '')

def formatear_telefono(telefono: str) -> str:
    """Formatea un teléfono para almacenamiento"""
    if not telefono:
        return ""
    
    # Remover todo excepto números y +
    telefono = re.sub(r'[^\d+]', '', telefono)
    
    return telefono