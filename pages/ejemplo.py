from pathlib import Path
import streamlit as st
import pandas as pd
import sys

# Ajustar la ruta raíz del proyecto
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

# Importar cargar_datos
from utils.cargar_datos import cargar_datos

# Cargar datos desde la base de datos SQLite
path_sakila = cargar_datos('sakila_master', '.db')

# Título de la aplicación
st.title("Base de Datos Sakila")

# Mostrar mensaje de éxito
st.write("¡Base de datos cargada con éxito!")

