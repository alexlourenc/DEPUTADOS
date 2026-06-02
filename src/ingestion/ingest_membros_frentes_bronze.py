import pandas as pd
import requests
import os
from datetime import datetime
import glob
import time

"""
English: Script to ingest members of each Parliamentary Front by iterating through collected Front IDs.
Português: Script para ingerir membros de cada Frente Parlamentar iterando pelos IDs das frentes coletadas.
"""

class BronzeMembrosIngestion:
    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.input_path = r'data\bronze\frentes'
        self.output_path = r'data\bronze\membros_frentes'
        os.makedirs(self.output_path, exist_ok=True)

    def get_frente_ids(self) -> list:
        """
        English: Reads the latest ingested fronts file to get IDs.
        Português: Lê o último arquivo de frentes ingerido para obter os IDs.
        """
        list_of_files = glob.glob(os.path.join(self.input_path, '*.parquet'))
        if not list_of_files:
            return []
        
        latest_file = max(list_of_files, key=os.path.getctime)
        df = pd.read_parquet(latest_file)
        return df['id'].tolist()

    def ingest_membros(self):
        frente_ids = self.get_frente_ids()
        all_membros = []
        
        print(f"Iniciando coleta de membros para {len(frente_ids)} frentes...")

        for idx, f_id in enumerate(frente_ids):
            # English: Progress tracking / Português: Acompanhamento de progresso
            if idx % 50 == 0:
                print(f"Processando frente {idx} de {len(frente_ids)}...")

            try:
                response = requests.get(f"{self.base_url}/frentes/{f_id}/membros")
                if response.status_code == 200:
                    membros = response.json().get('dados', [])
                    for m in membros:
                        m['id_frente'] = f_id # FK for Silver layer / FK para camada Silver
                        all_membros.append(m)
                
                # English: Respect API rate limits / Português: Respeitar limites da API
                time.sleep(0.1)
            except Exception as e:
                print(f"Erro no ID {f_id}: {e}")

        if all_membros:
            df_membros = pd.DataFrame(all_membros)
            df_membros['extraction_at'] = datetime.now()
            df_membros['source_system'] = 'API_CAMARA_V2'
            
            file_name = f"membros_frentes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            df_membros.to_parquet(os.path.join(self.output_path, file_name), index=False)
            print(f"Sucesso! {len(all_membros)} membros de frentes salvos na Bronze.")

if __name__ == "__main__":
    ingestor = BronzeMembrosIngestion()
    ingestor.ingest_membros()

# English: Suggested Commit / Português: Commit Sugerido:
# FEAT: INGESTÃO DE MEMBROS DAS FRENTES PARLAMENTARES NA CAMADA BRONZE