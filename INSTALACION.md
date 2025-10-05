# 🚀 **GUÍA DE INSTALACIÓN RÁPIDA**

## ⚡ **INSTALACIÓN EN 1 CLIC**

### 🪟 **Windows:**
1. Descarga el proyecto desde GitHub
2. **Doble clic en:** `instalar.bat`
3. **Para ejecutar:** `INICIAR_VENTAPRO.bat`

### 🐧 **Linux/Mac:**
```bash
# Clonar repositorio
git clone https://github.com/Luiss2080/NegocioSmart.git
cd NegocioSmart

# Instalar
chmod +x instalar.sh ejecutar.sh
./instalar.sh

# Ejecutar
./ejecutar.sh
```

---

## 📋 **REQUISITOS MÍNIMOS**

### 🐍 **Python 3.8 o superior**
- **Windows:** Descargar desde [python.org](https://python.org)
- **Linux:** `sudo apt install python3 python3-venv python3-pip`
- **Mac:** `brew install python3`

### 💾 **Espacio en disco:** ~200 MB
### 🧠 **RAM:** 4 GB mínimo, 8 GB recomendado

---

## 🎯 **INSTALACIÓN PASO A PASO**

### 1️⃣ **Descargar el Proyecto:**
```bash
git clone https://github.com/Luiss2080/NegocioSmart.git
cd NegocioSmart
```

### 2️⃣ **Ejecutar Instalador:**

**Windows:**
```cmd
instalar.bat
```

**Linux/Mac:**
```bash
chmod +x instalar.sh
./instalar.sh
```

### 3️⃣ **Ejecutar la Aplicación:**

**Windows:**
```cmd
INICIAR_VENTAPRO.bat
```

**Linux/Mac:**
```bash
./ejecutar.sh
```

---

## 🔧 **INSTALACIÓN MANUAL (Opcional)**

Si prefieres instalar manualmente:

```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar instalación
python verificar_entorno.py

# 5. Ejecutar aplicación
python main.py
```

---

## ✅ **VERIFICACIÓN DE INSTALACIÓN**

Después de la instalación, deberías ver:

```
🎉 ¡ENTORNO COMPLETAMENTE FUNCIONAL!
📋 VentaPro Universal listo para ejecutar
```

---

## 🆘 **SOLUCIÓN DE PROBLEMAS**

### ❌ **"Python no encontrado"**
- **Solución:** Instala Python 3.8+ desde python.org
- **Verifica:** `python --version`

### ❌ **"Error instalando dependencias"**
- **Solución:** Actualiza pip: `python -m pip install --upgrade pip`
- **Intenta:** Ejecutar como administrador

### ❌ **"Entorno virtual no encontrado"**
- **Solución:** Ejecuta primero el instalador
- **Verifica:** Que existe la carpeta `.venv`

### ❌ **"CustomTkinter no funciona"**
- **Solución:** Reinstala: `pip install --upgrade customtkinter`
- **Alternativa:** Usa `pip install --force-reinstall customtkinter`

---

## 📞 **SOPORTE**

- 📧 **GitHub Issues:** [Crear Issue](https://github.com/Luiss2080/NegocioSmart/issues)
- 📚 **Documentación:** Ver `README.md`
- 🔧 **Logs de error:** Revisar `logs/app.log`

---

*✨ Instalación simplificada para máxima compatibilidad*

## 🎉 **¡LISTO PARA USAR EN CUALQUIER COMPUTADORA!** 🎉