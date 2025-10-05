#!/usr/bin/env python3
"""
VentaPro Universal - Verificador Automático de Dependencias
Verifica e instala automáticamente las dependencias necesarias
"""

import subprocess
import sys
import os

def install_package(package):
    """Instala un paquete Python usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Verifica e instala las dependencias necesarias"""
    
    print("🔍 Verificando dependencias de VentaPro Universal...")
    
    # Lista de dependencias requeridas
    required_packages = [
        "customtkinter>=5.2.0",
        "pillow>=9.0.0",
        "packaging"
    ]
    
    missing_packages = []
    
    # Verificar cada dependencia
    for package in required_packages:
        package_name = package.split(">=")[0]
        try:
            __import__(package_name)
            print(f"✅ {package_name} - OK")
        except ImportError:
            print(f"❌ {package_name} - FALTANTE")
            missing_packages.append(package)
    
    # Instalar paquetes faltantes
    if missing_packages:
        print(f"\n📦 Instalando {len(missing_packages)} dependencias faltantes...")
        
        for package in missing_packages:
            print(f"  📥 Instalando {package}...")
            if install_package(package):
                print(f"  ✅ {package} instalado correctamente")
            else:
                print(f"  ❌ Error instalando {package}")
                return False
    
    print("\n🎉 Todas las dependencias están correctas!")
    return True

def main():
    """Función principal"""
    
    print("=" * 60)
    print("🚀 VENTAPRO UNIVERSAL - VERIFICADOR DE DEPENDENCIAS")  
    print("=" * 60)
    
    # Verificar Python 3.7+
    if sys.version_info < (3, 7):
        print("❌ Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - OK")
    
    # Verificar e instalar dependencias
    if not check_and_install_dependencies():
        print("\n❌ Error en la verificación de dependencias")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 SISTEMA LISTO PARA EJECUTAR")
    print("=" * 60)
    print("➡️  Para iniciar VentaPro: python main.py")
    print("➡️  O usar el archivo: INICIAR_VENTAPRO.bat")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        input("\n⏸️  Presiona Enter para continuar...")
    sys.exit(0 if success else 1)