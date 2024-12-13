from pathlib import Path
import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Sakila Dashboard", layout="wide", page_icon="🎥")

# Obtener la carpeta actual del archivo
carpeta = os.path.dirname(__file__)

# Construir la ruta al archivo de la base de datos
db_path = os.path.join(carpeta, '..', 'data', 'sakila_master.db')

def cargar_datos():
    """
    Carga los datos desde la base de datos SQLite usando consultas SQL predefinidas.

    Returns:
        tuple: Tres DataFrames correspondientes a las consultas de pagos, rentas y categorías.
    """
    try:
        conexion = sqlite3.connect(db_path)

        # Consultas SQL
        consulta_pago = """
        SELECT payment_id, customer_id, staff_id, rental_id, amount, payment_date
        FROM payment;
        """
        consulta_rentas = """
        SELECT rental_id, customer_id, staff_id, inventory_id, rental_date
        FROM rental;
        """
        consulta_categoria = """
        SELECT s.store_id AS tienda, c.name AS categoria, COUNT(r.rental_id) AS cantidad_rentas
        FROM rental r
        JOIN inventory i ON r.inventory_id = i.inventory_id
        JOIN film_category fc ON i.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        JOIN store s ON i.store_id = s.store_id
        GROUP BY s.store_id, c.name;
        """

        # Cargar datos de cada consulta
        datos_pago = pd.read_sql_query(consulta_pago, conexion)
        datos_rentas = pd.read_sql_query(consulta_rentas, conexion)
        datos_categoria = pd.read_sql_query(consulta_categoria, conexion)

        conexion.close()
        return datos_pago, datos_rentas, datos_categoria
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def listar_tablas(nombre_bd):
    """
    Obtiene una lista de las tablas disponibles en la base de datos.

    Args:
        nombre_bd (str): Ruta de la base de datos.

    Returns:
        list: Lista con los nombres de las tablas.
    """
    with sqlite3.connect(nombre_bd) as conn:
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        return pd.read_sql(query, conn)['name'].tolist()

def cargar_tabla(nombre_bd, tabla):
    """
    Carga datos de una tabla específica desde la base de datos SQLite.

    Args:
        nombre_bd (str): Ruta de la base de datos.
        tabla (str): Nombre de la tabla a cargar.

    Returns:
        DataFrame: Datos de la tabla seleccionada.
    """
    with sqlite3.connect(nombre_bd) as conn:
        query = f"SELECT * FROM {tabla};"
        return pd.read_sql(query, conn)

# Cargar datos desde las consultas
datos_pago, datos_rentas, datos_categoria = cargar_datos()

# Encabezado con logo y título
st.sidebar.image("https://static.vecteezy.com/system/resources/previews/046/929/694/original/movie-poster-template-retro-cinema-background-with-an-open-clapper-board-film-reel-and-movie-tickets-illustration-in-flat-style-free-vector.jpg", use_column_width=True)
st.sidebar.title("Filtros del Dashboard")

# Filtros ficticios (modificar según necesidades)
st.sidebar.multiselect("Selecciona Región:", ["Este", "Oeste", "Norte", "Sur"])
st.sidebar.multiselect("Selecciona Ubicación:", ["Urbana", "Rural"])

# Encabezado con logo y título
title_col1, title_col2 = st.columns([1, 8])
with title_col1:
    st.image("https://img.freepik.com/vetores-premium/logotipo-do-rolo-de-filme-vetor-do-logotipo-do-cinema_472355-391.jpg", width=100)
with title_col2:
    st.title("Dashboard de Análisis - Sakila")
st.markdown("---")

# Panel de métricas clave
metric1, metric2, metric3, metric4 = st.columns(4)
with metric1:
    st.metric("Suma de Pagos", f"${datos_pago['amount'].sum():,.2f}")
with metric2:
    st.metric("Promedio de Pagos", f"${datos_pago['amount'].mean():,.2f}")
with metric3:
    st.metric("Pago Máximo", f"${datos_pago['amount'].max():,.2f}")
with metric4:
    st.metric("Pago Mínimo", f"${datos_pago['amount'].min():,.2f}")

# Gráficos organizados
grafico_col1, grafico_col2 = st.columns(2)

# Gráfico de línea para evolución mensual de alquileres
if not datos_rentas.empty:
    datos_rentas['rental_date'] = pd.to_datetime(datos_rentas['rental_date'])
    datos_rentas['mes_anio'] = datos_rentas['rental_date'].dt.to_period('M').astype(str)
    rentas_mensuales = datos_rentas.groupby('mes_anio').size().reset_index(name='cantidad_rentas')

    with grafico_col1:
        st.subheader("Evolución Mensual de Alquileres")
        grafico_linea = px.line(rentas_mensuales, x='mes_anio', y='cantidad_rentas', 
                                title="Evolución de Alquileres Mensuales", 
                                labels={'mes_anio': 'Mes y Año', 'cantidad_rentas': 'Cantidad de Alquileres'}, 
                                markers=True)
        st.plotly_chart(grafico_linea, use_container_width=True)

# Gráfico de pastel para popularidad de categorías de películas
if not datos_categoria.empty:
    with grafico_col2:
        st.subheader("Popularidad de Categorías de Películas")
        grafico_pastel = px.pie(datos_categoria, names='categoria', values='cantidad_rentas', 
                                title="Distribución de Popularidad por Categoría", 
                                labels={'categoria': 'Categoría', 'cantidad_rentas': 'Cantidad de Rentas'})
        st.plotly_chart(grafico_pastel, use_container_width=True)

# Gráficos adicionales organizados
grafico_col3, grafico_col4 = st.columns(2)

# Gráfico de pagos por cliente
with grafico_col3:
    st.subheader("Distribución de Pagos por Cliente")
    grafico_pagos = px.histogram(datos_pago, x='customer_id', y='amount', 
                                 title="Pagos por Cliente", 
                                 labels={'customer_id': 'ID de Cliente', 'amount': 'Monto Pagado'}, 
                                 color_discrete_sequence=['#636EFA'])
    st.plotly_chart(grafico_pagos, use_container_width=True)

# Gráfico de rentas por categoría y tienda
with grafico_col4:
    st.subheader("Cantidad de Rentas por Categoría y Tienda")
    grafico_categorias = px.bar(datos_categoria, x='categoria', y='cantidad_rentas', color='tienda', 
                                barmode='group', 
                                title="Rentas por Categoría y Tienda", 
                                labels={'categoria': 'Categoría', 'cantidad_rentas': 'Cantidad de Rentas', 'tienda': 'ID de Tienda'})
    st.plotly_chart(grafico_categorias, use_container_width=True)

# Selector de tablas y análisis detallado
st.markdown("---")

st.subheader("Exploración de Tablas")
tablas = listar_tablas(db_path)
tabla_seleccionada = st.selectbox("Selecciona una tabla para explorar:", tablas)

if tabla_seleccionada:
    datos = cargar_tabla(db_path, tabla_seleccionada)
    st.dataframe(datos)

    if not datos.empty:
        st.subheader("Estadísticas Básicas")
        st.write(datos.describe())
