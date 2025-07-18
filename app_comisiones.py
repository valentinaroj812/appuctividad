
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Análisis de Comisiones - Junio 2025")

uploaded_file = st.file_uploader("Sube el archivo Excel con los cierres", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['Fecha Cierre'] = pd.to_datetime(df['Fecha Cierre'], errors='coerce')
    df = df[df['Fecha Cierre'].dt.month == 6]

    df['Dirección'] = df['Dirección'].str.strip().str.lower()
    df['Precio Cierre'] = pd.to_numeric(df['Precio Cierre'], errors='coerce')

    grouped = df.groupby(['Dirección', 'Precio Cierre'])

    def resolver_grupo(grupo):
        if grupo.shape[0] == 1:
            return grupo.iloc[0]
        fila = grupo.iloc[0].copy()
        captadores = grupo['OFICINA CAPTADOR'].dropna().unique()
        colocadores = grupo['OFICINA COLOCADOR'].dropna().unique()
        fila['OFICINA CAPTADOR'] = captadores[0] if len(captadores) > 0 else None
        fila['OFICINA COLOCADOR'] = colocadores[0] if len(colocadores) > 0 else None
        return fila

    df_deduplicado = grouped.apply(resolver_grupo).reset_index(drop=True)

    def calcular_comision(row):
        tipo_operacion = str(row.get('Tipo de Operación', '')).lower()
        oficina_captador = row.get('OFICINA CAPTADOR')
        oficina_colocador = row.get('OFICINA COLOCADOR')
        precio_cierre = row.get('Precio Cierre', 0)

        if pd.isna(precio_cierre) or precio_cierre == 0:
            return {}

        comisiones = {}
        if oficina_captador == oficina_colocador:
            oficina = oficina_captador
            if tipo_operacion == 'venta':
                comisiones[oficina] = round(precio_cierre * 0.04, 2)
            elif tipo_operacion == 'alquiler':
                comisiones[oficina] = round(precio_cierre * 1.0, 2)
        else:
            if tipo_operacion == 'venta':
                porcentaje = 0.02
            elif tipo_operacion == 'alquiler':
                porcentaje = 0.5
            else:
                return {}

            if pd.notna(oficina_captador):
                comisiones[oficina_captador] = round(precio_cierre * porcentaje, 2)
            if pd.notna(oficina_colocador):
                comisiones[oficina_colocador] = round(precio_cierre * porcentaje, 2)

        return comisiones

    df_deduplicado['Comisiones'] = df_deduplicado.apply(calcular_comision, axis=1)

    def descomponer_comisiones(row):
        comisiones = row['Comisiones']
        tipo = row['Tipo de Operación']
        if not comisiones:
            return pd.DataFrame([{
                'ID': row['ID'],
                'Tipo de Operación': tipo,
                'Fecha Cierre': row['Fecha Cierre'],
                'Oficina': None,
                'Comisión': 0.0
            }])
        return pd.DataFrame([{
            'ID': row['ID'],
            'Tipo de Operación': tipo,
            'Fecha Cierre': row['Fecha Cierre'],
            'Oficina': oficina,
            'Comisión': monto
        } for oficina, monto in comisiones.items()])

    comisiones_expandidas = pd.concat(
        [descomponer_comisiones(row) for _, row in df_deduplicado.iterrows()],
        ignore_index=True
    )

    ventas = comisiones_expandidas[comisiones_expandidas['Tipo de Operación'].str.lower() == 'venta']
    alquileres = comisiones_expandidas[comisiones_expandidas['Tipo de Operación'].str.lower() == 'alquiler']

    st.subheader("Resumen de Comisiones")
    st.write("👔 Ventas")
    st.dataframe(ventas)

    st.write("🏠 Alquileres")
    st.dataframe(alquileres)

    def to_excel(v_df, a_df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            v_df.to_excel(writer, index=False, sheet_name='Ventas')
            a_df.to_excel(writer, index=False, sheet_name='Alquileres')
        return output.getvalue()

    excel_data = to_excel(ventas, alquileres)
    st.download_button("📥 Descargar Excel", data=excel_data, file_name="comisiones_junio_2025.xlsx")
