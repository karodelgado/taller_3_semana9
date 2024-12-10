import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
import os
import time

# Título de la aplicación
st.title("Análisis de Pagos - Base de Datos Sakila")
st.header("Visualización de Datos Filtrados")

# Obtener la carpeta actual del archivo
carpeta = os.path.dirname(__file__)
st.write('Carpeta actual:', carpeta)

# Construir la ruta al archivo de la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'data', 'sakila_master.db')
if os.path.exists(db_path):
    print(f"Archivo encontrado: {db_path}")
else:
    print(f"Archivo no encontrado en la ruta: {db_path}")
st.write('Ruta al archivo de la base de datos:', db_path)

# Verificar si el archivo de la base de datos existe
if not os.path.exists(db_path):
    st.error(f"El archivo de la base de datos no se encuentra en la ruta: {db_path}")
else:
    # Intentar conectar con la base de datos
    try:
        conn = sqlite3.connect(db_path)
        st.write("Conexión a la base de datos exitosa.")
    except sqlite3.Error as e:
        st.error(f"Error al conectar con la base de datos: {e}")

    # Función para cargar datos desde la base de datos
    def cargar_datos():
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

    # Cargar datos desde las consultas
    datos_pago, datos_rentas, datos_categoria = cargar_datos()

    # Renombrar columnas y verificar si los datos no están vacíos
    if not datos_pago.empty:
        datos_pago = datos_pago.rename(columns={
            'amount': 'monto',
            'payment_date': 'fecha_pago',
            'staff_id': 'empleado_id',
            'customer_id': 'cliente_id'
        })
        datos_pago['fecha_pago'] = pd.to_datetime(datos_pago['fecha_pago'])

    if not datos_categoria.empty:
        datos_categoria = datos_categoria.rename(columns={
            'tienda': 'tienda_id',
            'categoria': 'categorias',
            'cantidad_rentas': 'total_rentas'
        })

    # Sidebar para filtros
    st.sidebar.header('Filtros de Pagos')

    if not datos_pago.empty:
        # Filtro por rango de montos
        rango_monto = st.sidebar.slider(
            'Rango de montos',
            min_value=float(datos_pago['monto'].min()),
            max_value=float(datos_pago['monto'].max()),
            value=(float(datos_pago['monto'].min()), float(datos_pago['monto'].max()))
        )

        # Filtro por rango de fechas
        fecha_min = datos_pago['fecha_pago'].min().date()
        fecha_max = datos_pago['fecha_pago'].max().date()
        rango_fechas = st.sidebar.date_input(
            'Rango de fechas',
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )

        # Filtro por empleado
        empleado_seleccionado = st.sidebar.selectbox(
            'Empleado',
            options=['Todos'] + datos_pago['empleado_id'].astype(str).unique().tolist()
        )

        # Aplicar filtros
        mask = (
            (datos_pago['monto'] >= rango_monto[0]) &
            (datos_pago['monto'] <= rango_monto[1]) &
            (datos_pago['fecha_pago'].dt.date >= rango_fechas[0]) &
            (datos_pago['fecha_pago'].dt.date <= rango_fechas[1])
        )

        if empleado_seleccionado != 'Todos':
            mask &= datos_pago['empleado_id'] == int(empleado_seleccionado)

        datos_filtrados = datos_pago[mask]

        # Métricas
        st.subheader('Métricas de Interés')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Total de registros', len(datos_filtrados))
        with col2:
            st.metric('Monto promedio', f"${datos_filtrados['monto'].mean():.2f}" if len(datos_filtrados) > 0 else "$0.00")
        with col3:
            st.metric('Monto total', f"${datos_filtrados['monto'].sum():.2f}")

        # Mostrar datos filtrados
        st.subheader('Datos Filtrados')
        st.dataframe(datos_filtrados)

        # Visualización
        st.subheader('Relación Monto/Fecha de Pago')
        fig = px.scatter(
            datos_filtrados,
            x='fecha_pago',
            y='monto',
            color='empleado_id',
            hover_data=['cliente_id']
        )
        st.plotly_chart(fig)

    if not datos_categoria.empty:
        # Visualización adicional por categorías
        st.subheader('Rentas por Categorías y Tienda')
        fig_categorias = px.bar(
            datos_categoria,
            x='categorias',
            y='total_rentas',
            color='tienda_id',
            barmode='group',
            title='Total de Rentas por Categorías y Tienda'
        )
        st.plotly_chart(fig_categorias)
