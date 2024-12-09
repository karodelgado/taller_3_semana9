
import streamlit as st
import plotly.express as px
import pandas as pd

from utils.cargar_datos import cargar_datos

# Cargar datos desde la función de la utilidad
# Nota: Asegúrate de que `cargar_datos` esté implementado y cargue correctamente la base de datos o datos necesarios.
cargar_datos()

# Título de la aplicación
st.title("Aplicación de Ejemplo")

# Crear DataFrame de ejemplo
df = pd.DataFrame({
    'cuenta_total': [10, 20, 30, 40, 50],
    'tamano_mesa': [1, 2, 3, 4, 5]
})

# Mostrar el DataFrame original
st.subheader("Datos Originales")
st.dataframe(df)

# Filtros en la barra lateral
st.sidebar.header('Filtros')

# Filtro por valor mínimo de cuenta total
filtro_cuenta = st.sidebar.slider(
    'Cuenta total mayor a',
    min_value=int(df['cuenta_total'].min()),
    max_value=int(df['cuenta_total'].max()),
    value=int(df['cuenta_total'].min())
)

# Filtro por tamaño de mesa mínimo
filtro_tamano_mesa = st.sidebar.slider(
    'Tamaño de mesa mayor o igual a',
    min_value=int(df['tamano_mesa'].min()),
    max_value=int(df['tamano_mesa'].max()),
    value=int(df['tamano_mesa'].min())
)

# Aplicar filtros al DataFrame
mascara = df['cuenta_total'] > filtro_cuenta
mascara1 = mascara & (df['tamano_mesa'] >= filtro_tamano_mesa)
df_filtrado = df[mascara1]

# Mostrar filtros aplicados
st.subheader("Filtros Aplicados")
st.write(f"Filtro 'cuenta_total' > {filtro_cuenta}")
st.write(f"Filtro 'tamano_mesa' >= {filtro_tamano_mesa}")

# Mostrar datos filtrados
st.subheader("Datos Filtrados")
st.dataframe(df_filtrado)

# Visualización con Plotly
if not df_filtrado.empty:
    st.subheader("Gráfico Interactivo")
    fig = px.scatter(
        df_filtrado,
        x='tamano_mesa',
        y='cuenta_total',
        title="Relación entre Tamaño de Mesa y Cuenta Total",
        labels={'tamano_mesa': 'Tamaño de Mesa', 'cuenta_total': 'Cuenta Total'},
        hover_data=['cuenta_total']
    )
    st.plotly_chart(fig)
else:
    st.warning("No hay datos que cumplan con los filtros aplicados.")

