import pandas as pd
import glob
import os
from datetime import datetime

"""
English: Silver transformation for CEAP expenses, handling data types and merging deputy metadata.
Português: Transformação Silver para despesas CEAP, tratando tipos de dados e unindo metadados dos deputados.
"""

class SilverGastosTransformation:
    def __init__(self):
        self.bronze_path = r'data\bronze'
        self.silver_path = r'data\silver'
        os.makedirs(self.silver_path, exist_ok=True)

    def get_latest_file(self, entity: str) -> str:
        """
        English: Retrieves the most recent parquet file for the entity.
        Português: Recupera o arquivo parquet mais recente para a entidade.
        """
        files = glob.glob(os.path.join(self.bronze_path, entity, '*.parquet'))
        return max(files, key=os.path.getctime) if files else None

    def process_gastos(self):
        """
        English: Cleans expense values and enriches with party/state information for anomaly detection.
        Português: Limpa valores de despesas e enriquece com info de partido/estado para detecção de anomalias.
        """
        print("--- INICIANDO TRANSFORMAÇÃO SILVER: GASTOS CEAP ---")
        
        path_gastos = self.get_latest_file('gastos')
        path_deputados = self.get_latest_file('deputados')

        if not path_gastos or not path_deputados:
            return

        df_gastos = pd.read_parquet(path_gastos)
        df_deputados = pd.read_parquet(path_deputados)

        # English: Ensure numeric values for calculations
        # Português: Garante valores numéricos para cálculos
        df_gastos['valorLiquido'] = pd.to_numeric(df_gastos['valorLiquido'], errors='coerce').fillna(0)
        
        # English: Standardize vendor names
        # Português: Padroniza nomes de fornecedores
        df_gastos['tipoDespesa'] = df_gastos['tipoDespesa'].str.upper().str.strip()
        df_gastos['cnpjCpfFornecedor'] = df_gastos['cnpjCpfFornecedor'].str.replace(r'\D', '', regex=True)

        # English: Join with Master Deputy list
        # Português: Cruzamento com a lista mestre de Deputados
        df_dep_master = df_deputados[['id', 'siglaPartido', 'siglaUf']].rename(columns={'id': 'id_deputado'})
        df_silver = pd.merge(df_gastos, df_dep_master, on='id_deputado', how='left')

        df_silver['processing_at'] = datetime.now()
        
        output_file = os.path.join(self.silver_path, 'silver_gastos_ceap.parquet')
        df_silver.to_parquet(output_file, index=False)
        
        print(f"✔ Sucesso: Camada Silver de Gastos gerada com {len(df_silver)} registros.")

if __name__ == "__main__":
    transformer = SilverGastosTransformation()
    transformer.process_gastos()