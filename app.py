import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Análisis de Apuestas", layout="wide")
st.title("📊 Sistema de Análisis de Apuestas")

# Simular datos de apuestas
@st.cache_data
def generar_datos_apuestas(n=100):
    np.random.seed(42)
    fechas = [datetime.now() - timedelta(days=i) for i in range(n)]
    datos = {
        'fecha': sorted(fechas),
        'monto_apostado': np.random.uniform(10, 500, n),
        'cuota': np.random.uniform(1.5, 5.0, n),
        'resultado': np.random.choice(['Ganada', 'Perdida', 'Empatada'], n, p=[0.45, 0.45, 0.10]),
        'deporte': np.random.choice(['Fútbol', 'Tenis', 'Baloncesto', 'Béisbol'], n),
        'liga': np.random.choice(['Clasificatorias', 'Playoff', 'Regular'], n)
    }
    return pd.DataFrame(datos)

df = generar_datos_apuestas()

# Cálculos cuantitativos
def calcular_metricas(datos):
    total_apostado = datos['monto_apostado'].sum()
    total_ganadas = len(datos[datos['resultado'] == 'Ganada'])
    total_perdidas = len(datos[datos['resultado'] == 'Perdida'])
    tasa_ganancia = (total_ganadas / len(datos)) * 100
    roi = ((total_ganadas - total_perdidas) / len(datos)) * 100
    
    return {
        'total_apostado': total_apostado,
        'total_apuestas': len(datos),
        'ganadas': total_ganadas,
        'perdidas': total_perdidas,
        'tasa_ganancia': tasa_ganancia,
        'roi': roi
    }

metricas = calcular_metricas(df)

# Dashboard de métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Apostado", f"${metricas['total_apostado']:.2f}")
col2.metric("Tasa de Ganancia", f"{metricas['tasa_ganancia']:.1f}%")
col3.metric("ROI", f"{metricas['roi']:.1f}%")
col4.metric("Total Apuestas", metricas['total_apuestas'])

# Filtros interactivos
st.sidebar.header("⚙️ Filtros")
deporte_filter = st.sidebar.multiselect("Deporte", df['deporte'].unique(), 
                                       default=df['deporte'].unique())
resultado_filter = st.sidebar.multiselect("Resultado", df['resultado'].unique(),
                                         default=df['resultado'].unique())

df_filtrado = df[(df['deporte'].isin(deporte_filter)) & 
                 (df['resultado'].isin(resultado_filter))]

# Análisis cualitativo
st.subheader("📈 Análisis por Deporte")
col1, col2 = st.columns(2)

with col1:
    deporte_stats = df_filtrado.groupby('deporte').agg({
        'monto_apostado': 'sum',
        'resultado': lambda x: (x == 'Ganada').sum()
    }).rename(columns={'monto_apostado': 'Total Apostado', 'resultado': 'Ganadas'})
    st.dataframe(deporte_stats)

with col2:
    fig = px.pie(df_filtrado, names='resultado', 
                 title="Distribución de Resultados")
    st.plotly_chart(fig, use_container_width=True)

# Gráficos
st.subheader("📊 Visualizaciones")
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(df_filtrado.groupby('deporte')['monto_apostado'].sum().reset_index(),
                  x='deporte', y='monto_apostado', title="Apuestas por Deporte")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.scatter(df_filtrado, x='cuota', y='monto_apostado', 
                     color='resultado', title="Cuota vs Monto")
    st.plotly_chart(fig2, use_container_width=True)

# Tabla de datos
st.subheader("📋 Datos Filtrados")
st.dataframe(df_filtrado.sort_values('fecha', ascending=False), use_container_width=True)

