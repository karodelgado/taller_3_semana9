import sqlite3
import pandas as pd
import os
import streamlit as st
import plotly.express as px

# Función para cargar datos de una base de datos SQLite
def cargar_datos(nombre_bd, extension=".db"):
    """
    Carga datos desde una base de datos SQLite.

    Args:
        nombre_bd (str): Nombre del archivo de la base de datos (sin extensión).
        extension (str): Extensión del archivo de la base de datos.

    Returns:
        dict: Diccionario con las tablas de la base de datos como DataFrames.
    """
    carpeta = os.path.dirname(__file__)  # Carpeta donde está este archivo
    db_path = os.path.join(carpeta, '..', 'data', f'{nombre_bd}{extension}')

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"El archivo {db_path} no existe.")

    # Conectar a la base de datos y cargar las tablas
    with sqlite3.connect(db_path) as conn:
        # Listar todas las tablas
        tablas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        dataframes = {tabla: pd.read_sql(f"SELECT * FROM {tabla}", conn) for tabla in tablas['name']}

    return dataframes

# Función para cargar datos de una tabla
def cargar_tabla(nombre_bd, tabla):
    with sqlite3.connect(nombre_bd) as conn:
        query = f"SELECT * FROM {tabla};"
        return pd.read_sql(query, conn)

# Configurar la aplicación
st.title("Explorador de la base de datos Sakila")

# Ruta de la base de datos
db_path = "data/sakila_master.db"

# Listar tablas disponibles
with sqlite3.connect(db_path) as conn:
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tablas = pd.read_sql(query, conn)['name'].tolist()

# Selector de tablas
tabla_seleccionada = st.selectbox("Selecciona una tabla para explorar:", tablas)

# Mostrar datos de la tabla seleccionada
if tabla_seleccionada:
    st.subheader(f"Datos de la tabla: {tabla_seleccionada}")
    datos = cargar_tabla(db_path, tabla_seleccionada)
    st.dataframe(datos)

    # Mostrar estadísticas básicas
    if not datos.empty:
        st.subheader("Estadísticas de la tabla")
        st.write(datos.describe())

        # Si la tabla tiene columnas numéricas, permitir visualizaciones
        columnas_numericas = datos.select_dtypes(include=['number']).columns.tolist()
        if columnas_numericas:
            st.subheader("Visualización de datos")
            x_col = st.selectbox("Selecciona la columna para el eje X:", columnas_numericas)
            y_col = st.selectbox("Selecciona la columna para el eje Y:", columnas_numericas)
            
            # Crear gráfico de dispersión
            grafico = px.scatter(datos, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
            st.plotly_chart(grafico)

            # Crear gráfico de barras o histogramas si se desea
            tipo_grafico = st.radio("Selecciona tipo de gráfico", ["Dispersión", "Barras", "Histograma"])
            if tipo_grafico == "Barras":
                grafico_barras = px.bar(datos, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                st.plotly_chart(grafico_barras)
            elif tipo_grafico == "Histograma":
                grafico_histograma = px.histogram(datos, x=x_col, title=f"Distribución de {x_col}")
                st.plotly_chart(grafico_histograma)


