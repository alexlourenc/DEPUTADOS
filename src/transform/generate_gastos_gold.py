import pandas as pd
import os
import numpy as np
from datetime import datetime

"""
English: Gold layer for CEAP auditing, implementing Z-Score for anomaly detection in expenses.
Português: Camada Gold para auditoria da CEAP, implementando Z-Score para detecção de anomalias em despesas.
"""

class GoldGastos:
    def __init__(self):
        self.silver_path = r'data\silver\silver_gastos_ceap.parquet'
        self.gold_path = r'data\gold'
        os.makedirs(self.gold_path, exist_ok=True)

    def generate_audit(self):
        """
        English: Calculates total spending per deputy and identifies statistical outliers by expense type.
        Português: Calcula o gasto total por deputado e identifica outliers estatísticos por tipo de despesa.
        """
        if not os.path.exists(self.silver_path):
            return

        df = pd.read_parquet(self.silver_path)

        # 1. Ranking de Gastos por Deputado
        # English: Summary of total investment per deputy
        ranking_gastos = df.groupby(['nome', 'siglaPartido', 'siglaUf'])['valorLiquido'].sum().reset_index()
        ranking_gastos = ranking_gastos.sort_values(by='valorLiquido', ascending=False)

        # 2. Detecção de Anomalias (Z-Score) por Categoria
        # English: Identifying outliers (Z-Score > 3) to flag for manual audit
        print("Calculando desvios estatísticos (Z-Score) por categoria...")
        
        # Agrupamos por tipo de despesa para calcular média e desvio padrão
        stats = df.groupby('tipoDespesa')['valorLiquido'].agg(['mean', 'std']).reset_index()
        df_audit = pd.merge(df, stats, on='tipoDespesa')
        
        # Cálculo do Z-Score: (Valor - Média) / Desvio Padrão
        df_audit['z_score'] = (df_audit['valorLiquido'] - df_audit['mean']) / df_audit['std']
        
        # Filtramos apenas as anomalias significativas
        anomalias = df_audit[df_audit['z_score'] > 3].copy()
        anomalias = anomalias.sort_values(by='z_score', ascending=False)

        # 3. Exportação dos Ativos Gold
        ranking_gastos.to_parquet(os.path.join(self.gold_path, 'gold_gastos_ranking.parquet'), index=False)
        anomalias.to_parquet(os.path.join(self.gold_path, 'gold_gastos_anomalias.parquet'), index=False)
        
        print("--- RESULTADOS CAMADA GOLD: AUDITORIA CEAP ---")
        print(f"Top 5 Maiores Gastadores (2026):\n{ranking_gastos.head(5)}")
        print(f"\nTotal de anomalias detectadas (Z-Score > 3): {len(anomalias)}")
        if not anomalias.empty:
            print(f"Maior anomalia encontrada: R$ {anomalias.iloc[0]['valorLiquido']:.2f} ({anomalias.iloc[0]['tipoDespesa']})")

if __name__ == "__main__":
    gold = GoldGastos()
    gold.generate_audit()