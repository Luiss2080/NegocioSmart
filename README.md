# � VentaPro - Sistema Universal de Gestión Comercial

![VentaPro Logo](assets/images/banner.jpg)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](main_mvp.py)
[![Universal](https://img.shields.io/badge/Universal-All%20Business%20Types-gold.svg)](README.md)

## 📋 Descripción

**VentaPro** es un **sistema UNIVERSAL** de punto de venta (POS) y gestión de inventario que se adapta a **CUALQUIER TIPO DE NEGOCIO**. Diseñado para pequeñas y medianas empresas que necesitan una solución profesional, completa, fácil de usar y **SIN COSTOS DE SUSCRIPCIÓN**.

## 🌍 **SISTEMA VERDADERAMENTE UNIVERSAL**

### 🏪 **Tipos de Negocios Soportados:**
✅ **Tiendas de Abarrotes** - Control de inventario perecedero y no perecedero  
✅ **Ferreterías** - Gestión de herramientas, materiales y proveedores  
✅ **Papelerías** - Artículos de oficina, útiles escolares y suministros  
✅ **Boutiques de Ropa** - Manejo de tallas, colores, temporadas y marcas  
✅ **Librerías** - Inventario por ISBN, autores y categorías literarias  
✅ **Farmacias** - Control de medicamentos, fechas de vencimiento y recetas  
✅ **Restaurantes** - Menús, ingredientes, comandas y mesas  
✅ **Talleres Mecánicos** - Servicios, repuestos y mano de obra  
✅ **Distribuidoras** - Ventas al mayoreo y minoreo con descuentos por volumen  
✅ **Panaderías** - Productos horneados, ingredientes y producción diaria  
✅ **Veterinarias** - Servicios médicos, productos y historiales de mascotas  
✅ **Zapaterías** - Calzado por tallas, marcas y estilos  
✅ **Perfumerías** - Productos de belleza, marcas y líneas de productos  
✅ **Electrodomésticos** - Aparatos, garantías y servicios técnicos  
✅ **Jugueterías** - Juguetes por edades, marcas y categorías  
✅ **Cualquier Comercio** - **100% Adaptable a sus necesidades**

## 🎯 **Objetivo Principal**

Proporcionar a **CUALQUIER COMERCIANTE** una herramienta profesional que se adapte perfectamente a su industria:

### 💼 **Para Tu Tipo de Negocio:**
- 📦 **Gestionar inventario** específico (productos físicos, servicios, digitales)
- 💰 **Procesar ventas** con flujos adaptados a tu industria
- 📄 **Generar facturas** profesionales personalizadas  
- 📊 **Obtener reportes** específicos para tu sector
- ⚠️ **Controlar stock** con alertas inteligentes por industria
- 📈 **Analizar tendencias** relevantes para tu mercado

### 🌟 **Características Universales:**
- ✅ **Auto-configuración** según tipo de negocio
- ✅ **Campos dinámicos** específicos por industria  
- ✅ **Flujos de trabajo** optimizados
- ✅ **Reportes especializados** por sector
- ✅ **Sin límites** de adaptación
- ✅ Controlar stock y recibir alertas de productos con bajo inventario
- ✅ Analizar tendencias de ventas y productos más vendidos

## ✨ Características Principales

### 1. 📦 Gestión de Inventario
- Alta, baja y modificación de productos
- Control de stock en tiempo real
- Categorización de productos
- Alertas de stock bajo
- Búsqueda rápida por código o nombre

### 2. 💰 Punto de Venta (POS)
- Interfaz intuitiva para ventas rápidas
- Búsqueda de productos por código de barras
- Cálculo automático de totales
- Múltiples métodos de pago
- Registro de clientes (opcional)

### 3. 🧾 Facturación
- Generación automática de facturas en PDF
- Diseño profesional personalizable
- Numeración automática de facturas
- Histórico de todas las ventas

### 4. 📊 Reportes y Análisis
- Dashboard con estadísticas en tiempo real
- Gráficos de ventas por período
- Productos más vendidos
- Análisis de ganancias
- Reportes exportables a Excel
- Gráficos visuales con matplotlib

### 5. 🔒 Seguridad y Respaldos
- Base de datos SQLite local (sin necesidad de servidor)
- Sistema de respaldos automáticos
- Logs de actividad
- Sistema de usuarios (opcional)

## 🔧 Tecnologías Utilizadas

- **Python 3.10+** - Lenguaje principal
- **Tkinter/CustomTkinter** - Interfaz gráfica moderna
- **SQLite** - Base de datos local
- **Pandas** - Análisis de datos
- **Matplotlib** - Gráficos y visualizaciones
- **ReportLab** - Generación de PDFs
- **OpenPyXL** - Exportación a Excel

## 👥 Usuarios Objetivo

- 🏪 Tiendas de abarrotes
- 🔧 Ferreterías
- 📝 Papelerías
- 👗 Boutiques de ropa
- 📚 Librerías
- 💊 Farmacias pequeñas
- 🛒 Cualquier comercio minorista pequeño o mediano

## 📥 Instalación

### Requisitos Previos
- Python 3.10 o superior
- Windows 10/11 (compatible con otros SO)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/ventapro.git
   cd ventapro
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la aplicación**
   ```bash
   # El archivo config.ini se creará automáticamente en el primer uso
   ```

5. **Ejecutar VentaPro**
   ```bash
   python main.py
   ```

## 🚀 Uso Rápido

1. **Primer Inicio**: La aplicación creará automáticamente la base de datos y configuración inicial
2. **Agregar Productos**: Ve a "Gestión de Productos" y agrega tu inventario
3. **Realizar Ventas**: Usa el módulo "Punto de Venta" para registrar transacciones
4. **Ver Reportes**: Consulta estadísticas y genera reportes desde el Dashboard

## 📁 Estructura del Proyecto

```
VentaPro/
├── 📄 main.py                    # Punto de entrada principal
├── 📁 database/                  # Gestión de base de datos
├── 📁 ui/                        # Interfaces gráficas
├── 📁 services/                  # Lógica de negocio
├── 📁 utils/                     # Utilidades y helpers
├── 📁 static/                    # Archivos estáticos (CSS, JS)
├── 📁 templates/                 # Plantillas HTML
├── 📁 data/                      # Base de datos y respaldos
├── 📁 reports/                   # Reportes generados
├── 📁 assets/                    # Recursos multimedia
├── 📁 tests/                     # Pruebas unitarias
├── 📁 logs/                      # Archivos de log
└── 📁 docs/                      # Documentación
```

## 📖 Documentación

- [📘 Manual de Usuario](docs/manual_usuario.md)
- [🔧 Manual Técnico](docs/manual_tecnico.md)
- [⚙️ Guía de Instalación](docs/instalacion.md)
- [🗄️ Estructura de Base de Datos](docs/estructura_db.md)
- [📋 Documentación de API](docs/api_docs.md)

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: Amazing Feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

- 📧 Email: soporte@ventapro.com
- 📱 WhatsApp: +52 xxx-xxx-xxxx
- 🌐 Web: https://ventapro.com

## 📝 Changelog

### v1.0.0 (2025-10-04)
- ✨ Lanzamiento inicial
- 📦 Sistema completo de inventario
- 💰 Punto de venta funcional
- 📊 Dashboard con estadísticas
- 🧾 Generación de facturas PDF

---

**Desarrollado con ❤️ para pequeños y medianos comerciantes**

*VentaPro - Tu aliado en el crecimiento del negocio*