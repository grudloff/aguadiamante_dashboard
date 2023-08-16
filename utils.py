import os
import streamlit as st
import psycopg2
import warnings
from tenacity import retry, stop_after_attempt, retry_if_not_exception_type
import time
import logging
from psycopg2.errors import UniqueViolation

fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s : %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(fmt)
logger.addHandler(handler)

folder_filepath = ".postgresql" 
cert_filepath = os.path.join(folder_filepath, "root.crt") 

def _validate_connection(conn):
     try:
          return conn.closed==0
     except Exception as e:
          warnings.warn(f"Error accessing the database connection:\n {repr(e)} \n Reconnecting...")
          return False

@st.cache_resource(validate = _validate_connection)
def init_connection():
    if not os.path.exists(folder_filepath):
            os.mkdir(folder_filepath)
    with open(cert_filepath,"w+") as f:
        f.write(st.secrets["CA_CERTIFICATE"])
    conn = psycopg2.connect(st.secrets["DATABASE_URL"], sslrootcert=cert_filepath)
    return conn

def rollback():
    conn = init_connection()
    conn.rollback()

def rerun_when_all_attempts_fail(retry_state):
    init_connection.clear()
    try:
        raise retry_state.outcome.exception()
    except Exception as e:
        st.warning("La ejecución del llamado a la base de datos fallo multiples veces!"+
                   "Se reiniciara la conección a la base de datos...", icon="🚨")
        st.error(repr(e))
        logger.error("The maximum number of retries was reached!")
        logger.error(repr(e))
        raise e
    finally:
        time.sleep(10)
        st.experimental_rerun()


@st.cache_data(ttl=600)
@retry(stop=stop_after_attempt(3), reraise=True, retry_error_callback=rerun_when_all_attempts_fail,
       retry=retry_if_not_exception_type(UniqueViolation))
def run_query(query, params=None):
    try:
        conn = init_connection()
        with conn.cursor() as cur:
            if params is not None:
                cur.execute(query, params)
            else:
                cur.execute(query)
            return cur.fetchall()
    except UniqueViolation as e:
        st.error("Estas intentando duplicar una entrada ya ingresada!", icon="🚨")
        logger.error("There was an error while executing the query!")
        logger.error(repr(e))
        raise e
    except Exception as e:
        logger.error("There was an error while executing the query!")
        logger.error(repr(e))
        logger.error("Rolling back the transaction...")
        rollback()
        raise e

@retry(stop=stop_after_attempt(3), reraise=True, retry_error_callback=rerun_when_all_attempts_fail,
       retry=retry_if_not_exception_type(UniqueViolation))
def run_execute(query, params=None):
    try:
        conn = init_connection()
        with conn.cursor() as cur:
            if params is not None:
                cur.execute(query, params)
            else:
                cur.execute(query)
            conn.commit()
    except UniqueViolation as e:
        st.error("Estas intentando duplicar una entrada ya ingresada!", icon="🚨")
        logger.error("There was an error while executing the query!")
        logger.error(repr(e))
        raise e
    except Exception as e:
        logger.error("There was an error while executing the query!")
        logger.error(repr(e))
        logger.error("Rolling back the transaction...")
        rollback()
        raise e
