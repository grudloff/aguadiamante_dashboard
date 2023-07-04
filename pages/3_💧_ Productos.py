import streamlit as st
st.set_page_config(page_title="Productos", page_icon="💧")
from Diamante_Agua_Pura import init_connection, run_execute, run_query
from datetime import date
import pandas as pd

@st.cache_data(ttl=600)
def load_products():
    conn = st.session_state.get("conn", None)
    if conn is None:
        conn = init_connection()
        st.session_state["conn"] = conn
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM productos")
        return cur.fetchall()

@st.cache_data(ttl=600)
def load_stock():

    stock_query = """
    SELECT producto_id, producto_stock
    FROM producto_stock
    WHERE stock_id IN (
        SELECT MAX(stock_id)
        FROM producto_stock
        GROUP BY producto_id
    )
    """

    conn = st.session_state.get("conn", None)
    if conn is None:
        conn = init_connection()
        st.session_state["conn"] = conn
    with conn.cursor() as cur:
        cur.execute(stock_query)
        return cur.fetchall()


def reload_products():
        load_products.clear() # clear cache
        load_stock.clear() # clear cache

product_table = load_products()
stock_table = load_stock()
product_df = pd.DataFrame(product_table, columns=["id", "nombre", "precio"])
stock_df = pd.DataFrame(stock_table, columns=["id", "stock"])
product_df = product_df.merge(stock_df, left_on="id", right_on="id")

st.write("# Productos")
with st.expander("Ver Productos"):
    
    st.table(product_df.drop(columns=["id"]))
    if st.button("Recargar datos", use_container_width=True):
        reload_products()

with st.expander("Agregar Stock"):
    with st.form("Agregar Stock"):
        # st.write("## Ingrese el nombre y cantidad de producto a agregar")
        nombre = st.selectbox("Nombre", product_df["nombre"])
        stock = st.number_input("Cantidad", min_value=0, step=1)
        submit = st.form_submit_button("Agregar", use_container_width=True)
    if submit:
        product_id = product_df[product_df["nombre"] == nombre]["id"].values[0]
        product_id = int(product_id)
        current_stock = product_df[product_df["nombre"] == nombre]["stock"].values[0]
        new_stock = int(current_stock + stock)
        try:
            run_execute("INSERT INTO producto_stock (producto_id, producto_stock) VALUES (%s, %s)", (product_id, new_stock))
            st.success("Stock agregado con éxito!")
        except Exception as e:
            st.error("No se pudo agregar el stock")
            st.error(e)

with st.expander("Agregar Producto"):
    with st.form("Agregar Producto"):
        st.write("## Ingrese los datos del producto")
        nombre = st.text_input("Nombre")
        precio = st.number_input("Precio", min_value=0, step=10)
        stock = st.number_input("Cantidad", min_value=0, step=1)
        submit = st.form_submit_button("Agregar", use_container_width=True)
    if submit:
        try:
            
            st.success("Producto agregado con éxito!")  
            reload_products() # clear cache
        except Exception as e:
            st.error("No se pudo agregar el producto")
            st.error(e)

with st.expander("Modificar Producto"):
    # TODO: Don't use form, to dynamically update the product_df
    with st.form("Modificar Producto"):
        st.write("## Ingrese el nombre y datos de producto a modificar")
        nombre = st.selectbox("Nombre", product_df["nombre"])
        precio = st.number_input("Precio", min_value=0, step=10, value=product_df[product_df["nombre"] == nombre]["precio"].values[0])
        stock = st.number_input("Cantidad", min_value=0, step=1, value=product_df[product_df["nombre"] == nombre]["stock"].values[0])
        submit = st.form_submit_button("Modificar", use_container_width=True)
    if submit:
        product_id = int(product_df[product_df["nombre"] == nombre]["id"].values[0])
        try:
            run_execute("UPDATE productos SET precio = %s WHERE nombre = %s", (precio, nombre))
            run_execute("Insert INTO producto_stock (producto_id, producto_stock) VALUES (%s, %s)", (product_id, stock))
            st.success("Producto modificado con éxito!")
            reload_products() # clear cache
        except Exception as e:
            st.error("No se pudo modificar el producto")
            st.error(e)

with st.expander("Eliminar Producto"):
    with st.form("Eliminar Producto"):
        st.write("## Ingrese el nombre del producto a eliminar")
        nombre = st.selectbox("Nombre", product_df["nombre"])
        submit = st.form_submit_button("Eliminar", use_container_width=True, type="primary")
    if submit:
        try:
            run_execute("DELETE FROM productos WHERE nombre = %s", (nombre,))
            st.success("Producto eliminado con éxito!")
            reload_products() # clear cache
        except Exception as e:
            st.error("No se pudo eliminar el producto")
            st.error(e)
