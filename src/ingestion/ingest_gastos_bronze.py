import pandas as pd
import requests
import os
from datetime import datetime
import glob
import time

"""
English: Ingests CEAP (Parliamentary Expense) data for each deputy with pagination control.
Português: Ingere dados da CEAP (Despesas Parlamentares) para cada deputado com controle de paginação.
"""

class GastosBronzeIngestion:
    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.input_path = r'data\bronze\deputados'
        self.output_path = r'data\bronze\gastos'
        os.makedirs(self.output_path, exist_ok=True)

    def get_deputado_ids(self) -> list:
        """
        English: Retrieves IDs of active deputies from the master list.
        Português: Recupera IDs dos deputados ativos da lista mestre.
        """
        files = glob.glob(os.path.join(self.input_path, '*.parquet'))
        if not files: return []
        latest_file = max(files, key=os.path.getctime)
        return pd.read_parquet(latest_file)['id'].tolist()

    def ingest_gastos(self):
        """
        English: Fetches expenses for each deputy for the year 2026.
        Português: Coleta despesas para cada deputado referente ao ano de 2026.
        """
        deputado_ids = self.get_deputado_ids()
        all_gastos = []
        
        print(f"--- INICIANDO COLETA DE GASTOS CEAP (2026) PARA {len(deputado_ids)} DEPUTADOS ---")

        for idx, d_id in enumerate(deputado_ids):
            if idx % 50 == 0:
                print(f"Processando gastos do deputado {idx} de {len(deputado_ids)}...")

            page = 1
            while True:
                params = {'ano': 2026, 'pagina': page, 'itens': 100}
                try:
                    response = requests.get(f"{self.base_url}/deputados/{d_id}/despesas", params=params)
                    if response.status_code == 200:
                        dados = response.json().get('dados', [])
                        if not dados: break
                        
                        for gasto in dados:
                            gasto['id_deputado'] = d_id # Link key
                            all_gastos.append(gasto)
                        
                        page += 1
                        time.sleep(0.05)
                    else:
                        break
                except Exception as e:
                    print(f"Erro no ID {d_id}: {e}")
                    break

        if all_gastos:
            df = pd.DataFrame(all_gastos)
            df['extraction_at'] = datetime.now()
            df['source_system'] = 'API_CAMARA_V2'
            
            file_name = f"gastos_ceap_2026_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            df.to_parquet(os.path.join(self.output_path, file_name), index=False)
            print(f"✔ Sucesso: {len(all_gastos)} registros de despesas salvos na Bronze.")

if __name__ == "__main__":
    ingestor = GastosBronzeIngestion()
    ingestor.ingest_gastos()