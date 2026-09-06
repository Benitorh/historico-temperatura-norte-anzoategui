import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from pathlib import Path

# 1. Configuración de la página del Dashboard (Layout Profesional Ancho)
st.set_page_config(
    page_title="Dashboard de Temperaturas Mínimas ERA5",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal de la aplicación con logo y estilo limpio
st.title("🌡️ Dashboard Climático: Análisis de Temperaturas Mínimas ERA5")
st.markdown(
    """
    Este dashboard interactivo permite explorar **20 años de datos de temperatura mínima diaria** (ERA5) 
    para la región de análisis. Utiliza los filtros en la barra lateral para recortar la serie temporal, 
    analizar estaciones específicas del año o subir tu propia base de datos de manera dinámica.
    """
)
st.markdown("---")

# 2. Carga y Preparación de Datos (Pandas) con Caché y Soporte Dinámico (Requisito 5)
@st.cache_data
def cargar_datos(file_obj):
    def normalizar_nombre(col):
        texto = str(col).strip().lower()
        for reemplazo in [" ", "-", "_", "/", "(", ")", ".", ":"]:
            texto = texto.replace(reemplazo, "")
        return texto

    def detectar_columna_fecha(df_raw):
        for col in df_raw.columns:
            nombre = normalizar_nombre(col)
            if any(palabra in nombre for palabra in [
                "date", "fecha", "time", "timestamp", "datetime", "fecha_hora",
                "unnamed0", "unnamed", "index"
            ]):
                return col

        for col in df_raw.columns:
            try:
                serie = pd.to_datetime(df_raw[col], errors="coerce")
                validos = serie.notna().sum()
                if validos > max(2, len(df_raw) * 0.05):
                    return col
            except Exception:
                continue

        for col in df_raw.columns:
            serie = df_raw[col].astype(str).str.strip()
            if serie.str.contains(r"^\d{4}-\d{2}-\d{2}", na=False).any():
                return col

        return None

    def detectar_columna_temperatura(df_raw):
        for col in df_raw.columns:
            nombre = normalizar_nombre(col)
            if any(palabra in nombre for palabra in [
                "temp", "tmin", "tmax", "tmean", "temperatura", "minimum", "minima",
                "valor", "mínima", "averagepolygon"
            ]):
                return col

        num_cols = df_raw.select_dtypes(include=["number"]).columns.tolist()
        num_cols = [
            col for col in num_cols
            if not any(palabra in normalizar_nombre(col) for palabra in [
                "id", "year", "month", "año", "mes", "unnamed", "date", "fecha", "time", "timestamp"
            ])
        ]
        if not num_cols:
            return None

        # Si existen varias columnas numéricas, se evita elegir una de resumen (promedio, índice, etc.)
        prioridad = []
        for col in num_cols:
            nombre = normalizar_nombre(col)
            peso = 0
            if "temp" in nombre:
                peso += 5
            if "min" in nombre or "mín" in nombre:
                peso += 4
            if "mean" in nombre or "average" in nombre:
                peso -= 2
            prioridad.append((peso, col))

        prioridad.sort(reverse=True)
        return prioridad[0][1]

    if file_obj is not None:
        try:
            if file_obj.name.endswith('.csv'):
                df_raw = pd.read_csv(file_obj)
            else:
                df_raw = pd.read_excel(file_obj)
        except Exception as e:
            st.error(f"Error al leer el archivo subido: {e}")
            return None
    else:
        try:
            base_dir = Path(__file__).resolve().parent
            ruta_datos = base_dir / 'temperatura-minima-ERA-5-a-20-anos.csv'

            if not ruta_datos.exists():
                raise FileNotFoundError(f"No se encontró el archivo de datos en: {ruta_datos}")

            df_raw = pd.read_csv(ruta_datos)
        except Exception as e:
            st.error(f"Error al cargar el archivo de datos por defecto: {e}")
            return None

    if df_raw is None or df_raw.empty or df_raw.shape[1] == 0:
        st.error("El archivo cargado no contiene columnas válidas para analizar.")
        return None

    col_fecha = detectar_columna_fecha(df_raw)
    col_temp = detectar_columna_temperatura(df_raw)

    if col_fecha is None or col_temp is None:
        st.error("No se pudo identificar automáticamente una columna de fecha y otra de temperatura en el archivo cargado.")
        return None

    df = df_raw[[col_fecha, col_temp]].copy()
    df.columns = ["Fecha", "Temperatura Mínima (°C)"]

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Temperatura Mínima (°C)"] = pd.to_numeric(df["Temperatura Mínima (°C)"], errors="coerce")
    df = df.dropna(subset=["Fecha", "Temperatura Mínima (°C)"]).copy()
    df = df.sort_values("Fecha").reset_index(drop=True)

    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month

    meses_es = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    df['Mes_Nombre'] = df['Mes'].map(meses_es)

    def obtener_estacion(mes):
        if mes in [12, 1, 2]:
            return 'Verano'
        elif mes in [3, 4, 5]:
            return 'Otoño'
        elif mes in [6, 7, 8]:
            return 'Invierno'
        elif mes in [9, 10, 11]:
            return 'Primavera'
        return 'Sin dato'

    df['Estación'] = df['Mes'].apply(obtener_estacion)

    columnas_finales = ["Fecha", "Temperatura Mínima (°C)", "Año", "Mes", "Mes_Nombre", "Estación"]
    return df[[col for col in columnas_finales if col in df.columns]]

# 3. Controladores y Filtros en la Barra Lateral (Sidebar) (Requisito 4 - Mínimo 2 filtros dinámicos)
st.sidebar.header("🔍 Carga de Datos y Filtros")

# Requisito 5: Carga dinámica de archivos (CSV o XLSX)
archivo_subido = st.sidebar.file_uploader(
    "📥 Sube tu base de datos (.csv o .xlsx):",
    type=["csv", "xlsx"],
    help="Si subes un archivo, el dashboard se adaptará automáticamente a tus datos."
)

# Cargar el dataframe
df = cargar_datos(archivo_subido)

if df is not None:
    # FILTRO DINÁMICO 1: Rango de Fechas
    min_date = df["Fecha"].min().date()
    max_date = df["Fecha"].max().date()
    
    fechas_seleccionadas = st.sidebar.date_input(
        "📅 Rango de Fechas:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Selecciona la fecha de inicio y fin para acotar el análisis."
    )
    
    # Filtrado robusto según el rango de fechas seleccionado
    if isinstance(fechas_seleccionadas, tuple) and len(fechas_seleccionadas) == 2:
        start_date, end_date = fechas_seleccionadas
        df_filtrado = df[(df["Fecha"].dt.date >= start_date) & (df["Fecha"].dt.date <= end_date)]
    else:
        df_filtrado = df
        
    def normalizar_estacion(valor):
        if pd.isna(valor):
            return ""
        texto = str(valor).strip()
        texto = texto.replace("Temporada de sequía", "Verano")
        texto = texto.replace("Temporada de sequia", "Verano")
        texto = texto.replace("Temporada de lluvias", "Invierno")
        texto = texto.lower()

        if "verano" in texto:
            return "Verano"
        if "otoño" in texto or "otono" in texto:
            return "Otoño"
        if "invierno" in texto:
            return "Invierno"
        if "primavera" in texto:
            return "Primavera"
        return texto.title() if texto else ""

    # FILTRO DINÁMICO 2: Estaciones del Año (Multi-selección)
    estaciones_validas = df["Estación"].map(normalizar_estacion)
    estaciones_validas = estaciones_validas[estaciones_validas != ""]
    estaciones_disponibles = sorted(estaciones_validas.unique())

    if not estaciones_disponibles:
        estaciones_disponibles = ["Sin dato"]

    estaciones_seleccionadas = st.sidebar.multiselect(
        "🍂 Estaciones del Año:",
        options=estaciones_disponibles,
        default=estaciones_disponibles,
        help="Filtra los registros según las estaciones climáticas."
    )

    if estaciones_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado["Estación"].map(normalizar_estacion).isin(estaciones_seleccionadas)]
    
    # FILTRO DINÁMICO 3: Deslizador de Rango de Temperatura
    min_temp = float(df["Temperatura Mínima (°C)"].min())
    max_temp = float(df["Temperatura Mínima (°C)"].max())
    rango_temperatura = st.sidebar.slider(
        "🌡️ Rango de Temperatura (°C):",
        min_value=min_temp,
        max_value=max_temp,
        value=(min_temp, max_temp),
        step=0.1,
        help="Recorta los datos a un umbral térmico específico."
    )
    df_filtrado = df_filtrado[
        (df_filtrado["Temperatura Mínima (°C)"] >= rango_temperatura[0]) & 
        (df_filtrado["Temperatura Mínima (°C)"] <= rango_temperatura[1])
    ]

    # 4. Sección de Métricas Clave (KPIs) (Requisito 2 - Al menos 6 KPIs claros)
    st.markdown("### 📈 Métricas Clave (De un vistazo)")
    
    # Primera Fila de KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        avg_temp = df_filtrado["Temperatura Mínima (°C)"].mean()
        st.metric(
            label="🌡️ Temp. Mínima Promedio", 
            value=f"{avg_temp:.2f} °C",
            help="Promedio general de todas las temperaturas mínimas registradas."
        )
        
    with kpi2:
        abs_min = df_filtrado["Temperatura Mínima (°C)"].min()
        st.metric(
            label="❄️ Temp. Mínima Absoluta", 
            value=f"{abs_min:.2f} °C",
            help="La temperatura más fría registrada en la serie filtrada (noche más helada)."
        )
        
    with kpi3:
        abs_max = df_filtrado["Temperatura Mínima (°C)"].max()
        st.metric(
            label="🔥 Mínima Más Elevada", 
            value=f"{abs_max:.2f} °C",
            help="La temperatura mínima más alta de la serie (noche más cálida)."
        )
        
    with kpi4:
        rango_termico = abs_max - abs_min
        st.metric(
            label="↔️ Amplitud Térmica", 
            value=f"{rango_termico:.2f} °C",
            help="Diferencia entre la noche más fría y la noche más cálida de la selección."
        )
        
    # Segunda Fila de KPIs
    kpi5, kpi6, kpi7 = st.columns(3)
    
    with kpi5:
        total_dias = df_filtrado.shape[0]
        st.metric(
            label="📅 Total de Días Analizados", 
            value=f"{total_dias:,}",
            help="Número total de registros diarios que cumplen con los filtros."
        )
        
    with kpi6:
        # Noches muy cálidas (Tmin > 26.0 °C)
        umbral_calido = 26.0
        cant_calidas = (df_filtrado["Temperatura Mínima (°C)"] > umbral_calido).sum()
        pct_calidas = (df_filtrado["Temperatura Mínima (°C)"] > umbral_calido).mean() * 100
        st.metric(
            label="🔥 Noches Cálidas (>26°C)", 
            value=f"{cant_calidas} ({pct_calidas:.1f}%)",
            help="Días y porcentaje cuya temperatura mínima superó los 26°C."
        )
        
    with kpi7:
        # Noches frescas (Tmin < 24.5 °C)
        umbral_fresco = 24.5
        cant_frescas = (df_filtrado["Temperatura Mínima (°C)"] < umbral_fresco).sum()
        pct_frescas = (df_filtrado["Temperatura Mínima (°C)"] < umbral_fresco).mean() * 100
        st.metric(
            label="🍃 Noches Frescas (<24.5°C)", 
            value=f"{cant_frescas} ({pct_frescas:.1f}%)",
            help="Días y porcentaje cuya temperatura mínima estuvo por debajo de 24.5°C."
        )
        
    st.markdown("---")

    # 5. Sección de Análisis Visual (Plotly Express) (Requisito 3 - Al menos 4 gráficos interactivos)
    st.markdown("### 📊 Gráficos de Análisis Climático Interactivo")
    
    # Organización profesional en pestañas (Tabs)
    tab_linea, tab_climatologia, tab_cajas, tab_distribucion = st.tabs([
        "📅 Evolución Temporal", 
        "📊 Climatología Estacional", 
        "📦 Variabilidad Anual (BoxPlot)", 
        "📈 Distribución de Frecuencias"
    ])
    
    # GRÁFICO 1: Evolución Temporal con Agrupamiento Dinámico
    with tab_linea:
        st.markdown("#### Serie Temporal de Temperaturas Mínimas")
        
        # Selector de agrupación temporal interactivo
        unidad_tiempo = st.selectbox(
            "Selecciona la escala temporal de agrupación:",
            options=["Día", "Semana", "Mes", "Año"],
            key="time_scale_select_box"
        )
        
        mapa_frecuencias = {
            "Día": "D",
            "Semana": "W",
            "Mes": "ME",
            "Año": "YE"
        }
        freq_sel = mapa_frecuencias[unidad_tiempo]
        
        # Agrupación con pd.Grouper
        df_grouped = (
            df_filtrado.groupby(pd.Grouper(key="Fecha", freq=freq_sel))["Temperatura Mínima (°C)"]
            .mean()
            .reset_index()
        )
        
        fig_linea = px.line(
            df_grouped,
            x="Fecha",
            y="Temperatura Mínima (°C)",
            markers=True if unidad_tiempo in ["Mes", "Año"] else False,
            title=f"Evolución Temporal de la Temperatura Mínima (Promedio por {unidad_tiempo})",
            labels={"Fecha": "Fecha", "Temperatura Mínima (°C)": "Temperatura Mínima Promedio (°C)"},
            color_discrete_sequence=["#1f77b4"]
        )
        fig_linea.update_layout(hovermode="x unified")
        st.plotly_chart(fig_linea, width="stretch")
        
    # GRÁFICO 2: Climatología Mensual Promedio (Ciclo Estacional Anual)
    with tab_climatologia:
        st.markdown("#### Climatología Mensual Promedio (Ciclo Anual)")
        orden_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Agrupar por mes y ordenar correctamente de Enero a Diciembre
        df_mes = (
            df_filtrado.groupby("Mes_Nombre")["Temperatura Mínima (°C)"]
            .mean()
            .reindex(orden_meses)
            .reset_index()
        )
        
        fig_barras = px.bar(
            df_mes,
            x="Mes_Nombre",
            y="Temperatura Mínima (°C)",
            color="Temperatura Mínima (°C)",
            color_continuous_scale="RdBu",
            title="Ciclo Climatológico Mensual Promedio",
            labels={"Mes_Nombre": "Mes", "Temperatura Mínima (°C)": "Temp. Mínima Promedio (°C)"}
        )
        st.plotly_chart(fig_barras, width="stretch")
        
    # GRÁFICO 3: Box Plot Interanual (Variabilidad y Dispersión por Año)
    with tab_cajas:
        st.markdown("#### Distribución Térmica Interanual")
        
        fig_caja = px.box(
            df_filtrado.sort_values("Año"),
            x="Año",
            y="Temperatura Mínima (°C)",
            color="Año",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title="Variabilidad y Rango de Temperatura Mínima por Año",
            labels={"Año": "Año", "Temperatura Mínima (°C)": "Temperatura Mínima (°C)"}
        )
        st.plotly_chart(fig_caja, width="stretch")
        
    # GRÁFICO 4: Histograma de Distribución y Frecuencias
    with tab_distribucion:
        st.markdown("#### Histograma de Frecuencias de Temperatura Mínima")
        
        fig_hist = px.histogram(
            df_filtrado,
            x="Temperatura Mínima (°C)",
            nbins=40,
            marginal="box",  # Añade un box plot marginal para análisis estadístico completo
            color_discrete_sequence=["#00bbf9"],
            title="Distribución de Frecuencia de Días Registrados",
            labels={"count": "Cantidad de Días", "Temperatura Mínima (°C)": "Temperatura Mínima (°C)"}
        )
        st.plotly_chart(fig_hist, width="stretch")
        
    st.markdown("---")

    # 6. Visualización Interactiva del DataFrame y Exportación a CSV (Requisitos 6 y 7)
    st.markdown("### 📥 Visualización y Exportación de Datos")
    
    col_exp1, col_exp2 = st.columns([3, 1])
    
    with col_exp1:
        st.write("Explora la tabla completa de los datos filtrados en tiempo real o expórtala directamente en formato CSV.")
        
    with col_exp2:
        # Generar CSV para descarga (Requisito 7)
        csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV Filtrado",
            data=csv_data,
            file_name="temperaturas_filtradas_era5.csv",
            mime="text/csv",
            width="stretch"
        )
        
    # Requisito 6: Objeto interactivo para visualizar la tabla de datos completa
    expander_tabla = st.expander("🔍 Ver Tabla de Datos Filtrada Completa", expanded=False)
    with expander_tabla:
        st.dataframe(df_filtrado, width="stretch")

else:
    st.error("No se pudieron cargar los datos. Por favor, verifica el formato de tu archivo subido.")
