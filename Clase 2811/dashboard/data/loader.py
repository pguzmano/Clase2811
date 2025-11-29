import pandas as pd
import streamlit as st
import os

# Configuration
# Data is located in the 'Data' folder relative to the project root or absolute path
# Using absolute path as per previous exploration
DATA_PATH = "c:/Users/Pedro Luis/Downloads/Clase 2811/Data/"

@st.cache_data
def load_data():
    """
    Loads all necessary data files from the configured data path.
    Returns a dictionary of DataFrames.
    """
    files = {
        "cartera": "cartera_andina.csv",
        "clientes": "clientes_andina.csv",
        "importaciones": "importaciones_andina.csv",
        "inventario": "inventario_andina.csv",
        "productos": "productos_andina.csv",
        "ventas": "ventas_andina.csv"
    }
    
    data = {}
    
    for key, filename in files.items():
        file_path = os.path.join(DATA_PATH, filename)
        try:
            # Special handling for importaciones which uses ; delimiter and , decimal
            if key == "importaciones":
                df = pd.read_csv(file_path, sep=';', decimal=',')
            else:
                df = pd.read_csv(file_path)
            
            data[key] = df
        except Exception as e:
            st.error(f"Error loading {filename}: {e}")
            data[key] = pd.DataFrame() # Return empty DF on error to prevent crash
            
    return data
