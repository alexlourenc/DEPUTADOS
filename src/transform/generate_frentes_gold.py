import pandas as pd
import os
from datetime import datetime

"""
English: Gold layer generation with schema validation and data integrity checks.
Português: Geração da camada Gold com validação de esquema e verificação de integridade de dados.
"""

class GoldFrentes:
    def __init__(self):
        self.silver_path = r'data\silver\silver_frentes_membros.parquet'
        self.gold_path = r'data\gold'
        os.makedirs(self.gold_path, exist_ok=True)

    def generate_metrics(self):
        """
        English: Calculates analytical metrics with pre-validation of the Silver dataset.
        Português: Calcula métricas analíticas com pré-validação do conjunto de dados Silver.
        """
        if not os.path.exists(self.silver_path):
            print("Erro: Arquivo Silver não encontrado.")
            return

        df = pd.read_parquet(self.silver_path)

        # English: Ensure required columns exist and remove nulls for aggregation
        # Português: Garante que as colunas necessárias existam e remove nulos para agregação
        required_columns = ['id_frente', 'siglaPartido', 'nome', 'siglaUf']
        available_cols = [c for c in required_columns if c in df.columns]
        
        if 'siglaPartido' not in available_cols:
            print(f"Erro: Coluna 'siglaPartido' ausente. Colunas disponíveis: {df.columns.tolist()}")
            return

        # English: Drop rows with missing critical data to avoid KeyError during grouping
        # Português: Descarta linhas com dados críticos ausentes para evitar KeyError no agrupamento
        df_clean = df.dropna(subset=['id_frente', 'siglaPartido'])

        # English: HHI Calculation per front
        # Português: Cálculo de HHI por frente
        party_counts = df_clean.groupby(['id_frente', 'siglaPartido']).size().reset_index(name='count')
        total_members = df_clean.groupby('id_frente').size().reset_index(name='total')
        
        diversity = pd.merge(party_counts, total_members, on='id_frente')
        diversity['share_sq'] = (diversity['count'] / diversity['total']) ** 2
        
        hhi = diversity.groupby('id_frente')['share_sq'].sum().reset_index(name='hhi_index')

        # English: Deputy activity ranking
        # Português: Ranking de atividade dos deputados
        deputados_ativos = df_clean.groupby(['nome', 'siglaPartido', 'siglaUf']).size().reset_index(name='total_frentes')
        deputados_ativos = deputados_ativos.sort_values(by='total_frentes', ascending=False)

        # English: Storage of Gold entities
        # Português: Armazenamento das entidades Gold
        hhi.to_parquet(os.path.join(self.gold_path, 'gold_frentes_diversidade.parquet'), index=False)
        deputados_ativos.to_parquet(os.path.join(self.gold_path, 'gold_deputados_ativos.parquet'), index=False)
        
        print("--- RESULTADOS CAMADA GOLD ---")
        print(f"Total de frentes analisadas: {len(hhi)}")
        print(f"Top 5 Deputados ativos:\n{deputados_ativos.head(5)}")

if __name__ == "__main__":
    gold = GoldFrentes()
    gold.generate_metrics()

# English: Suggested Commit / Português: Commit Sugerido:
# FEAT: PROCESSAMENTO GOLD COM TRATAMENTO DE INTEGRIDADE DE DADOS