import streamlit as st
from utils import init_connection
st.set_page_config(page_title="Diamante Agua Pura", page_icon="💎")

st.write("# Bienvenido al dashboard de Agua Diamante 👋")

st.markdown(
    """
    Este es un dashboard de Agua Diamante, aquí podrás ingresar información de los clientes, productos, ventas, etc.
    así como también podrás visualizar información sobre estos.

    **👈 Seleccionar una opción en el sidebar** 
"""
)

conn = init_connection()




