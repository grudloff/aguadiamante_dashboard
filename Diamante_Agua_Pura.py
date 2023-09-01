import streamlit as st
from utils import init_connection
st.set_page_config(page_title="Diamante Agua Pura", page_icon="💎")

try:
    st.toast(repr(st.experimental_user))
    user_name = st.experimental_user["name"]
    st.toast(f"Hello {user_name}! 👋")
except KeyError:
    st.toast("Hello! 👋")

st.write("# Bienvenido al dashboard de Agua Diamante 👋")

st.markdown(
    """
    Este es un dashboard de Agua Diamante, aquí podrás ingresar información de los clientes, productos, ventas, etc.
    así como también podrás visualizar información sobre estos.

    **👈 Seleccionar una opción en el sidebar**
"""
)

st.info("Para abrir el sidebar seleccionar el icono de la esquina superior izquierda", icon="ℹ️")


conn = init_connection()




