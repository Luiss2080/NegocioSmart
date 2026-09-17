"""
Seguridad - Hashing de contraseñas - NegocioSmart
==================================================

Utilidades para almacenar y verificar contraseñas de forma segura.

Antes, `usuarios.password_hash` guardaba la contraseña en texto plano
(por ejemplo `admin123` tal cual). Esto es inseguro incluso para una
app de escritorio local: cualquiera que abra el archivo `data/erp.db`
con un visor de SQLite (o copie el archivo) obtiene todas las
contraseñas directamente, sin ningún esfuerzo.

Este módulo usa PBKDF2-HMAC-SHA256 (disponible en la librería estándar
de Python, sin dependencias externas) con una sal aleatoria por
usuario y un número de iteraciones configurable, siguiendo la
recomendación de OWASP para hashing de contraseñas cuando no se
dispone de bcrypt/argon2.

Formato almacenado en `password_hash`:
    pbkdf2_sha256$<iteraciones>$<sal_hex>$<hash_hex>

Uso:
    from utils.seguridad import hash_password, verificar_password

    hash_guardado = hash_password("admin123")
    verificar_password("admin123", hash_guardado)  # True
    verificar_password("incorrecta", hash_guardado)  # False
"""

import hashlib
import hmac
import secrets

ALGORITMO = "pbkdf2_sha256"
ITERACIONES_DEFECTO = 260_000
LONGITUD_SAL_BYTES = 16


def hash_password(password: str, iteraciones: int = ITERACIONES_DEFECTO) -> str:
    """Genera un hash seguro y salado de una contraseña.

    Args:
        password: Contraseña en texto plano.
        iteraciones: Número de iteraciones de PBKDF2 (mayor = más lento
            de romper por fuerza bruta, pero también más lento de
            verificar). El valor por defecto sigue la recomendación
            vigente de OWASP para PBKDF2-HMAC-SHA256.

    Returns:
        Cadena con el formato ``pbkdf2_sha256$iteraciones$sal$hash``,
        lista para guardar en la columna ``password_hash``.

    Raises:
        ValueError: si la contraseña está vacía.
    """
    if not password:
        raise ValueError("La contraseña no puede estar vacía")

    sal = secrets.token_hex(LONGITUD_SAL_BYTES)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), sal.encode("utf-8"), iteraciones
    )
    return f"{ALGORITMO}${iteraciones}${sal}${derivado.hex()}"


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Verifica una contraseña contra un hash generado por ``hash_password``.

    Devuelve ``False`` (nunca lanza excepción por datos malformados) si
    el hash guardado no tiene el formato esperado, incluyendo el caso
    de contraseñas antiguas guardadas en texto plano por versiones
    previas del sistema: esas nunca podrán "verificarse" como
    correctas mediante esta función, lo que fuerza a regenerar el hash
    (ver ``necesita_rehash``).

    Args:
        password: Contraseña en texto plano a verificar.
        hash_guardado: Valor almacenado en ``password_hash``.

    Returns:
        True si la contraseña coincide con el hash, False en cualquier
        otro caso (no coincide, formato inválido, hash vacío, etc.).
    """
    if not password or not hash_guardado:
        return False

    try:
        algoritmo, iteraciones_str, sal, hash_hex = hash_guardado.split("$")
    except ValueError:
        # Formato inesperado (p. ej. contraseña heredada en texto plano)
        return False

    if algoritmo != ALGORITMO:
        return False

    try:
        iteraciones = int(iteraciones_str)
    except ValueError:
        return False

    derivado = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), sal.encode("utf-8"), iteraciones
    )

    # Comparación en tiempo constante para evitar ataques de temporización.
    return hmac.compare_digest(derivado.hex(), hash_hex)


def necesita_rehash(hash_guardado: str) -> bool:
    """Indica si un valor de ``password_hash`` no está en el formato
    seguro esperado (por ejemplo, una contraseña heredada en texto
    plano) y por lo tanto debería regenerarse con ``hash_password`` en
    el próximo login exitoso.
    """
    if not hash_guardado:
        return True
    partes = hash_guardado.split("$")
    return len(partes) != 4 or partes[0] != ALGORITMO
