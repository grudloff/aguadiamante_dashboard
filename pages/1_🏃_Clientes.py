import streamlit as st
from .utils import run_query, run_execute
from streamlit_extras.switch_page_button import switch_page
from itertools import cycle
import pandas as pd
import time
from datetime import date

st.set_page_config(page_title="Clientes", page_icon="🏃")

def validarRut(rut):
	rut = rut.upper()
	rut = rut.replace("-","")
	rut = rut.replace(".","")
	aux = rut[:-1]
	dv = rut[-1:]
 
	revertido = map(int, reversed(str(aux)))
	factors = cycle(range(2,8))
	s = sum(d * f for d, f in zip(revertido,factors))
	res = (-s)%11
 
	if str(res) == dv:
		return True
	elif dv=="K" and res==10:
		return True
	else:
		return False


# form
with st.form("Cliente"):
    st.write("# Clientes")
    st.write("## Ingrese los datos del cliente")
    rut = st.text_input("RUT") 
    nombre = st.text_input("Nombre")
    direccion = st.text_input("Dirección")
    telefono = st.text_input("Teléfono")
    email = st.text_input("Email")
    submit = st.form_submit_button("Agregar", use_container_width=True)

# Check that the inputs are ok
def validate_form():
    if rut == "":
        st.error("Debes ingresar el RUT del cliente")
        return False
    if nombre == "":
        st.error("Debes ingresar el nombre del cliente")
        return False
    if direccion == "":
        st.error("Debes ingresar la dirección del cliente")
        return False
    if telefono == "":
        st.error("Debes ingresar el teléfono del cliente")
        return False
    if email == "":
        st.error("Debes ingresar el email del cliente")
        return False
    if validarRut(rut) is False:
        st.error("Debes ingresar un RUT válido")
        return False
    return True

if submit and validate_form():
    # remove dots and verifier digit from rut
    rut = rut.strip().replace(".", "")[:-2]
    st.session_state["rut"] = rut
    st.session_state["nombre"] = nombre
    ciudad = direccion.split(",")[-1].strip()
    added_date = date.today()
    try:
        run_execute("INSERT INTO clientes (cliente_rut, nombre, direccion, ciudad, numero_telefono, email, date) VALUES (%s, %s, %s, %s, %s, %s)", 
                (rut, nombre, direccion, ciudad, telefono, email, added_date))
        st.success("Cliente agregado exitosamente")
        run_query.clear()
    except Exception as e:
        st.error("No se pudo agregar el cliente")
        st.error(e)
    time.sleep(1)
    st.success("Redireccionando a la página de ventas...")
    time.sleep(2)
    switch_page("ventas")

# plot clientes table inside a container
with st.expander("Ver Clientes"):
    num_clients = st.number_input("Número máximo de clientes a mostrar", min_value=10, step=10)
    clientes = run_query("SELECT * FROM clientes ORDER BY date DESC LIMIT %s", (num_clients,))
    # convert to dataframe
    header = ["RUT", "Nombre", "Teléfono", "Dirección", "Ciudad", "Email", "Fecha de registro"]
    clientes = pd.DataFrame(clientes, columns=header)
    atributes = st.multiselect("Atributos a mostrar", header, default=header)
    st.write("## Tabla Clientes")
    st.table(clientes[atributes])
    # reload table
    if st.button("Recargar", use_container_width=True):
        run_query.clear()

# modify client
with st.expander("Modificar Cliente"):
    st.write("## Modificar Cliente")
    all_clients = run_query("SELECT * FROM clientes")
    all_clients = pd.DataFrame(all_clients, columns=header)
    nombre = st.selectbox("Nombre", all_clients["Nombre"].unique())
    rut = st.selectbox("RUT", all_clients[all_clients["Nombre"]==nombre]["RUT"])
    all_clients_rut = all_clients[all_clients["RUT"]==rut]
    direccion = st.selectbox("Dirección", all_clients_rut["Dirección"].unique())
    ciudad = st.selectbox("Ciudad", all_clients_rut["Ciudad"].unique())
    telefono = st.selectbox("Teléfono", all_clients_rut["Teléfono"].unique())
    email = st.selectbox("Email", all_clients_rut["Email"].unique())
    submit = st.button("Modificar", use_container_width=True)
    if submit:
        try:
            run_execute("UPDATE clientes SET nombre = %s, direccion = %s, ciudad = %s, numero_telefono = %s, email = %s WHERE rut = %s", 
                    (nombre, direccion, ciudad, telefono, email, rut))
            st.success("Cliente modificado exitosamente")
            run_query.clear()
        except Exception as e:
            st.error("No se pudo modificar el cliente")
            st.error(e)

# option to delete a client
with st.expander("Eliminar Cliente"):
    st.write("## Eliminar Cliente")
    nombre = st.selectbox("Nombre", clientes["Nombre"].unique(), key="nombre_eliminar")
    rut = st.selectbox("RUT", clientes[clientes["Nombre"]==nombre]["RUT"], key="rut_eliminar",
                       help = "Selección de rut, en caso de que exista más de un cliente con el mismo nombre")

    if st.session_state.get("delete_attempt", False):
        double_check = st.slider("¿Estás seguro? Desliza a la derecha para confirmar.", 0, 1, 0)
    else:
        st.warning("Esta acción no se puede deshacer")
        double_check = False
    submit = st.button("Eliminar", use_container_width=True, key="button_eliminar", type="primary")


    if submit:
        # set button_eliminar to True
        st.session_state["delete_attempt"] = True
        if double_check:
            try:
                run_execute("DELETE FROM clientes WHERE nombre = %s", (nombre,))
                st.success("Cliente eliminado exitosamente")
                run_query.clear()
            except Exception as e:
                st.error("No se pudo eliminar el cliente")
                st.error("Posiblemente el cliente tiene ventas asociadas, en tal caso, elimine primero las ventas asociadas")
                st.error(e)
            st.session_state["delete_attempt"] = False
