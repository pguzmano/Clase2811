import streamlit as st
import plotly.express as px
import pandas as pd

def show(data):
    st.title("Inventario y Operaciones")
    
    if "inventario" not in data:
        st.error("Datos no disponibles.")
        return
        
    df = data["inventario"].copy()
    
    # Ensure date
    df['fecha_corte'] = pd.to_datetime(df['fecha_corte'])
    
    # Filter by latest date (Snapshot)
    latest_date = df['fecha_corte'].max()
    st.info(f"Mostrando inventario al corte de: {latest_date.date()}")
    
    current_inventory = df[df['fecha_corte'] == latest_date]
    
    # --- KPIs ---
    total_value = current_inventory['valor_inventario_cop'].sum()
    total_units = current_inventory['stock_unidades'].sum()
    total_skus = current_inventory['producto_id'].nunique()
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Valor Total Inventario", f"${total_value:,.0f}")
    kpi2.metric("Unidades Totales", f"{total_units:,.0f}")
    kpi3.metric("Total SKUs", f"{total_skus}")
    
    st.markdown("---")
    
    # 1. Value by Logistic Center
    st.subheader("Valor de Inventario por Centro Logístico")
    center_value = current_inventory.groupby("centro_logistico")['valor_inventario_cop'].sum().reset_index().sort_values("valor_inventario_cop", ascending=False)
    fig_center = px.bar(center_value, x='centro_logistico', y='valor_inventario_cop', title="Valor por Centro", labels={'valor_inventario_cop': 'Valor (COP)', 'centro_logistico': 'Centro Logístico'})
    st.plotly_chart(fig_center, use_container_width=True)
    
    # 2. Category Breakdown
    st.subheader("Distribución de Stock por Categoría")
    col1, col2 = st.columns(2)
    
    with col1:
        # By Value
        cat_value = current_inventory.groupby("categoria")['valor_inventario_cop'].sum().reset_index()
        fig_cat_val = px.pie(cat_value, values='valor_inventario_cop', names='categoria', title="Por Valor", labels={'valor_inventario_cop': 'Valor', 'categoria': 'Categoría'})
        st.plotly_chart(fig_cat_val, use_container_width=True)
        
    with col2:
        # By Units
        cat_units = current_inventory.groupby("categoria")['stock_unidades'].sum().reset_index()
        fig_cat_units = px.pie(cat_units, values='stock_unidades', names='categoria', title="Por Unidades", labels={'stock_unidades': 'Unidades', 'categoria': 'Categoría'})
        st.plotly_chart(fig_cat_units, use_container_width=True)
        
    # 3. Historical Trend (Total Value)
    st.subheader("Tendencia de Valor de Inventario")
    history = df.groupby("fecha_corte")['valor_inventario_cop'].sum().reset_index()
    fig_trend = px.line(history, x='fecha_corte', y='valor_inventario_cop', markers=True, title="Valor Total en el Tiempo", labels={'fecha_corte': 'Fecha Corte', 'valor_inventario_cop': 'Valor (COP)'})
    st.plotly_chart(fig_trend, use_container_width=True)
