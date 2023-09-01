import streamlit as st
from utils import init_connection
st.set_page_config(page_title="Diamante Agua Pura", page_icon="💎")

try:
    user = st.experimental_user
    if "name" in user.keys():
        user_name = user["name"]
        st.toast(f"Hola {user_name}! 👋")
    else:
        email = user["email"]
        st.toast(f"{email} ha ingresado! 👋")
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




