from pathlib import Path
import streamlit as st
import pandas as pd
import sys
import sqlite3
import os

 #Obtener la carpeta actual del archivo
carpeta = os.path.dirname(__file__)

print('Carpeta actual:', carpeta)

# Construir la ruta al archivo de la base de datos
db_path = os.path.join(os.path.dirname(__file__),'..', 'data', 'sakila_master.db')

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

st.dataframe(datos_pago)