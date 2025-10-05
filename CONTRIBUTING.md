# 🤝 Guía de Contribución - VentaPro Universal

¡Gracias por tu interés en contribuir a VentaPro Universal! 🎉

## 🚀 **Cómo Contribuir**

### 1️⃣ **Fork y Clona**
```bash
# 1. Haz fork del repositorio en GitHub
# 2. Clona tu fork
git clone https://github.com/TU-USUARIO/NegocioSmart.git
cd NegocioSmart
```

### 2️⃣ **Configura el Entorno**
```bash
# Instala las dependencias de desarrollo
./instalar.sh  # Linux/Mac
# o
instalar.bat   # Windows
```

### 3️⃣ **Crea una Rama**
```bash
# Crea una rama descriptiva
git checkout -b feature/nueva-funcionalidad
# o
git checkout -b bugfix/correccion-error
```

### 4️⃣ **Desarrolla y Prueba**
```bash
# Ejecuta las pruebas antes de hacer cambios
python verificar_entorno.py

# Desarrolla tu funcionalidad
# ...

# Prueba tus cambios
python main.py
```

### 5️⃣ **Commit y Push**
```bash
# Commit descriptivo
git add .
git commit -m "✨ Agregar nueva funcionalidad de reportes"

# Push a tu fork
git push origin feature/nueva-funcionalidad
```

### 6️⃣ **Pull Request**
1. Ve a GitHub y crea un Pull Request
2. Describe claramente los cambios realizados
3. Incluye capturas de pantalla si es relevante

---

## 📝 **Estándares de Código**

### 🐍 **Python Style Guide**
- Seguir **PEP 8** para el estilo de código
- Usar **docstrings** para funciones y clases
- **Comentarios claros** en español
- **Nombres descriptivos** para variables y funciones

### 📁 **Estructura de Archivos**
```
NegocioSmart/
├── main.py              # Aplicación principal
├── database/            # Módulos de base de datos
├── ui/                  # Interfaces de usuario
├── utils/               # Utilidades y herramientas
├── modules/             # Módulos de negocio
├── requirements.txt     # Dependencias
└── README.md           # Documentación
```

### 🧪 **Testing**
- Asegurar que `python verificar_entorno.py` pase
- Probar funcionalidad básica con `python main.py`
- Verificar que no se rompan características existentes

---

## 🎯 **Tipos de Contribuciones**

### 🐛 **Reportar Bugs**
- Usar el template de issues de GitHub
- Incluir pasos para reproducir el error
- Agregar capturas de pantalla si es posible
- Especificar sistema operativo y versión de Python

### ✨ **Nuevas Características**
- Abrir un issue de "Feature Request" primero
- Discutir la implementación antes de desarrollar
- Seguir el diseño y arquitectura existente
- Documentar la nueva funcionalidad

### 📚 **Mejorar Documentación**
- Corregir errores tipográficos
- Agregar ejemplos y tutoriales
- Traducir a otros idiomas
- Mejorar la claridad de las instrucciones

### 🎨 **Mejorar UI/UX**
- Seguir el diseño de CustomTkinter existente
- Mantener consistencia visual
- Probar en diferentes resoluciones
- Documentar cambios de interfaz

---

## 🏆 **Reconocimientos**

Los contribuidores serán reconocidos en:
- 📜 **Archivo CONTRIBUTORS.md**
- 🏷️ **Release notes** de GitHub  
- 📋 **Sección de créditos** en la aplicación
- ⭐ **Hall of Fame** en el README

---

## 📞 **Contacto y Ayuda**

- 💬 **Discord:** [Únete a la comunidad](https://discord.gg/ventapro)
- 📧 **Email:** [Contactar mantenedor](mailto:github@luiss2080.dev)
- 🐛 **Issues:** [GitHub Issues](https://github.com/Luiss2080/NegocioSmart/issues)
- 💡 **Discusiones:** [GitHub Discussions](https://github.com/Luiss2080/NegocioSmart/discussions)

---

## 📋 **Checklist del Pull Request**

Antes de enviar tu PR, asegúrate de:

- [ ] ✅ El código sigue el estilo PEP 8
- [ ] 📝 Los cambios están documentados
- [ ] 🧪 Las pruebas básicas pasan
- [ ] 🔍 No hay errores de importación
- [ ] 📸 Capturas incluidas (si hay cambios UI)
- [ ] 📋 Descripción clara del PR
- [ ] 🏷️ Labels apropiados asignados

---

## 🎉 **¡Gracias por Contribuir!**

Tu contribución hace que VentaPro Universal sea mejor para todos los pequeños negocios del mundo. ¡Cada línea de código cuenta! 🚀

---

*¿Primera vez contribuyendo a open source? ¡No te preocupes! Estamos aquí para ayudarte. 💜*