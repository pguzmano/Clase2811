import streamlit as st
import pandas as pd
import plotly.express as px

def show(data):
    st.title("Resumen General")
    
    if "ventas_enriched" not in data:
        st.error("Datos de ventas no disponibles.")
        return

    df = data["ventas_enriched"]
    
    # --- KPIs ---
    total_sales = df["subtotal_cop"].sum()
    total_profit = df["margen_total_cop"].sum()
    margin_pct = (total_profit / total_sales) * 100 if total_sales > 0 else 0
    
    # Active Customers (from Master if available, else from Sales)
    if "clientes" in data:
        active_customers = data["clientes"][data["clientes"]["estado"] == "Activo"].shape[0]
    else:
        active_customers = df["cliente_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Ventas Totales", f"${total_sales:,.0f}")
    col2.metric("Utilidad Total", f"${total_profit:,.0f}")
    col3.metric("Margen Bruto", f"{margin_pct:.1f}%")
    col4.metric("Clientes Activos", f"{active_customers}")
    
    st.markdown("---")
    
    # --- Charts ---
    
    # 1. Monthly Sales Trend
    # Ensure date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['fecha']):
         df['fecha'] = pd.to_datetime(df['fecha'])
         
    monthly_sales = df.groupby(df['fecha'].dt.to_period("M"))['subtotal_cop'].sum().reset_index()
    monthly_sales['fecha'] = monthly_sales['fecha'].dt.to_timestamp()
    
    st.subheader("Tendencia Mensual de Ventas")
    fig_trend = px.line(monthly_sales, x='fecha', y='subtotal_cop', markers=True, labels={'fecha': 'Fecha', 'subtotal_cop': 'Ventas (COP)'})
    st.plotly_chart(fig_trend, use_container_width=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        # 2. Sales by Region
        st.subheader("Ventas por Región")
        region_sales = df.groupby("region")['subtotal_cop'].sum().reset_index().sort_values("subtotal_cop", ascending=False)
        fig_region = px.bar(region_sales, x='region', y='subtotal_cop', labels={'region': 'Región', 'subtotal_cop': 'Ventas (COP)'})
        st.plotly_chart(fig_region, use_container_width=True)
        
    with col_right:
        # 3. Top 5 Products
        st.subheader("Top 5 Productos por Ingresos")
        # Use description if available, else ID
        prod_col = "descripcion" if "descripcion" in df.columns else "producto_id"
        top_products = df.groupby(prod_col)['subtotal_cop'].sum().reset_index().sort_values("subtotal_cop", ascending=False).head(5)
        fig_prod = px.bar(top_products, x='subtotal_cop', y=prod_col, orientation='h', labels={'subtotal_cop': 'Ventas (COP)', prod_col: 'Producto'})
        st.plotly_chart(fig_prod, use_container_width=True)
