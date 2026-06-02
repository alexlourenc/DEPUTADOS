import streamlit as st
import pandas as pd
import plotly.express as px
import os

# English: Executive page layout configuration must be the first command executed
# Português: A configuração executiva do layout da página deve ser o primeiro comando executado
st.set_page_config(page_title="Atlas Legislativo - Dashboard", layout="wide")

def main():
    # Created by / Autoria: Alex Lourenço (FIHD)
    st.title("🏛️ Atlas Legislativo: Inteligência de Dados")
    st.markdown("---")

    # English: Dynamic cross-platform paths
    # Português: Caminhos dinâmicos multiplataforma
    gold_path = os.path.join('data', 'gold')

    # English: Sidebar for navigation
    # Português: Barra lateral para navegação
    menu = ["Resumo Geral", "Atlas das Frentes", "Calendário de Eventos", "Auditoria CEAP"]
    choice = st.sidebar.selectbox("Navegar por Marco", menu)

    if choice == "Resumo Geral":
        st.subheader("Visão Geral do Projeto")
        st.info("Este dashboard consome dados processados via Arquitetura Medallion (Bronze -> Silver -> Gold).")
        
        # English: High-level KPI metrics
        # Português: Métricas de KPI de alto nível
        col1, col2, col3 = st.columns(3)
        col1.metric("Frentes Analisadas", "1.227")
        col2.metric("Eventos (2026)", "856")
        col3.metric("Anomalias CEAP", "51")

    elif choice == "Atlas das Frentes":
        st.subheader("🎯 Marco 1: Diversidade nas Frentes Parlamentares")
        file_path = os.path.join(gold_path, 'gold_deputados_ativos.parquet')
        
        if os.path.exists(file_path):
            df_ranking = pd.read_parquet(file_path)
            st.write("Top 10 Deputados com maior participação:")
            
            # English: Horizontal bar chart for readability
            # Português: Gráfico de barras horizontais para legibilidade
            fig = px.bar(df_ranking.head(10), x='total_frentes', y='nome', color='siglaPartido', orientation='h')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Arquivo da camada Gold correspondente às Frentes Parlamentares não encontrado.")

    elif choice == "Calendário de Eventos":
        st.subheader("📅 Marco 2: Engajamento Legislativo")
        file_path = os.path.join(gold_path, 'gold_presenca_ranking.parquet')
        
        if os.path.exists(file_path):
            df_presenca = pd.read_parquet(file_path)
            st.write("Assiduidade Parlamentar:")
            st.dataframe(df_presenca, use_container_width=True)
        else:
            st.warning("⚠️ Arquivo da camada Gold correspondente ao Calendário de Eventos não encontrado.")

    elif choice == "Auditoria CEAP":
        st.subheader("🔍 Marco 3: Auditoria de Gastos (Outliers)")
        file_path = os.path.join(gold_path, 'gold_gastos_anomalias.parquet')
        
        if os.path.exists(file_path):
            df_anomalias = pd.read_parquet(file_path)
            st.warning("⚠️ Despesas identificadas com Z-Score > 3 (Estatisticamente anômalas)")
            st.write("Top Anomalias Detectadas:")
            st.table(df_anomalias[['nome', 'tipoDespesa', 'valorLiquido', 'z_score']].head(10))
            
            # English: Scatter plot for outlier visualization
            # Português: Gráfico de dispersão para visualização de outliers
            fig_scatter = px.scatter(df_anomalias, x='valorLiquido', y='z_score', hover_data=['nome', 'tipoDespesa'], color='siglaUf')
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("⚠️ Arquivo da camada Gold correspondente à Auditoria CEAP não encontrado.")

if __name__ == "__main__":
    main()