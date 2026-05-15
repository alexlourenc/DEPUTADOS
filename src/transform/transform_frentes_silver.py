import pandas as pd
import glob
import os
from datetime import datetime

"""
English: Silver transformation focusing on resolving column name conflicts after merging.
Português: Transformação Silver focada em resolver conflitos de nomes de colunas após o cruzamento.
"""

class SilverTransformation:
    def __init__(self):
        self.bronze_path = r'data\bronze'
        self.silver_path = r'data\silver'
        os.makedirs(self.silver_path, exist_ok=True)

    def get_latest_file(self, entity: str) -> str:
        """
        English: Fetches the most recent parquet file for processing.
        Português: Coleta o arquivo parquet mais recente para processamento.
        """
        files = glob.glob(os.path.join(self.bronze_path, entity, '*.parquet'))
        return max(files, key=os.path.getctime) if files else None

    def process_frentes_members(self):
        """
        English: Merges and cleans columns, resolving suffixes like _x and _y to a standard schema.
        Português: Une e limpa colunas, resolvendo sufixos como _x e _y para um esquema padrão.
        """
        path_membros = self.get_latest_file('membros_frentes')
        path_deputados = self.get_latest_file('deputados')

        if not path_membros or not path_deputados:
            return

        df_membros = pd.read_parquet(path_membros)
        df_deputados = pd.read_parquet(path_deputados)

        # English: Use deputy master list for party and state ground truth
        # Português: Utiliza a lista mestre de deputados como fonte da verdade para partido e UF
        df_dep_clean = df_deputados[['id', 'siglaPartido', 'siglaUf']].copy()
        
        # English: Drop redundant columns from members before merge to avoid _x/_y
        # Português: Remove colunas redundantes de membros antes do merge para evitar _x/_y
        cols_to_drop = ['siglaPartido', 'siglaUf', 'uriPartido']
        df_membros_clean = df_membros.drop(columns=[c for c in cols_to_drop if c in df_membros.columns])

        df_silver = pd.merge(
            df_membros_clean, 
            df_dep_clean, 
            on='id', 
            how='left'
        )

        df_silver['processing_at'] = datetime.now()
        
        output_file = os.path.join(self.silver_path, 'silver_frentes_membros.parquet')
        df_silver.to_parquet(output_file, index=False)
        
        print(f"✔ Silver consolidada. Colunas finais: {df_silver.columns.tolist()}")

if __name__ == "__main__":
    transformer = SilverTransformation()
    transformer.process_frentes_members()

# English: Suggested Commit / Português: Commit Sugerido:
# FIX: CONSOLIDAÇÃO DE ESQUEMA SILVER PARA ELIMINAÇÃO DE SUFIXOS DUPLICADOS