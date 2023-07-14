import streamlit as st
from utils import init_connection, run_query, run_execute
from datetime import date
import pandas as pd

st.set_page_config(page_title="Ventas", page_icon="💰")

nombre = st.session_state.get("nombre", None)

st.session_state["valid_form"] = st.session_state.get("valid_form", True)

nombre_rut = dict(run_query("SELECT nombre, cliente_rut FROM clientes"))
productos_nombre_id = dict(run_query("SELECT nombre, producto_id FROM productos"))

def valid_form():
    producto = st.session_state["Producto"]
    return not (producto == [])
    
def reset_form():
    producto = st.session_state["Producto"]
    del st.session_state["Nombre"]
    del st.session_state["Fecha de pago"]
    for producto in productos:
        del st.session_state["Cantidad " + producto]
    del st.session_state["Producto"]
    # NOTE: this is a hack to reset the multiselect as for
    # some reason it doesn't work with just deleting it from session_state
    st.session_state["Producto"] = []
    st.experimental_rerun()

st.write("# Ventas")

# This is a form to add a new order
# NOTE: I don't use st.form because I need the products list to be updated
# so that the user can then select the quantity for selected products.
with st.container():

    st.write("## Ingrese los datos de la venta")
    nombres = list(nombre_rut.keys())
    index = nombres.index(nombre) if nombre in nombres else 0
    nombre_ingreso_venta = st.selectbox("Nombre", nombres, index=index, key="Nombre")
    rut = nombre_rut.get(nombre_ingreso_venta)
    producto_idx = []
    cantidades = []
    with st.expander("Cuenta por pagar?"):
        fecha_pago = st.date_input("Fecha de pago", min_value=date.today(), key="Fecha de pago",
                               help="Fecha en la que a más tardar se realizara el pago")
        if fecha_pago == date.today():
            fecha_pago = None
    productos = st.multiselect("Producto", productos_nombre_id.keys(), key="Producto")
    for producto in productos:
        cantidad = st.number_input("Cantidad " + producto, min_value=1, max_value=50, value=1, key="Cantidad " + producto)
        producto_idx.append(productos_nombre_id[producto])
        cantidades.append(cantidad)

    submitted = st.button("Agregar", use_container_width=True)

if submitted and not valid_form():
        st.error("Debes seleccionar al menos un producto!")
if submitted and valid_form():
    producto_idx = [productos_nombre_id[producto] for producto in productos]
    # Get the last order from the same client
    try:
        res = run_query("SELECT pedido_id FROM pedidos WHERE cliente_rut = %s ORDER BY pedido_id DESC LIMIT 1", (rut,))
        if res == []:
            pedido_anterior_id = None
        else:
            pedido_anterior_id = res[0]

        # Insert the new order
        conn = st.session_state.get("conn", init_connection())
        with conn.cursor() as cur:
            # Insert the new order and return the id
            cur.execute(
                "INSERT INTO pedidos (cliente_rut, fecha_pedido, fecha_pago, pedido_anterior_id) VALUES (%s, %s, %s, %s) RETURNING pedido_id",
                (rut, date.today(), fecha_pago, pedido_anterior_id),    
            )
            conn.commit()
            # get the id of the inserted order
            pedido_id = cur.fetchone()[0]
        # Insert the items of the order
        for producto_id, cantidad in zip(producto_idx, cantidades):
            run_execute("INSERT INTO items_pedido (pedido_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                        (pedido_id, producto_id, cantidad))
        # pop default nombre
        if "nombre" in st.session_state:
            st.session_state.pop("nombre")
        st.success("Venta agregada exitosamente")
        run_query.clear()
        reset_form()
    except Exception as e:
        st.error("Error al agregar venta")
        st.error(e)

with st.expander("Ver ultimas ventas"):
    num_pedidos = st.number_input("Número máximo de pedidos a mostrar", min_value=10, step=10)
    # pedidos = run_query("SELECT * FROM pedidos LIMIT %s", (num_pedidos,))
    pedidos = run_query("SELECT * FROM pedidos ORDER BY pedido_id DESC LIMIT %s", (num_pedidos,))
    # convert to dataframe
    header = ["Pedido ID", "RUT", "Fecha Pedido", "Fecha Pago", "Pedido Anterior ID"]
    pedidos = pd.DataFrame(pedidos, columns=header)
    atributes = st.multiselect("Atributos a mostrar", header, default=["Pedido ID", "RUT", "Fecha Pedido"])
    st.write("## Tabla Pedidos")
    st.table(pedidos[atributes])
    if st.button("Recargar", use_container_width=True):
        run_query.clear()

# Visualize the items of a selected order
with st.expander("Ver items de un pedido"):
    pedido_id = st.selectbox("Pedido ID", pedidos["Pedido ID"], key="pedido_id")
    # get the items of the selected order
    items = run_query("SELECT * FROM items_pedido WHERE pedido_id = %s", (pedido_id,))
    # convert to dataframe
    header = ["Item Pedido ID", "Pedido ID", "Producto ID", "Cantidad"]
    items = pd.DataFrame(items, columns=header)
    atributes = st.multiselect("Atributos a mostrar", header, default=["Producto ID", "Cantidad"])
    st.write("## Tabla Items")
    st.table(items[atributes])

with st.expander("Eliminar Venta"):
    pedido_id = st.selectbox("Pedido ID", pedidos["Pedido ID"])
    submit = st.button("Eliminar", use_container_width=True)
    if submit:
        try:
            run_execute("DELETE FROM pedidos WHERE pedido_id = %s", (pedido_id,))
            st.success("Pedido eliminado exitosamente")
            run_query.clear()
        except Exception as e:
            st.error("No se pudo eliminar el pedido")
            st.error(e)
