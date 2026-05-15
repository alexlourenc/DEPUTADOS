import streamlit as st
import pandas as pd
import plotly.express as px
import os

"""
English: Streamlit dashboard to visualize legislative insights from the Gold layer.
Português: Dashboard Streamlit para visualizar insights legislativos da camada Gold.
"""

def main():
    st.set_page_config(page_title="Atlas Legislativo - Dashboard", layout="wide")
    st.title("🏛️ Atlas Legislativo: Inteligência de Dados")
    st.markdown("---")

    gold_path = r'data\gold'

    # English: Sidebar for navigation / Português: Barra lateral para navegação
    menu = ["Resumo Geral", "Atlas das Frentes", "Calendário de Eventos", "Auditoria CEAP"]
    choice = st.sidebar.selectbox("Navegar por Marco", menu)

    if choice == "Resumo Geral":
        st.subheader("Visão Geral do Projeto")
        st.info("Este dashboard consome dados processados via Arquitetura Medallion (Bronze -> Silver -> Gold).")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Frentes Analisadas", "1.227")
        col2.metric("Eventos (2026)", "856")
        col3.metric("Anomalias CEAP", "51")

    elif choice == "Atlas das Frentes":
        st.subheader("🎯 Marco 1: Diversidade nas Frentes Parlamentares")
        df_ranking = pd.read_parquet(os.path.join(gold_path, 'gold_deputados_ativos.parquet'))
        
        st.write("Top 10 Deputados com maior participação:")
        fig = px.bar(df_ranking.head(10), x='total_frentes', y='nome', color='siglaPartido', orientation='h')
        st.plotly_chart(fig, use_container_width=True)

    elif choice == "Calendário de Eventos":
        st.subheader("📅 Marco 2: Engajamento Legislativo")
        df_presenca = pd.read_parquet(os.path.join(gold_path, 'gold_presenca_ranking.parquet'))
        
        st.write("Assiduidade Parlamentar:")
        st.dataframe(df_presenca, use_container_width=True)

    elif choice == "Auditoria CEAP":
        st.subheader("🔍 Marco 3: Auditoria de Gastos (Outliers)")
        df_anomalias = pd.read_parquet(os.path.join(gold_path, 'gold_gastos_anomalias.parquet'))
        
        st.warning("⚠️ Despesas identificadas com Z-Score > 3 (Estatisticamente anômalas)")
        st.write("Top Anomalias Detectadas:")
        st.table(df_anomalias[['nome', 'tipoDespesa', 'valorLiquido', 'z_score']].head(10))
        
        fig_scatter = px.scatter(df_anomalias, x='valorLiquido', y='z_score', hover_data=['nome', 'tipoDespesa'], color='siglaUf')
        st.plotly_chart(fig_scatter, use_container_width=True)

if __name__ == "__main__":
    main()