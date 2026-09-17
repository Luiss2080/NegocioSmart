# 🏪 NegocioSmart

> Sistema de punto de venta e inventario de escritorio, en Python + SQLite,
> para pequeños negocios (tiendas, ferreterías, farmacias, boutiques) que
> necesitan cobrar, controlar stock y ver reportes básicos sin depender de
> internet ni de una suscripción mensual: todo corre y se guarda en la propia
> computadora.

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2%2B-green?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![SQLite](https://img.shields.io/badge/SQLite-3-orange?style=for-the-badge&logo=sqlite)](https://sqlite.org)
[![Tests](https://img.shields.io/badge/tests-pytest-informational?style=for-the-badge)](tests)
[![License](https://img.shields.io/badge/License-MIT%20%2B%20terms-red?style=for-the-badge)](LICENSE)

</div>

---

## Características

Verificadas contra el código real (no aspiracionales):

- **🛒 Punto de venta (POS)**: carrito con búsqueda de productos, cálculo de
  totales, y **persistencia real y atómica en SQLite**: una venta descuenta
  stock y queda registrada en `ventas`/`detalle_ventas` en una sola
  transacción, o no se aplica nada (ver `services/ventas_service.py`). La
  base de datos —no la interfaz— es quien decide si hay stock suficiente,
  así que no es posible vender más unidades de las que existen.
- **📦 Inventario y productos**: alta/edición de productos, categorías,
  ajuste de stock (entrada, salida o ajuste a cantidad exacta) con
  validación de cantidades y precios (rechaza negativos, formatos
  inválidos y precios con más de 2 decimales), alertas de stock bajo.
- **👥 Clientes y proveedores**: alta rápida de clientes, historial de
  compras por cliente, módulo dedicado de proveedores.
- **📊 Reportes básicos**: resumen de ventas del día, historial, estadísticas
  generales e inventario por categoría, con respaldo automático a JSON/CSV
  en cada operación (`utils/backup_manager.py`). El módulo de reportes
  avanzado (`modules/reportes.py`) agrega más tipos de análisis, aunque hoy
  usa datos de demostración y su exportación a PDF está simulada — no un
  export real todavía.
- **⚙️ Configuración centralizada**: nombre y datos del negocio, moneda,
  tasa de impuesto, umbral de stock bajo, etc. se editan en `config.ini`
  (`utils/config_manager.py`), sin tocar código.
- **💾 Backups automáticos**: cada venta, producto nuevo o reporte generado
  se respalda también como JSON/CSV en `data/backups/`.

### Seguridad y correctitud (lo que se auditó y corrigió)

- **Sin inyección SQL**: todas las consultas de `database/consultas.py` usan
  parámetros ligados (`?`), nunca interpolación de texto.
- **Contraseñas hasheadas**: `usuarios.password_hash` usa PBKDF2-HMAC-SHA256
  con sal aleatoria (`utils/seguridad.py`), no texto plano.
- **Matemática de dinero con `Decimal`**, nunca `float`: totales, descuentos
  e impuestos se calculan y redondean a centavos de forma exacta, con
  descuentos siempre limitados al importe que descuentan (nunca dan un
  total negativo).
- **Sin sobreventa**: el descuento de stock usa una actualización
  condicionada (`WHERE stock_actual >= cantidad`) dentro de una transacción
  que se revierte por completo si cualquier línea del carrito no tiene
  stock suficiente.

### Qué NO incluye todavía (para ser honestos)

- No hay pantalla de login: la tabla `usuarios` y sus roles existen, pero
  `enable_login = false` por defecto y la interfaz no pide credenciales.
- Es una app de un solo usuario/proceso en una sola computadora: la base de
  datos SQLite (`data/erp.db`) no está protegida ni cifrada en disco; para
  un equipo compartido, protege el archivo a nivel de sistema operativo.
- Exportar reportes a PDF real y a Excel no está implementado (las
  dependencias `reportlab`/`openpyxl` están listadas pero no se usan
  todavía); sí funciona la exportación a JSON/CSV.

## Cómo usar

1. Ejecuta la aplicación (`python main.py`). La primera vez crea
   `data/erp.db`, siembra un catálogo de ejemplo y abre el dashboard.
2. Ve a **Punto de Venta** para armar un carrito y presionar
   **Procesar Venta**: la venta y el descuento de stock quedan guardados de
   verdad en la base de datos.
3. Ve a **Productos** para dar de alta artículos, ajustar stock o revisar
   alertas de stock bajo.
4. Ve a **Clientes**/**Proveedores** para administrarlos, y a **Reportes**
   para ver el resumen del día.
5. Ajusta nombre del negocio, moneda, impuesto y demás en **Configuración**
   (o editando `config.ini` directamente).

## Instalación y uso local

```bash
# 1. Clonar el repositorio
git clone https://github.com/Luiss2080/NegocioSmart.git
cd NegocioSmart

# 2. Crear y activar un entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Opcional) Verificar que el entorno está completo
python verificar_entorno.py

# 5. Ejecutar la aplicación
python main.py
# En Linux/Mac también puedes usar:
./ejecutar.sh
```

Requiere Python 3.8 o superior. No necesita un servidor de base de datos
aparte: SQLite viene incluido en la librería estándar de Python.

## Tecnologías

- **Python 3.8+** con **CustomTkinter** para la interfaz gráfica.
- **SQLite3** (librería estándar) como base de datos, vía
  `database/db_manager.py`.
- **`decimal.Decimal`** (librería estándar) para toda la matemática de
  dinero — nunca `float`.
- **pandas / matplotlib / reportlab / openpyxl / Pillow**: dependencias
  listadas para análisis y exportación avanzada; hoy sólo `matplotlib` se
  importa en el módulo de reportes avanzado, y no todavía para renderizar
  gráficos activos.
- **pytest** para la suite de tests automatizados.
- **GitHub Actions** para CI (matriz Windows/Linux/macOS × Python 3.8–3.12,
  lint con flake8, chequeo de seguridad con bandit/safety/pip-audit, y la
  suite de pytest).

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```

La suite cubre las áreas de mayor riesgo para un punto de venta: matemática
de dinero con `Decimal` (incluyendo descuentos del 100%, descuentos mayores
al importe, cantidades negativas/cero), el servicio de ventas atómico
(sobreventa, carritos mixtos con una línea sin stock, ventas secuenciales),
seguridad de las consultas SQL parametrizadas, y hashing de contraseñas.

## Licencia

MIT, con algunos términos adicionales para uso comercial (atribución
sugerida pero no obligatoria, sin garantía sobre errores de cálculo, etc.)
— por eso GitHub puede mostrarla como "Other" en vez de "MIT" a secas. Ver
el archivo [`LICENSE`](LICENSE) completo para el texto exacto.
