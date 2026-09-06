# Dashboard de Análisis de Temperaturas Mínimas (ERA5) en Zona Metropolitana del Estado Anzoategui  durante ek Periodo 2006-2026🌦️
Este proyecto consiste en un **Dashboard Climático Interactivo** de nivel profesional diseñado y desarrollado con **Python**, **Streamlit**, **Pandas** y **Plotly**. La aplicación web permite explorar y analizar un conjunto de datos histórico de **20 años de registros diarios** de temperaturas mínimas (2006-2026) para la zona metropolitana del Estado Anzoategui en Venezuela, obtenidos a partir del reanálisis **ERA5-Land** de la Unión Europea / Copernicus.

El dashboard ha sido desarrollado cumpliendo con la totalidad de los requisitos del **Proyecto Final** de la formación en Análisis de Datos.

---

## 🔗 Fuente de Datos (ERA5 desde Climate Engine de Google)

Los datos climáticos utilizados como base provienen del reanálisis global de alta resolución **ERA5-Land**, procesados mediante Google Earth Engine (GEE).
* **Enlace de Descarga en Climate Engine (Dataset de Referencia):** [Fuente: ERA5-Land Temperature de Engine Climate en Google ](https://www.climateengine.org) *(Nota: Puedes sustituir este enlace por el enlace público específico de tu dataset en Kaggle).*

---

## ⚡ Requisitos Técnicos Implementados (Rúbrica del Proyecto)

La aplicación web cubre rigurosamente los **7 puntos obligatorios** exigidos para la entrega:

1. **Fuente de Datos (Kaggle):** Integración del dataset diario de temperaturas mínimas de 20 años de ERA5.
2. **Siete (7) Métricas Clave / KPIs (Rúbrica exige mín. 6):**
   * **Tª Mínima Promedio (°C):** Promedio de las temperaturas mínimas de la selección.
   * **Tª Mínima Absoluta (°C):** La noche más fría registrada en el periodo filtrado.
   * **Tª Mínima Más Alta (°C):** La noche menos fría registrada en el periodo filtrado.
   * **Amplitud Térmica de Mínimas (°C):** El rango de variación extrema de las mínimas.
   * **Total de Días Analizados:** Cantidad total de registros que cumplen los filtros.
   * **Noches Tropicales / Cálidas:** Conteo y porcentaje de noches con temperatura mínima $> 26.0\text{°C}$.
   * **Noches Frescas / Frías:** Conteo y porcentaje de noches con temperatura mínima $< 24.5\text{°C}$.
3. **Cuatro (4) Gráficos Interactivos con Plotly (Rúbrica exige mín. 4):**
   * **📅 Evolución Temporal Dinámica:** Gráfico de líneas interactivo con selector de escala de tiempo dinámica (Día, Semana, Mes, Año) utilizando agrupaciones temporales inteligentes con `pd.Grouper`.
   * **📊 Ciclo Climatológico Estacional:** Gráfico de barras que representa la temperatura promedio de cada uno de los 12 meses (Enero a Diciembre) para comprender el ciclo anual.
   * **📦 Variabilidad Interanual (Boxplot):** Diagrama de caja interactivo por año para evaluar la dispersión de los datos, medianas y la presencia de temperaturas mínimas anómalas.
   * **📈 Distribución Estadística (Histograma):** Gráfico de distribución de frecuencias con una representación de caja marginal (*rug/box*) para evaluar sesgos en la climatología de la zona.
4. **Filtros Dinámicos (Rúbrica exige mín. 2):**
   * **Rango de Fechas:** Filtro de calendario (`st.sidebar.date_input`) para seleccionar ventanas de tiempo específicas.
   * **Estaciones del Año:** Selector múltiple de estaciones climatológicas adaptadas al Hemisferio Sur (Verano, Otoño, Invierno, Primavera).
   * **Umbral de Temperatura:** Deslizador (*slider*) interactivo para acotar el rango de análisis a valores térmicos concretos.
5. **Carga Dinámica de Archivos (Requisito 5):**
   * El dashboard cuenta con un componente `st.sidebar.file_uploader` que permite al usuario **subir su propio archivo de datos (CSV o XLSX)**.
   * Cuenta con un **algoritmo de detección heurística** que identifica de forma automática qué columna contiene fechas y cuál contiene valores de temperatura para adaptar la interfaz dinámicamente al nuevo archivo.
6. **Visualización de Tabla Interactiva (Requisito 6):**
   * Un visor expandible (`st.expander`) que renderiza la tabla de datos filtrada completa mediante `st.dataframe`, permitiendo búsquedas y ordenamientos en tiempo real.
7. **Exportación de Datos Filtrados (Requisito 7):**
   * Botón de descarga integrado (`st.download_button`) que genera de forma automática un archivo `.csv` con los datos que han sido filtrados en pantalla.

---

## 📂 Estructura del Repositorio

El repositorio está organizado siguiendo las mejores prácticas de desarrollo en Python:

```text
├── main-v2.py            # Código fuente de la aplicación en Streamlit
├── requirements.txt      # Dependencias y librerías del proyecto
├── .gitignore            # Archivos excluidos del control de versiones (ej: .venv, __pycache__)
└── README.md             # Documento de presentación del proyecto (este archivo)
```

---

## 🛠️ Guía de Instalación y Ejecución Local

Para ejecutar este dashboard de forma local en tu computadora, sigue los siguientes pasos desde tu terminal (PowerShell, Bash o Terminal de VS Code):

### 1. Clonar el repositorio y situarse en el directorio
```bash
git clone <URL_DE_TU_REPOSITORIO_DE_GITHUB>
cd <NOMBRE_DEL_REPOSITORIO>
```

### 2. Crear e iniciar el Entorno Virtual (Práctica Obligatoria)
* **En Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
* **En macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
*(Sabrás que está activo porque aparecerá `(.venv)` al inicio de la línea de comandos).*

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación de Streamlit
```bash
streamlit run main-v2.py
```
*Este comando levantará un servidor local y abrirá de forma automática la aplicación web en tu navegador predeterminado (normalmente en `http://localhost:8501`).*

---

## 🌐 Tecnologías Utilizadas

* **Python 3.12**
* **Streamlit** (Creación de la Interfaz Web y Widgets)
* **Pandas** (Procesamiento y Agrupación de Series Temporales Climatológicas)
* **Plotly Express** (Visualizaciones y Gráficos Dinámicos y Reactivos)
* **OpenPyXL** (Ingesta dinámica de archivos de Microsoft Excel)

---

## 👥 Autor
* **Nombre:** [Benito Rodriguez]
* **Curso:** Fundamentos de Programación y Análisis de Datos con Python
* **Fecha de Entrega:** 4 de Septiembre de 2026
