
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Análisis de Comisiones - Junio 2025")

# Cargar archivo Excel
uploaded_file = st.file_uploader("Sube el archivo Excel con los cierres", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['Fecha Cierre'] = pd.to_datetime(df['Fecha Cierre'], errors='coerce')
    df = df[df['Fecha Cierre'].dt.month == 6]

    # Calcular comisiones por fila
    def calcular_comision(row):
        tipo_operacion = row.get('Tipo de Operación', '').lower()
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

    df['Comisiones'] = df.apply(calcular_comision, axis=1)

    # Expandir comisiones a filas
    def descomponer_comisiones(row):
        comisiones = row['Comisiones']
        if not comisiones:
            return pd.DataFrame([{
                'ID': row['ID'],
                'Fecha Cierre': row['Fecha Cierre'],
                'Oficina': None,
                'Comisión': 0.0
            }])
        return pd.DataFrame([{
            'ID': row['ID'],
            'Fecha Cierre': row['Fecha Cierre'],
            'Oficina': oficina,
            'Comisión': monto
        } for oficina, monto in comisiones.items()])

    comisiones_expandidas = pd.concat(
        [descomponer_comisiones(row) for _, row in df.iterrows()],
        ignore_index=True
    )

    st.subheader("Comisiones por Oficina")
    st.dataframe(comisiones_expandidas)

    # Descargar como Excel
    def to_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Comisiones')
        return output.getvalue()

    excel_data = to_excel(comisiones_expandidas)
    st.download_button("📥 Descargar Excel", data=excel_data, file_name="comisiones_junio_2025.xlsx")
