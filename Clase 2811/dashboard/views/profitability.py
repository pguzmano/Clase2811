import streamlit as st
import plotly.express as px
import pandas as pd

def show(data):
    st.title("Rentabilidad Detallada")
    
    if "ventas_enriched" not in data:
        st.error("Datos no disponibles.")
        return
        
    df = data["ventas_enriched"].copy()
    
    # --- Filters ---
    with st.expander("Filtros", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            categories = ["Todas"] + sorted(list(df["categoria"].dropna().unique()))
            selected_cat = st.selectbox("Seleccionar Categoría", categories)
        
        if selected_cat != "Todas":
            df = df[df["categoria"] == selected_cat]
            
    st.markdown("---")
            
    # 1. Margin by Subcategory
    st.subheader("Margen Total por Subcategoría")
    # Handle column name variations if any, though we expect 'subcategoria'
    subcat_col = "subcategoria" if "subcategoria" in df.columns else "subcategory"
    
    margin_by_sub = df.groupby(subcat_col)['margen_total_cop'].sum().reset_index().sort_values("margen_total_cop", ascending=False)
    
    fig_margin = px.bar(
        margin_by_sub, 
        x=subcat_col, 
        y='margen_total_cop',
        color='margen_total_cop',
        labels={'margen_total_cop': 'Margen Total (COP)', subcat_col: 'Subcategoría'},
        template="plotly_white"
    )
    st.plotly_chart(fig_margin, use_container_width=True)
    
    # 2. Price vs Margin Scatter
    st.subheader("Análisis Precio vs Margen")
    st.caption("Cada punto representa una transacción de venta. El color indica la categoría.")
    
    # Calculate unit margin for scatter plot
    df['unit_margin'] = df['margen_total_cop'] / df['cantidad']
    
    # Sample if too large to prevent lag
    plot_df = df.sample(n=min(5000, len(df)), random_state=42)
    
    fig_scatter = px.scatter(
        plot_df, 
        x='precio_unitario_cop', 
        y='unit_margin', 
        color='categoria',
        hover_data=['descripcion', 'cliente_id'],
        labels={'precio_unitario_cop': 'Precio Unitario (COP)', 'unit_margin': 'Margen Unitario (COP)', 'categoria': 'Categoría'},
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 3. Detailed SKU Table
    st.subheader("Top Productos por Rentabilidad")
    
    # Group by product
    sku_stats = df.groupby(['producto_id', 'descripcion', 'categoria']).agg({
        'subtotal_cop': 'sum',
        'margen_total_cop': 'sum',
        'cantidad': 'sum'
    }).reset_index()
    
    sku_stats['margin_pct'] = (sku_stats['margen_total_cop'] / sku_stats['subtotal_cop']) * 100
    
    # Formatting columns
    st.dataframe(
        sku_stats.sort_values("margen_total_cop", ascending=False),
        column_config={
            "producto_id": "ID Producto",
            "descripcion": "Descripción",
            "categoria": "Categoría",
            "cantidad": "Cantidad",
            "subtotal_cop": st.column_config.NumberColumn("Ingresos Totales", format="$%.0f"),
            "margen_total_cop": st.column_config.NumberColumn("Margen Total", format="$%.0f"),
            "margin_pct": st.column_config.NumberColumn("Margen %", format="%.1f%%"),
        },
        use_container_width=True
    )
