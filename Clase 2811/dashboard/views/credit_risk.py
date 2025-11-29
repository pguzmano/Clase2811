import streamlit as st
import plotly.express as px
import pandas as pd

def show(data):
    st.title("Análisis de Riesgo Crediticio")
    
    if "cartera" not in data:
        st.error("Datos no disponibles.")
        return
        
    df = data["cartera"].copy()
    
    # Ensure dates
    df['fecha_factura'] = pd.to_datetime(df['fecha_factura'])
    df['fecha_vencimiento'] = pd.to_datetime(df['fecha_vencimiento'])
    
    # --- KPIs ---
    total_receivables = df['saldo_cop'].sum()
    # Assuming 'dias_mora' > 0 means overdue
    overdue_receivables = df[df['dias_mora'] > 0]['saldo_cop'].sum()
    overdue_pct = (overdue_receivables / total_receivables) * 100 if total_receivables > 0 else 0
    
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Cartera", f"${total_receivables:,.0f}")
    kpi2.metric("Cartera Vencida", f"${overdue_receivables:,.0f}")
    kpi3.metric("Riesgo de Portafolio (%)", f"{overdue_pct:.1f}%")
    
    st.markdown("---")
    
    # 1. Aging Analysis
    st.subheader("Edades de Cartera")
    
    def categorize_aging(days):
        if days <= 0: return "Al Día"
        elif days <= 30: return "1-30 Días"
        elif days <= 60: return "31-60 Días"
        elif days <= 90: return "61-90 Días"
        else: return "90+ Días"
        
    df['aging_bucket'] = df['dias_mora'].apply(categorize_aging)
    
    # Order buckets
    bucket_order = ["Al Día", "1-30 Días", "31-60 Días", "61-90 Días", "90+ Días"]
    
    aging_summary = df.groupby('aging_bucket')['saldo_cop'].sum().reindex(bucket_order).reset_index()
    
    fig_aging = px.bar(
        aging_summary, 
        x='aging_bucket', 
        y='saldo_cop', 
        title="Cartera por Rango de Mora",
        labels={'saldo_cop': 'Saldo (COP)', 'aging_bucket': 'Días de Mora'}
    )
    st.plotly_chart(fig_aging, use_container_width=True)
    
    # 2. Risk by Region
    st.subheader("Saldo Vencido por Región")
    region_risk = df[df['dias_mora'] > 0].groupby("region")['saldo_cop'].sum().reset_index().sort_values("saldo_cop", ascending=False)
    
    fig_region = px.pie(region_risk, values='saldo_cop', names='region', labels={'saldo_cop': 'Saldo Vencido', 'region': 'Región'})
    st.plotly_chart(fig_region, use_container_width=True)
    
    # 3. Top Delinquent Accounts
    st.subheader("Facturas con Mayor Mora")
    top_delinquent = df[df['dias_mora'] > 0].groupby(['cliente_id', 'documento_id']).agg({
        'saldo_cop': 'sum',
        'dias_mora': 'max'
    }).reset_index().sort_values("saldo_cop", ascending=False).head(20)
    
    st.dataframe(
        top_delinquent,
        column_config={
            "cliente_id": "ID Cliente",
            "documento_id": "Factura",
            "saldo_cop": st.column_config.NumberColumn("Saldo Vencido", format="$%.0f"),
            "dias_mora": st.column_config.NumberColumn("Días Mora"),
        },
        use_container_width=True
    )
