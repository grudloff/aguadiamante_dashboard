import streamlit as st
from Diamante_Agua_Pura import run_query, run_execute
from datetime import date
import pandas as pd

st.set_page_config(page_title="Gastos", page_icon="🧾")

# add a new expense to the database
with st.form(key="form"):
    st.write("# Ingrese los datos del gasto")
    tipo_gasto = st.text_input("Tipo de gasto")
    cantidad = st.number_input("Cantidad", value=0)
    fecha = st.date_input("Fecha", value=date.today())
    submitted = st.form_submit_button("Agregar", use_container_width=True)

def validate_form():
    if cantidad == 0:
        st.error("La cantidad debe ser mayor a 0")
        return False
    return True

if submitted and validate_form():
    run_execute("INSERT INTO gastos (tipo_gasto, cantidad, fecha) VALUES (%s, %s, %s)", (tipo_gasto, cantidad, fecha))
    st.success("Gasto agregado con éxito!")
    run_query.clear() # clear cache

# show expenses
with st.expander("Ver Gastos"):
    gastos = run_query("SELECT * FROM gastos ORDER BY fecha DESC")
    gastos_db = pd.DataFrame(gastos, columns=["gasto_id", "tipo_gasto", "cantidad", "fecha"])
    st.table(gastos_db)
    # reload data
    if st.button("Recargar datos", use_container_width=True):
        run_query.clear()

# delete an expense
with st.expander("Eliminar Gasto"):
    with st.form(key="delete_form"):
        st.write("## Ingrese el id del gasto a eliminar")
        gasto_id = st.selectbox("Gasto", gastos_db["gasto_id"])
        delete_submitted = st.form_submit_button("Eliminar", use_container_width=True)
    if delete_submitted:
        try:
            run_execute("DELETE FROM gastos WHERE gasto_id = %s", (gasto_id,))
            st.success("Gasto eliminado con éxito!")
            run_query.clear() # clear cache
        except Exception as e:
            st.error("No se pudo eliminar el gasto")
            st.error(e)