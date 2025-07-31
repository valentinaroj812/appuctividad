
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Análisis de Comisiones - Año 2025")

uploaded_file = st.file_uploader("Sube el archivo Excel con los cierres", type=["xlsx"])

if uploaded_file:
    st.markdown("## 🔍 Filtros")

    raw_df = pd.read_excel(uploaded_file)
    raw_df['Fecha Cierre'] = pd.to_datetime(raw_df['Fecha Cierre'], errors='coerce')
    df = raw_df[raw_df['Fecha Cierre'].dt.year == 2025]

    oficina_options = sorted(list(set(df['OFICINA CAPTADOR'].dropna().unique()) | set(df['OFICINA COLOCADOR'].dropna().unique())))
    oficina_filtro = st.selectbox("Filtrar por Oficina", options=["Todas"] + oficina_options)

    
meses = ['Todos'] + list(range(1, 13))
mes_filtro = st.selectbox("Filtrar por Mes", meses)

tipo_filtro = st.selectbox("Filtrar por Tipo de Operación", ["Todas", "venta", "alquiler"])


    if oficina_filtro != "Todas":
        df = df[(df['OFICINA CAPTADOR'] == oficina_filtro) | (df['OFICINA COLOCADOR'] == oficina_filtro)]

    
    if mes_filtro != "Todos":
        df = df[df['Fecha Cierre'].dt.month == mes_filtro]

    if tipo_filtro != "Todas":

        df = df[df['Tipo de Operación'].str.lower() == tipo_filtro]

    df['Dirección'] = df['Dirección'].str.strip().str.lower()
    df['Precio Cierre'] = pd.to_numeric(df['Precio Cierre'], errors='coerce')

    grouped = df.groupby(['Dirección', 'Precio Cierre'])

    def resolver_grupo(grupo):
        fila = grupo.iloc[0].copy()
        oficinas_captador = grupo['OFICINA CAPTADOR'].dropna().unique().tolist()
        oficinas_colocador = grupo['OFICINA COLOCADOR'].dropna().unique().tolist()
        fila['OFICINAS_INVOLUCRADAS'] = list(set(oficinas_captador + oficinas_colocador))
        return fila

    df_deduplicado = grouped.apply(resolver_grupo).reset_index(drop=True)

    def calcular_comision(row):
        tipo_operacion = str(row.get('Tipo de Operación', '')).lower()
        oficinas = row.get('OFICINAS_INVOLUCRADAS', [])
        precio_cierre = row.get('Precio Cierre', 0)

        if not isinstance(oficinas, list) or len(oficinas) == 0 or pd.isna(precio_cierre) or precio_cierre == 0:
            return {}

        comisiones = {}

        if (
            'BUSINESS&RESIDENCES' in oficinas
            and precio_cierre == df['Precio Cierre'].max()
        ):
            comisiones['BUSINESS&RESIDENCES'] = round(precio_cierre * 0.03, 2)
            return comisiones

        if tipo_operacion == 'venta':
            total_comision = precio_cierre * 0.02
        elif tipo_operacion == 'alquiler':
            total_comision = precio_cierre * 0.5
        else:
            return {}

        split = round(total_comision / len(oficinas), 2)
        for oficina in oficinas:
            comisiones[oficina] = split

        return comisiones

    df_deduplicado['Comisiones'] = df_deduplicado.apply(calcular_comision, axis=1)

    def descomponer_comisiones(row):
        comisiones = row['Comisiones']
        tipo = row['Tipo de Operación']
        if not comisiones:
            return pd.DataFrame([{
                'Tipo de Operación': tipo,
            'Dirección': row['Dirección'],
                'Fecha Cierre': row['Fecha Cierre'],
                'Oficina': None,
                'Comisión': 0.0
            }])
        return pd.DataFrame([{
            'Tipo de Operación': tipo,
            'Dirección': row['Dirección'],
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

    st.markdown("### Totales por Oficina (Ventas)")
    totales_ventas = ventas.groupby("Oficina", dropna=False)['Comisión'].sum().reset_index().sort_values(by='Comisión', ascending=False)
    st.dataframe(totales_ventas)

    st.markdown("### Totales por Oficina (Alquileres)")
    totales_alquileres = alquileres.groupby("Oficina", dropna=False)['Comisión'].sum().reset_index().sort_values(by='Comisión', ascending=False)
    st.dataframe(totales_alquileres)

    st.markdown("### Detalle de Ventas")
    st.dataframe(ventas)

    st.markdown("### Detalle de Alquileres")
    st.dataframe(alquileres)

    def to_excel(v_df, a_df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            v_df.to_excel(writer, index=False, sheet_name='Ventas')
            a_df.to_excel(writer, index=False, sheet_name='Alquileres')
        return output.getvalue()

    excel_data = to_excel(ventas, alquileres)
    st.download_button("📥 Descargar Excel", data=excel_data, file_name="comisiones_2025.xlsx")
