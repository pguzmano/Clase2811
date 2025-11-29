import streamlit as st
from data.loader import load_data
from data.processor import process_data
from components.sidebar import show_sidebar
from views import overview, profitability, customers, imports, inventory, credit_risk

# Page Config
st.set_page_config(
    page_title="Tablero Comercializadora Andina",
    page_icon="📊",
    layout="wide"
)

# Load Data
# We use st.cache_data in loader, so this is efficient
with st.spinner("Cargando y procesando datos..."):
    raw_data = load_data()
    data = process_data(raw_data)

# Sidebar
selection = show_sidebar()

# Routing
if selection == "Resumen General":
    overview.show(data)
elif selection == "Rentabilidad":
    profitability.show(data)
elif selection == "Clientes":
    customers.show(data)
elif selection == "Importaciones":
    imports.show(data)
elif selection == "Inventario":
    inventory.show(data)
elif selection == "Riesgo Crediticio":
    credit_risk.show(data)
