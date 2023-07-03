import streamlit as st
from Diamante_Agua_Pura import run_query
from geopy.geocoders import Nominatim
import pandas as pd
from typing import Tuple

st.set_page_config(page_title="Visualización", page_icon="📈")

# get geocorder function
@st.cache_resource    
def get_geocoder():
    return Nominatim(user_agent="Diamante Agua Pura")

def get_location(x: str) -> pd.Series:
    """ Gets the latitude and longitude of a direction and city. """
    x_dict = { "direction" : x['direccion'], "city" : x['ciudad']}
    location = geocoder.geocode(x_dict, country_codes="cl", timeout=10)
    if location is None:
        location = geocoder.geocode(x_dict["city"], country_codes="cl", timeout=10)
    return pd.Series([location.latitude, location.longitude])

def direction_to_latlong(df: pd.DataFrame) -> pd.DataFrame:
    """ Converts a dataframe with direction and city columns to a dataframe with 
    latitude and longitude columns. """	
    df[["latitude", "longitude"]] = df.apply(get_location, axis=1)
    return df



geocoder = get_geocoder()

st.write("# Visualización")
st.write("## Clientes")

# Visualizacion de clientes en el tiempo
with st.expander("Captación de clientes"):
    # select between daily, weekly, monthly
    time_options = ["Diario", "Semanal", "Mensual"]
    time_selection = st.selectbox("Seleccionar periodo", time_options, index=1, key="Periodo")
    if time_selection == "Diario":
        time_option = "day"
    elif time_selection == "Semanal":
        time_option = "week"
    else:
        time_option = "month"

    # get data
    query = f"""
    SELECT DATE_TRUNC('{time_option}', date), COUNT(*) AS clientes
    FROM clientes
    GROUP BY DATE_TRUNC('{time_option}', date)
    """

    clientes = run_query(query)

    # plot
    time_map = {"Diario" : "día", "Semanal" : "semana", "Mensual" : "mes"}
    st.write("### Captación de clientes por " + time_map[time_selection])
    clientes_df = pd.DataFrame(clientes, columns=["Fecha", "Clientes"])
    clientes_df["Fecha"] = pd.to_datetime(clientes_df["Fecha"])
    clientes_df = clientes_df.set_index("Fecha")
    st.line_chart(clientes_df)

with st.expander("Mapa de clientes"):

    client_directions = run_query("SELECT DISTINCT direccion FROM clientes")
    clients_loc = pd.DataFrame(client_directions, columns=["direccion"])
    clients_loc[["direccion", "ciudad"]] = clients_loc["direccion"].str.split(",", expand=True)
    clients_loc = direction_to_latlong(clients_loc)

    # filter by city option
    city_options = clients_loc["ciudad"].unique()
    city_selection = st.multiselect("Filtrar por ciudad", city_options,  default=city_options, key="Ciudad")
    df_clients_loc_filtered = clients_loc[clients_loc["ciudad"].isin(city_selection)]

    # option: aggregated map or per city map
    help = "Muestra todos los clientes en un mapa. En su defecto, muestra un mapa por ciudad."
    if st.checkbox("Mostrar mapa agregado", value=True, help=help):
        st.map(df_clients_loc_filtered)
    else:
        for city in city_options:
            st.write("### " + city)
            st.map(clients_loc[clients_loc["ciudad"] == city])

st.write("## Ventas")

with st.expander("Ventas en el tiempo"):
    # select between daily, weekly, monthly
    time_options = ["Diario", "Semanal", "Mensual"]
    time_selection = st.selectbox("Seleccionar periodo", time_options, index=1, key="Periodo_ventas")
    if time_selection == "Diario":
        time_option = "day"
    elif time_selection == "Semanal":
        time_option = "week"
    else:
        time_option = "month"

    help = "Muestra las ventas totales en un gráfico. En su defecto, muestra un gráfico por producto."
    if st.checkbox("Mostrar ventas agregadas", value=True, help=help):

        query = f"""
        SELECT DATE_TRUNC('{time_option}', p.fecha_pedido), SUM(ip.cantidad * pr.precio), pr.nombre AS ventas
        FROM pedidos p
        INNER JOIN items_pedido ip ON p.pedido_id = ip.pedido_id
        INNER JOIN productos pr ON ip.producto_id = pr.producto_id
        GROUP BY DATE_TRUNC('{time_option}', p.fecha_pedido), pr.nombre
        """

        ventas = run_query(query)

        # plot
        time_map = {"Diario" : "día", "Semanal" : "semana", "Mensual" : "mes"}
        st.write("### Ventas por " + time_map[time_selection])
        ventas_df = pd.DataFrame(ventas, columns=["Fecha", "Ventas", "Producto"])
        ventas_df["Ventas"] = ventas_df["Ventas"].astype(int)
        ventas_df["Fecha"] = pd.to_datetime(ventas_df["Fecha"])
        ventas_df = ventas_df.set_index("Fecha")
        ventas_df = ventas_df.pivot_table(index="Fecha", columns="Producto", values="Ventas", aggfunc="sum")
        ventas_df = ventas_df.fillna(0)
        st.area_chart(ventas_df)

    else:
        product_options = run_query("SELECT DISTINCT nombre FROM productos")
        product_options = [product[0] for product in product_options]
        product_selection = st.selectbox("Seleccionar producto", product_options, index=0, key="Producto")

        query = f"""
        SELECT DATE_TRUNC('{time_option}', fecha_pedido), SUM(precio * cantidad) AS ventas
        FROM pedidos
        INNER JOIN items_pedido ON pedidos.pedido_id = items_pedido.pedido_id
        INNER JOIN productos ON items_pedido.producto_id = productos.producto_id
        WHERE nombre = '{product_selection}'
        GROUP BY DATE_TRUNC('{time_option}', fecha_pedido)
        """

        ventas = run_query(query)

        # plot
        time_map = {"Diario" : "día", "Semanal" : "semana", "Mensual" : "mes"}
        st.write("### Ventas de " + product_selection + " por " + time_map[time_selection])
        ventas_df = pd.DataFrame(ventas, columns=["Fecha", "Ventas"])
        ventas_df["Fecha"] = pd.to_datetime(ventas_df["Fecha"])
        ventas_df = ventas_df.set_index("Fecha")
        ventas_df = ventas_df.astype(int)
        st.line_chart(ventas_df)

with st.expander("Mapa de ventas"):
    # get data
    query = """
    SELECT DISTINCT direccion, ciudad, SUM(ip.cantidad * pr.precio) AS ventas
    FROM pedidos p
    INNER JOIN items_pedido ip ON p.pedido_id = ip.pedido_id
    INNER JOIN productos pr ON ip.producto_id = pr.producto_id
    INNER JOIN clientes c ON p.cliente_rut = c.cliente_rut
    GROUP BY direccion, ciudad
    """

    ventas = run_query(query)

    # plot
    ventas_df = pd.DataFrame(ventas, columns=["direccion", "ciudad", "ventas"])
    ventas_df[["direccion", "ciudad"]] = ventas_df["direccion"].str.split(",", expand=True)
    ventas_df = direction_to_latlong(ventas_df)
    st.map(ventas_df)

st.write("## Productos")
with st.expander("Stock en el tiempo"):
    # select between daily, weekly, monthly
    time_options = ["Diario", "Semanal", "Mensual"]
    time_selection = st.selectbox("Seleccionar periodo", time_options, index=1, key="Periodo_productos")
    if time_selection == "Diario":
        time_option = "day"
    elif time_selection == "Semanal":
        time_option = "week"
    else:
        time_option = "month"

    # select between aggregated or per product
    help = "Muestra el stock total en un gráfico. En su defecto, muestra un gráfico por producto."
    if st.checkbox("Mostrar stock agregado", value=True, help=help):
            
        query = f"""
        SELECT DATE_TRUNC('{time_option}', date), SUM(stock), nombre AS stock
        FROM productos
        GROUP BY DATE_TRUNC('{time_option}', date), nombre
        """

        stock = run_query(query)

        # plot
        time_map = {"Diario" : "día", "Semanal" : "semana", "Mensual" : "mes"}
        st.write("### Stock por " + time_map[time_selection])
        stock_df = pd.DataFrame(stock, columns=["Fecha", "Stock", "Producto"])
        stock_df["Fecha"] = pd.to_datetime(stock_df["Fecha"])
        stock_df["Stock"] = stock_df["Stock"].astype(int)
        stock_df = stock_df.set_index("Fecha")
        stock_df = stock_df.pivot_table(index="Fecha", columns="Producto", values="Stock", aggfunc="sum")
        st.area_chart(stock_df)
    else:
        product_options = run_query("SELECT DISTINCT nombre FROM productos")
        product_options = [product[0] for product in product_options]
        product_selection = st.selectbox("Seleccionar producto", product_options, index=0, key="Producto")

        query = f"""
        SELECT DATE_TRUNC('{time_option}', fecha), stock
        FROM productos
        WHERE nombre = '{product_selection}'
        """

        stock = run_query(query)

        # plot
        time_map = {"Diario" : "día", "Semanal" : "semana", "Mensual" : "mes"}
        st.write("### Stock de " + product_selection + " por " + time_map[time_selection])
        stock_df = pd.DataFrame(stock, columns=["Fecha", "Stock"])
        stock_df["Fecha"] = pd.to_datetime(stock_df["Fecha"])
        stock_df = stock_df.set_index("Fecha")
        stock_df = stock_df.astype(int)
        st.line_chart(stock_df)

