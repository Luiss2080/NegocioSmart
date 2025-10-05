# VentaPro Universal
__version__ = "1.0.0"
__author__ = "Luiss2080"
__email__ = "github@luiss2080.dev"
__license__ = "MIT"
__description__ = "Sistema Universal de Gestión Comercial"

# Configuración de la aplicación
APP_NAME = "VentaPro Universal"
APP_VERSION = __version__
APP_AUTHOR = __author__
APP_LICENSE = __license__

# URLs del proyecto
GITHUB_URL = "https://github.com/Luiss2080/NegocioSmart"
ISSUES_URL = f"{GITHUB_URL}/issues"
RELEASES_URL = f"{GITHUB_URL}/releases"
DOCS_URL = f"{GITHUB_URL}/blob/main/README.md"

# Configuración de dependencias mínimas
MIN_PYTHON_VERSION = (3, 8)
REQUIRED_PACKAGES = [
    "customtkinter>=5.2.0",
    "colorama>=0.4.6", 
    "matplotlib>=3.9.0",
    "pandas>=1.5.0",
    "pillow>=9.0.0"
]

# Metadatos para instaladores
INSTALLER_CONFIG = {
    "app_name": APP_NAME,
    "version": APP_VERSION,
    "author": APP_AUTHOR,
    "license": APP_LICENSE,
    "python_min": f"{MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}",
    "main_script": "main.py",
    "requirements_file": "requirements.txt"
}