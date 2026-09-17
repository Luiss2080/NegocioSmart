"""
Tests de hashing de contraseñas (utils/seguridad.py) y de que el
sistema realmente lo usa en vez de guardar texto plano.
"""

import pytest

from utils.seguridad import hash_password, verificar_password, necesita_rehash


def test_hash_no_es_la_contrasena_en_texto_plano():
    hashed = hash_password("admin123")
    assert hashed != "admin123"
    assert "admin123" not in hashed


def test_verificar_password_correcta():
    hashed = hash_password("mi-clave-segura")
    assert verificar_password("mi-clave-segura", hashed) is True


def test_verificar_password_incorrecta():
    hashed = hash_password("mi-clave-segura")
    assert verificar_password("otra-clave", hashed) is False


def test_dos_hashes_de_la_misma_password_son_distintos_por_la_sal():
    h1 = hash_password("repetida")
    h2 = hash_password("repetida")
    assert h1 != h2
    assert verificar_password("repetida", h1)
    assert verificar_password("repetida", h2)


def test_password_vacia_lanza_error():
    with pytest.raises(ValueError):
        hash_password("")


def test_hash_legado_en_texto_plano_nunca_verifica_como_correcto():
    """Una contraseña vieja guardada en texto plano no debe poder
    'colarse' como válida sólo porque coincide como string."""
    assert verificar_password("admin123", "admin123") is False


def test_necesita_rehash_detecta_texto_plano_legado():
    assert necesita_rehash("admin123") is True
    assert necesita_rehash(hash_password("admin123")) is False
    assert necesita_rehash("") is True


def test_admin_por_defecto_queda_hasheado_en_la_base_de_datos(db):
    fila = db.ejecutar_consulta(
        "SELECT password_hash FROM usuarios WHERE usuario = ?", ("admin",)
    )
    assert fila, "El usuario admin por defecto debería existir"
    password_hash = fila[0]["password_hash"]
    assert password_hash != "admin123"
    assert verificar_password("admin123", password_hash) is True
