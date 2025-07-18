
# 📊 App de Análisis de Comisiones - Junio 2025

Esta aplicación en Streamlit permite analizar los cierres inmobiliarios del mes de junio 2025 y calcular las comisiones correspondientes por oficina, según el tipo de operación (venta o alquiler) y si fue compartida o no.

---

## 🧩 Estructura del Proyecto

```
📁 tu-repositorio
├── app_comisiones.py        # Código principal de la aplicación
├── requirements.txt         # Dependencias necesarias para ejecutarla
```

---

## 🚀 ¿Cómo usar la app?

### Opción 1: Ejecutar localmente

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta la app:
   ```bash
   streamlit run app_comisiones.py
   ```

---

### Opción 2: Subir a [Streamlit Cloud](https://streamlit.io/cloud)

1. Crea un repositorio en GitHub con estos archivos:
   - `app_comisiones.py`
   - `requirements.txt`

2. Entra a [Streamlit Cloud](https://streamlit.io/cloud) y crea una nueva app.

3. Selecciona el repositorio y configura:
   - **Main file**: `app_comisiones.py`

4. Haz clic en **Deploy** y ¡listo!

---

## 📄 Reglas de Comisión Aplicadas

- **Venta no compartida**: 4% para la oficina (si captador = colocador)
- **Venta compartida**: 2% para cada oficina
- **Alquiler no compartido**: 100% para la oficina
- **Alquiler compartido**: 50% para cada oficina

---

## 🧠 Autor

Desarrollado con 💡 por inteligencia artificial para Century 21.
