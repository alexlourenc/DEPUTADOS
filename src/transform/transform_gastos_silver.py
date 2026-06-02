import pandas as pd
import glob
import os
import logging
from datetime import datetime

# English: Configuring logging to prevent terminal encoding failures on Windows
# Português: Configurando o logging para evitar falhas de codificação de terminal no Windows
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SilverGastosTransformation:
    # Created by / Autoria: Alex Lourenço (FIHD)
    # English: Consolidated Silver transformation for expenses, ensuring deputy names and political metadata are correctly joined.
    # Português: Transformação Silver consolidada para despesas, garantindo que nomes de deputados e metadados políticos sejam unidos corretamente.

    def __init__(self):
        # English: Dynamic cross-platform paths
        # Português: Caminhos dinâmicos multiplataforma
        self.bronze_path = os.path.join('data', 'bronze')
        self.silver_path = os.path.join('data', 'silver')
        os.makedirs(self.silver_path, exist_ok=True)

    def get_latest_file(self, entity: str) -> str:
        # English: Retrieves the most recent parquet file for the specified entity.
        # Português: Recupera o arquivo parquet mais recente para a entidade especificada.
        files = glob.glob(os.path.join(self.bronze_path, entity, '*.parquet'))
        return max(files, key=os.path.getctime) if files else None

    def process_gastos(self):
        # English: Normalizes spending values and performs a robust join with the deputy master list.
        # Português: Normaliza valores de gastos e realiza um join robusto com a lista mestre de deputados.
        logging.info("--- INICIANDO TRANSFORMAÇÃO SILVER: GASTOS (CEAP) ---")
        
        path_gastos = self.get_latest_file('gastos')
        path_deputados = self.get_latest_file('deputados')

        if not path_gastos or not path_deputados:
            logging.warning("[WARNING] Arquivos de gastos ou deputados não encontrados na camada Bronze. Abortando.")
            return

        try:
            df_gastos = pd.read_parquet(path_gastos)
            df_deputados = pd.read_parquet(path_deputados)

            # English: Ensure numeric integrity for currency values
            # Português: Garante integridade numérica para valores monetários
            df_gastos['valorLiquido'] = pd.to_numeric(df_gastos['valorLiquido'], errors='coerce').fillna(0)
            
            # English: Prepare master deputy list with clear column names
            # Português: Prepara lista mestre de deputados com nomes de colunas claros
            df_dep_master = df_deputados[['id', 'nome', 'siglaPartido', 'siglaUf']].copy()
            df_dep_master.columns = ['id_deputado_mestre', 'nome', 'siglaPartido', 'siglaUf']

            # English: Join spending data with deputy names and metadata
            # Português: Une dados de gastos com nomes e metadados dos deputados
            df_silver = pd.merge(
                df_gastos, 
                df_dep_master, 
                left_on='id_deputado', 
                right_on='id_deputado_mestre', 
                how='left'
            )

            # English: Adding processing timestamp
            # Português: Adicionando carimbo de tempo de processamento
            df_silver['processing_at'] = datetime.now()
            
            output_file = os.path.join(self.silver_path, 'silver_gastos_ceap.parquet')
            df_silver.to_parquet(output_file, index=False)
            
            logging.info(f"[SUCCESS] Camada Silver Gastos atualizada em {output_file}. {len(df_silver)} registros.")
            
        except Exception as e:
            # English: Error handling during transformation
            # Português: Tratamento de erro durante a transformação
            logging.error(f"[ERROR] Erro fatal durante o processamento da Silver de Gastos: {e}")
            raise e

if __name__ == "__main__":
    transformer = SilverGastosTransformation()
    transformer.process_gastos()