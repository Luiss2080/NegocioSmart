#!/usr/bin/env python3
"""
Script de verificación del entorno NegocioSmart
Verifica que todas las dependencias estén correctamente instaladas
"""

def verificar_entorno():
    """Verificar que el entorno esté correctamente configurado"""
    
    print("🔍 Verificando entorno NegocioSmart...")
    print("=" * 50)
    
    # Verificar librerías críticas
    dependencias = [
        ("customtkinter", "CustomTkinter - Interfaz moderna"),
        ("colorama", "Colorama - Colores en terminal"),
        ("matplotlib.pyplot", "Matplotlib - Gráficos y reportes"),
        ("sqlite3", "SQLite3 - Base de datos"),
        ("json", "JSON - Manejo de datos"),
        ("datetime", "DateTime - Manejo de fechas")
    ]
    
    todas_ok = True
    
    for modulo, descripcion in dependencias:
        try:
            __import__(modulo)
            print(f"✅ {descripcion}")
        except ImportError as e:
            print(f"❌ {descripcion} - ERROR: {e}")
            todas_ok = False
    
    print("=" * 50)
    
    if todas_ok:
        print("🎉 ¡ENTORNO COMPLETAMENTE FUNCIONAL!")
        print("📋 NegocioSmart listo para ejecutar")
        return True
    else:
        print("⚠️  Hay dependencias faltantes")
        print("💡 Ejecutar: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    verificar_entorno()