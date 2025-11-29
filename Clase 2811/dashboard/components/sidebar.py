import streamlit as st

def show_sidebar():
    """
    Renders the sidebar and returns the selected navigation option.
    """
    with st.sidebar:
        st.title("Comercializadora Andina")
        st.image("https://via.placeholder.com/150", caption="Logo") # Replace with actual logo if available
        
        st.header("Navegación")
        
        options = [
            "Resumen General",
            "Rentabilidad",
            "Clientes",
            "Importaciones",
            "Inventario",
            "Riesgo Crediticio"
        ]
        
        selection = st.radio("Ir a", options)
        
        st.markdown("---")
        st.caption("Tablero v1.0")
        
        return selection
