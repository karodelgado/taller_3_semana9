from pathlib import Path
import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# Obtener la carpeta actual del archivo
carpeta = os.path.dirname(__file__)
print('Carpeta actual:', carpeta)

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
        SELECT rental_id, customer_id, staff_id, inventory_id
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

# Título del informe
st.title("Informe de Análisis de Alquileres - Base de Datos Sakila")
st.markdown("### Propósito del Informe")
st.markdown("Se busca identificar patrones de alquiler, tendencias de popularidad de películas, y el desempeño de las tiendas para optimizar las decisiones estratégicas de inventario y mejorar la experiencia del cliente.")

# Mostrar el DataFrame de pagos
st.subheader("Pagos Registrados")
st.dataframe(datos_pago)

# Gráfico de pagos por cliente
st.subheader("Distribución de Pagos por Cliente")
grafico_pagos = px.histogram(datos_pago, x='customer_id', y='amount', title="Pagos por Cliente", labels={'customer_id': 'ID de Cliente', 'amount': 'Monto Pagado'}, color_discrete_sequence=['#636EFA'])
st.plotly_chart(grafico_pagos)

# Gráfico de rentas por categoría y tienda
st.subheader("Cantidad de Rentas por Categoría y Tienda")
grafico_categorias = px.bar(datos_categoria, x='categoria', y='cantidad_rentas', color='tienda', barmode='group', title="Rentas por Categoría y Tienda", labels={'categoria': 'Categoría', 'cantidad_rentas': 'Cantidad de Rentas', 'tienda': 'ID de Tienda'})
st.plotly_chart(grafico_categorias)

# Listar tablas disponibles
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

tablas = listar_tablas(db_path)

# Selector de tablas
tabla_seleccionada = st.selectbox("Selecciona una tabla para explorar:", tablas)

# Mostrar datos de la tabla seleccionada
if tabla_seleccionada:
    st.subheader(f"Datos de la tabla: {tabla_seleccionada}")
    datos = cargar_tabla(db_path, tabla_seleccionada)
    st.dataframe(datos)

    # Mostrar estadísticas básicas si la tabla no está vacía
    if not datos.empty:
        st.subheader("Estadísticas de la tabla")
        st.write(datos.describe())

        # Filtrar columnas numéricas
        columnas_numericas = datos.select_dtypes(include=['number']).columns.tolist()
        if columnas_numericas:
            st.subheader("Visualización de datos")

            # Seleccionar columnas para los ejes X e Y
            x_col = st.selectbox("Selecciona la columna para el eje X:", columnas_numericas, key="x_col")
            y_col = st.selectbox("Selecciona la columna para el eje Y:", columnas_numericas, key="y_col")

            # Validar que las columnas seleccionadas sean diferentes
            if x_col != y_col:
                # Selector de tipo de gráfico
                tipo_grafico = st.radio("Selecciona tipo de gráfico:", ["Dispersión", "Barras", "Histograma"])

                # Generar gráfico según la selección
                if tipo_grafico == "Dispersión":
                    grafico = px.scatter(datos, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                elif tipo_grafico == "Barras":
                    grafico = px.bar(datos, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                elif tipo_grafico == "Histograma":
                    grafico = px.histogram(datos, x=x_col, title=f"Distribución de {x_col}")

                # Mostrar el gráfico
                st.plotly_chart(grafico)
            else:
                st.warning("Por favor, selecciona columnas diferentes para X e Y.")
        else:
            st.warning("La tabla seleccionada no tiene columnas numéricas para visualizar.")
    else:
        st.warning("La tabla seleccionada está vacía.")
