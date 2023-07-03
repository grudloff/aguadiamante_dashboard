import streamlit as st
from Diamante_Agua_Pura import run_query
from geopy.geocoders import Nominatim
import pandas as pd

st.set_page_config(page_title="Visualización", page_icon="📈")

# get geocorder function
@st.cache_resource    
def get_geocoder():
    return Nominatim(user_agent="Diamante Agua Pura")

def get_location(x):
    x_dict = { "direction" : x['direccion'], "city" : x['ciudad']}
    location = geocoder.geocode(x_dict, country_codes="cl", timeout=10)
    if location is None:
        location = geocoder.geocode(x_dict["city"], country_codes="cl", timeout=10)
    return location

def direction_to_latlong(df: pd.DataFrame) -> pd.DataFrame:
    df["location"] = df.apply(get_location, axis=1)
    df["latitude"] = df["location"].apply(lambda x: x.latitude)
    df["longitude"] = df["location"].apply(lambda x: x.longitude)
    df = df.drop(columns=["location"])
    return df

geocoder = get_geocoder()

st.write("# Visualización")
st.write("## Mapa de clientes")
client_locations = run_query("SELECT DISTINCT direccion FROM clientes")
client_locations = pd.DataFrame(client_locations, columns=["direccion"])
client_locations[["direccion", "ciudad"]] = client_locations["direccion"].str.split(",", expand=True)
# filter by city option
city_options = client_locations["ciudad"].unique()
city_selection = st.multiselect("Ciudad", city_options,  default=city_options, key="Ciudad")
client_locations = client_locations[client_locations["ciudad"].isin(city_selection)]
client_locations = direction_to_latlong(client_locations)
st.map(client_locations)

# map by city
with st.expander("Mapa de clientes por ciudad"):
    cities = client_locations["ciudad"].unique()
    for city in cities:
        st.write("### " + city)
        st.map(client_locations[client_locations["ciudad"] == city])
