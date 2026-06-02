import pandas as pd
import requests
import os
from datetime import datetime
import glob
import time
import logging

# English: Configuring logging to avoid Windows CP1252 encoding errors
# Português: Configurando o logging para evitar erros de encoding CP1252 no Windows
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GastosBronzeIngestion:
    # Created by / Autoria: Alex Lourenço (FIHD)
    # English: Ingests CEAP (Parliamentary Expense) data for each deputy with pagination control.
    # Português: Ingere dados da CEAP (Despesas Parlamentares) para cada deputado com controle de paginação.

    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        
        # English: Cross-platform paths configuration
        # Português: Configuração de caminhos multiplataforma
        self.input_path = os.path.join('data', 'bronze', 'deputados')
        self.output_path = os.path.join('data', 'bronze', 'gastos')
        os.makedirs(self.output_path, exist_ok=True)

    def get_deputado_ids(self) -> list:
        # English: Retrieves IDs of active deputies from the master list
        # Português: Recupera IDs dos deputados ativos da lista mestre
        files = glob.glob(os.path.join(self.input_path, '*.parquet'))
        if not files: 
            return []
        latest_file = max(files, key=os.path.getctime)
        return pd.read_parquet(latest_file)['id'].tolist()

    def ingest_gastos(self):
        # English: Fetches expenses for each deputy for the year 2026
        # Português: Coleta despesas para cada deputado referente ao ano de 2026
        deputado_ids = self.get_deputado_ids()
        all_gastos = []
        total_deputados = len(deputado_ids)
        
        logging.info(f"--- INICIANDO COLETA DE GASTOS CEAP (2026) PARA {total_deputados} DEPUTADOS ---")

        for idx, d_id in enumerate(deputado_ids, 1):
            if idx % 50 == 0 or idx == total_deputados:
                logging.info(f"Processando gastos do deputado {idx} de {total_deputados}...")

            page = 1
            while True:
                params = {'ano': 2026, 'pagina': page, 'itens': 100}
                try:
                    # English: Added strict timeout for API stability
                    # Português: Adicionado timeout estrito para estabilidade da API
                    response = requests.get(f"{self.base_url}/deputados/{d_id}/despesas", params=params, timeout=10)
                    
                    if response.status_code == 200:
                        dados = response.json().get('dados', [])
                        if not dados: 
                            break
                        
                        for gasto in dados:
                            # English: Link key
                            # Português: Chave de ligação
                            gasto['id_deputado'] = d_id  
                            all_gastos.append(gasto)
                        
                        page += 1
                        # English: Pause to respect API rate limits
                        # Português: Pausa para respeitar os limites de taxa da API
                        time.sleep(0.05)
                    else:
                        break
                except Exception as e:
                    # English: Error handling during ingestion
                    # Português: Tratamento de erro durante a ingestão
                    logging.error(f"[ERROR] Erro ao coletar gastos do ID {d_id} na pagina {page}: {e}")
                    break

        if all_gastos:
            # English: Creating DataFrame and adding metadata
            # Português: Criando DataFrame e adicionando metadados
            df = pd.DataFrame(all_gastos)
            df['extraction_at'] = datetime.now()
            df['source_system'] = 'API_CAMARA_V2'
            
            # English: Saving file in Parquet format
            # Português: Salvando arquivo no formato Parquet
            file_name = f"gastos_ceap_2026_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            file_path = os.path.join(self.output_path, file_name)
            df.to_parquet(file_path, index=False)
            logging.info(f"[SUCCESS] {len(all_gastos)} registros de despesas salvos na Bronze em: {file_path}")
        else:
            logging.warning("[INFO] Nenhum registro de gasto foi encontrado para o ano de 2026.")

if __name__ == "__main__":
    ingestor = GastosBronzeIngestion()
    ingestor.ingest_gastos()