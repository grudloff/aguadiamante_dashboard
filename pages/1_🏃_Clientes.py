import streamlit as st
from utils import run_query, run_execute
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
    rut = st.text_input("RUT", autocomplete="Disabled") 
    nombre = st.text_input("Nombre", autocomplete="Disabled")
    direccion = st.text_input("Dirección", autocomplete="Disabled")
    telefono = st.text_input("Teléfono", autocomplete="Disabled")
    email = st.text_input("Email", autocomplete="Disabled")
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
    if direccion[-5:].lower() == "chile":
        st.error("No debes ingresar el país en la dirección")
        return False
    if direccion.count(",") < 1:
        st.error("Debes ingresar la ciudad del cliente, separada por una coma")
        return False
    if telefono == "":
        st.error("Debes ingresar el teléfono del cliente")
        return False
    if telefono[:3] != "+56":
        st.error("Debes ingresar un teléfono válido, que comience con +56")
        return False
    if email != "" and "@" not in email:
        st.error("Debes ingresar un email válido")
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
    try:
        run_execute("INSERT INTO clientes (cliente_rut, nombre, direccion, ciudad, numero_telefono, email, date) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                (rut, nombre, direccion, ciudad, telefono, email, date.today()))
        st.success("Cliente agregado exitosamente")
        run_query.clear()
    except Exception as e:
        st.error("No se pudo agregar el cliente")
        raise e
    time.sleep(1)
    st.success("Redireccionando a la página de ventas...")
    time.sleep(2)
    switch_page("ventas")

# plot clientes table inside a container
with st.expander("Ver Clientes"):
    num_clients = st.number_input("Número máximo de clientes a mostrar", min_value=10, step=10)
    clientes = run_query("""SELECT cliente_rut, nombre, numero_telefono, direccion, ciudad, email, date
                         FROM clientes ORDER BY date DESC LIMIT %s""", (num_clients,))
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
    all_clients = run_query("SELECT cliente_rut, nombre, direccion, ciudad, numero_telefono, email FROM clientes")
    all_clients = pd.DataFrame(all_clients, columns=["RUT", "Nombre", "Dirección", "Ciudad", "Teléfono", "Email"])
    nombre = st.selectbox("Nombre", all_clients["Nombre"].unique(), help="Para modificar nombre, borrar cliente y crearlo nuevamente")
    rut = st.selectbox("RUT", all_clients[all_clients["Nombre"]==nombre]["RUT"])
    try:
        all_clients_rut = all_clients[all_clients["RUT"]==rut].iloc[0]
        disabled_flag = False
    except IndexError:
        all_clients_rut = {"Nombre": "", "Dirección": "", "Ciudad": "", "Teléfono": "", "Email": ""}
        disabled_flag = True
    direccion = st.text_input("Dirección", all_clients_rut["Dirección"],
                              autocomplete="Disabled" ,disabled=disabled_flag)
    ciudad = st.text_input("Ciudad", all_clients_rut["Ciudad"],
                           autocomplete="Disabled" ,disabled=disabled_flag)
    telefono = st.text_input("Teléfono", all_clients_rut["Teléfono"],
                             autocomplete="Disabled" ,disabled=disabled_flag)
    email = st.text_input("Email", all_clients_rut["Email"],
                          autocomplete="Disabled" ,disabled=disabled_flag)
    submit = st.button("Modificar", use_container_width=True)
    if submit:
        try:
            run_execute("UPDATE clientes SET nombre = %s, direccion = %s, ciudad = %s, numero_telefono = %s, email = %s WHERE cliente_rut = %s", 
                    (nombre, direccion, ciudad, telefono, email, rut))
            st.success("Cliente modificado exitosamente")
            run_query.clear()
        except Exception as e:
            st.error("No se pudo modificar el cliente")
            raise e

# option to delete a client
with st.expander("Eliminar Cliente"):
    st.write("## Eliminar Cliente")
    nombre = st.selectbox("Nombre", clientes["Nombre"].unique(), key="nombre_eliminar")
    rut = st.selectbox("RUT", clientes[clientes["Nombre"]==nombre]["RUT"], key="rut_eliminar",
                       help = "Selección de rut, en caso de que exista más de un cliente con el mismo nombre")

    st.warning("Esta acción no se puede deshacer")
    submit = st.button("Eliminar", use_container_width=True, key="button_eliminar", type="primary")

    if submit:
        try:
            run_execute("DELETE FROM clientes WHERE nombre = %s", (nombre,))
            st.success("Cliente eliminado exitosamente")
            run_query.clear()
        except Exception as e:
            st.error("No se pudo eliminar el cliente")
            st.error("Posiblemente el cliente tiene ventas asociadas, en tal caso, elimine primero las ventas asociadas")
            raise e
