# 🚀 NegocioSmart - Guía de Instalación y Uso

## 📋 Requisitos del Sistema

### Requisitos Mínimos
- **Python 3.10 o superior**
- **Windows 10/11** (compatible con Linux/macOS)
- **4 GB RAM mínimo**
- **500 MB espacio libre en disco**

### Verificar Python
```bash
python --version
```
Si no tienes Python, descárgalo desde: https://python.org/downloads/

---

## ⚡ Instalación Rápida

### 1. **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### 2. **Ejecutar la Aplicación**
```bash
python main.py
```

---

## 🔧 Instalación Detallada

### Paso 1: Clonar/Descargar el Proyecto
```bash
git clone https://github.com/Luiss2080/NegocioSmart.git
cd NegocioSmart
```

### Paso 2: Crear Entorno Virtual (Recomendado)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la Aplicación
```bash
python main.py
```

---

## 🎯 Uso Básico

### Primer Inicio
1. Al ejecutar `python main.py`, la aplicación:
   - ✅ Creará la base de datos automáticamente
   - ✅ Inicializará las tablas necesarias
   - ✅ Abrirá la interfaz gráfica

### Funcionalidades Principales
- **👥 Gestión de Clientes** - Agregar, editar y buscar clientes
- **📦 Inventario** - Control completo de productos y stock
- **💰 Ventas** - Sistema de punto de venta (POS)
- **📊 Reportes** - Análisis de ventas y inventario
- **👥 Proveedores** - Gestión de proveedores

---

## 🛠️ Solución de Problemas

### Error: "No module named 'customtkinter'"
```bash
pip install customtkinter
```

### Error: "No module named 'pandas'"
```bash
pip install pandas openpyxl matplotlib
```

### Error: Base de Datos
- La base de datos se crea automáticamente en `data/erp.db`
- Si hay problemas, elimina el archivo `data/erp.db` y reinicia

### Error: Permisos
- Ejecuta como administrador si hay problemas de permisos
- Asegúrate de tener permisos de escritura en la carpeta

---

## 📁 Estructura del Proyecto

```
NegocioSmart/
├── main.py              # 🚀 APLICACIÓN PRINCIPAL
├── config.ini           # ⚙️ Configuración
├── requirements.txt     # 📦 Dependencias
├── database/           # 🗄️ Base de datos
├── ui/                 # 🎨 Interfaz de usuario
├── utils/              # 🛠️ Utilidades
├── modules/            # 📊 Módulos de negocio
├── data/               # 💾 Datos y backups
└── logs/               # 📋 Registros
```

---

## 🎨 Personalización

### Cambiar Tema de la Aplicación
Edita `config.ini`:
```ini
[APPLICATION]
theme = modern
language = es
```

### Configurar Base de Datos
Edita `config.ini`:
```ini
[DATABASE]
db_path = data/erp.db
backup_enabled = true
backup_interval = 24
```

---

## 📞 Soporte

### Si tienes problemas:
1. Verifica que Python 3.10+ esté instalado
2. Instala todas las dependencias: `pip install -r requirements.txt`
3. Ejecuta: `python main.py`
4. Revisa los logs en `logs/app.log`

### Logs de Error
Los errores se guardan automáticamente en:
- `logs/app.log` - Log principal de la aplicación

---

## 🔄 Actualización

### Para actualizar NegocioSmart:
1. Respalda tu base de datos (`data/erp.db`)
2. Descarga la nueva versión
3. Ejecuta: `pip install -r requirements.txt`
4. Inicia normalmente: `python main.py`

---

## ✅ Verificación de Instalación

Ejecuta estos comandos para verificar:

```bash
# 1. Verificar Python
python --version

# 2. Verificar dependencias
pip list

# 3. Ejecutar aplicación
python main.py
```

### Salida Esperada:
```
🌍 Iniciando NegocioSmart - Sistema para TODO tipo de negocio...
✅ Base de datos inicializada correctamente
🚀 NegocioSmart iniciado correctamente
🎯 Sistema adaptable a cualquier tipo de negocio
```

---

## 🎯 ¡Listo para Usar!

Si ves el mensaje de inicio exitoso, **¡NegocioSmart está funcionando correctamente!**

La aplicación se abrirá en una ventana gráfica donde podrás:
- Gestionar productos
- Realizar ventas
- Ver reportes
- Administrar clientes

**¡Disfruta usando NegocioSmart!** 🎉