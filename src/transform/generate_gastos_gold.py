import pandas as pd
import os
import logging
import numpy as np
from datetime import datetime

# English: Configuring logging to prevent terminal encoding failures on Windows
# Português: Configurando o logging para evitar falhas de codificação de terminal no Windows
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GoldGastos:
    # Created by / Autoria: Alex Lourenço (FIHD)
    # English: Gold layer for CEAP auditing, implementing Z-Score for anomaly detection in expenses.
    # Português: Camada Gold para auditoria da CEAP, implementando Z-Score para detecção de anomalias em despesas.

    def __init__(self):
        # English: Dynamic cross-platform paths
        # Português: Caminhos dinâmicos multiplataforma
        self.silver_path = os.path.join('data', 'silver', 'silver_gastos_ceap.parquet')
        self.gold_path = os.path.join('data', 'gold')
        os.makedirs(self.gold_path, exist_ok=True)

    def generate_audit(self):
        # English: Calculates total spending per deputy and identifies statistical outliers by expense type.
        # Português: Calcula o gasto total por deputado e identifica outliers estatísticos por tipo de despesa.
        logging.info("--- INICIANDO GERAÇÃO GOLD: AUDITORIA FINANCEIRA CEAP ---")
        
        if not os.path.exists(self.silver_path):
            logging.warning(f"[WARNING] Arquivo Silver não encontrado em: {self.silver_path}. Abortando.")
            return

        try:
            df = pd.read_parquet(self.silver_path)

            # English: 1. Spending Ranking per Deputy
            # Português: 1. Ranking de Gastos por Deputado
            ranking_gastos = df.groupby(['nome', 'siglaPartido', 'siglaUf'])['valorLiquido'].sum().reset_index()
            ranking_gastos = ranking_gastos.sort_values(by='valorLiquido', ascending=False)

            # English: 2. Anomaly Detection (Z-Score) per Category
            # Português: 2. Detecção de Anomalias (Z-Score) por Categoria
            logging.info("[INFO] Calculando desvios estatísticos (Z-Score) por categoria...")
            
            # English: Grouping by expense type to compute mean and standard deviation
            # Português: Agrupamos por tipo de despesa para calcular média e desvio padrão
            stats = df.groupby('tipoDespesa')['valorLiquido'].agg(['mean', 'std']).reset_index()
            df_audit = pd.merge(df, stats, on='tipoDespesa')
            
            # English: Z-Score calculation: (Value - Mean) / Standard Deviation
            # Português: Cálculo do Z-Score: (Valor - Média) / Desvio Padrão
            # Adding small epsilon to standard deviation to avoid division by zero
            df_audit['z_score'] = (df_audit['valorLiquido'] - df_audit['mean']) / (df_audit['std'] + 1e-9)
            
            # English: Filtering significant anomalies (Z-Score > 3)
            # Português: Filtramos apenas as anomalias significativas (Z-Score > 3)
            anomalias = df_audit[df_audit['z_score'] > 3].copy()
            anomalias = anomalias.sort_values(by='z_score', ascending=False)

            # English: 3. Exporting Gold Assets
            # Português: 3. Exportação dos Ativos Gold
            ranking_output = os.path.join(self.gold_path, 'gold_gastos_ranking.parquet')
            anomalias_output = os.path.join(self.gold_path, 'gold_gastos_anomalias.parquet')
            
            ranking_gastos.to_parquet(ranking_output, index=False)
            anomalias.to_parquet(anomalias_output, index=False)
            
            logging.info("--- [SUCCESS] RESULTADOS CAMADA GOLD: AUDITORIA CEAP ---")
            logging.info(f"[INFO] Registros processados no ranking de investimentos: {len(ranking_gastos)}")
            logging.info(f"[INFO] Total de anomalias críticas detectadas (Z-Score > 3): {len(anomalias)}")
            
            if not anomalias.empty:
                maior_valor = anomalias.iloc[0]['valorLiquido']
                maior_cat = anomalias.iloc[0]['tipoDespesa']
                logging.info(f"[INFO] Maior desvio identificado: R$ {maior_valor:.2f} ({maior_cat})")

        except Exception as e:
            # English: Error handling during execution
            # Português: Tratamento de erro durante a execução
            logging.error(f"[ERROR] Erro fatal durante a geração dos agregados Gold de Gastos: {e}")
            raise e

if __name__ == "__main__":
    gold = GoldGastos()
    gold.generate_audit()