import os
import streamlit as st
import psycopg2
import warnings

folder_filepath = ".postgresql" 
cert_filepath = os.path.join(folder_filepath, "root.crt") 

def _validate_connection(conn):
     try:
          return conn.closed==0
     except Exception as e:
          warnings.warn(f"Error accessing the database connection:\n {e} \n Reconnecting...")
          return False

@st.cache_resource(validate = _validate_connection)
def init_connection():
    if not os.path.exists(folder_filepath):
            os.mkdir(folder_filepath)
    with open(cert_filepath,"w+") as f:
        f.write(st.secrets["CA_CERTIFICATE"])
    conn = psycopg2.connect(st.secrets["DATABASE_URL"], sslrootcert=cert_filepath)
    return conn

@st.cache_data(ttl=600)
def run_query(*query):
    conn = init_connection()
    with conn.cursor() as cur:
        cur.execute(*query)
        return cur.fetchall()
    
def run_execute(*query):
    conn = init_connection()
    with conn.cursor() as cur:
        cur.execute(*query)
        conn.commit()
