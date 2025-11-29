import pandas as pd
import streamlit as st

def process_data(data):
    """
    Process and clean the loaded data.
    Performs date conversions, numeric cleaning, and merges datasets for analysis.
    """
    # 1. Convert Dates
    date_cols = {
        "cartera": ["fecha_factura", "fecha_vencimiento"],
        "clientes": ["fecha_alta"],
        "importaciones": ["fecha_orden", "fecha_llegada"],
        "inventario": ["fecha_corte"],
        "ventas": ["fecha"]
    }
    
    for key, cols in date_cols.items():
        if key in data:
            df = data[key]
            for col in cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            data[key] = df

    # 2. Numeric Cleaning (if necessary)
    # Check for comma decimals in importaciones if they exist as strings
    if "importaciones" in data:
        df = data["importaciones"]
        numeric_cols = ["costo_mercancia_usd", "flete_usd", "arancel_cop", "otros_costos_cop"]
        for col in numeric_cols:
            if col in df.columns and df[col].dtype == 'object':
                 df[col] = df[col].str.replace(',', '.', regex=False).astype(float)
        data["importaciones"] = df

    # 3. Merge Data for easier analysis
    # Create a master sales table: Sales + Product Info + Customer Info
    if "ventas" in data and "productos" in data and "clientes" in data:
        sales = data["ventas"].copy()
        products = data["productos"].copy()
        customers = data["clientes"].copy()
        
        # Merge with products (left join to keep all sales)
        # Suffix collisions: 'categoria', 'subcategoria' exist in both. 
        # We prefer the ones from Product master if available, or keep Sales ones if they differ.
        # Usually Sales snapshot might differ from Master. Let's keep Sales as is, and add Product Master info with suffix.
        sales_enriched = sales.merge(
            products, 
            on="producto_id", 
            how="left", 
            suffixes=("", "_master")
        )
        
        # Merge with customers
        # 'region', 'ciudad', 'segmento' exist in both.
        sales_enriched = sales_enriched.merge(
            customers, 
            on="cliente_id", 
            how="left", 
            suffixes=("", "_master")
        )
        
        # Calculate calculated fields if missing
        # e.g. Margin %
        if "margen_total_cop" in sales_enriched.columns and "subtotal_cop" in sales_enriched.columns:
            sales_enriched["margen_pct"] = (sales_enriched["margen_total_cop"] / sales_enriched["subtotal_cop"]).fillna(0)
            
        data["ventas_enriched"] = sales_enriched
        
    return data
