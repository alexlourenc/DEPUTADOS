import pandas as pd
import requests
import os
from datetime import datetime
import glob
import time

"""
English: Ingests attendance data for each legislative event to calculate participation rates.
Português: Ingere dados de presença para cada evento legislativo para calcular taxas de participação.
"""

class PresencaEventosIngestion:
    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.input_path = r'data\bronze\eventos'
        self.output_path = r'data\bronze\presenca_eventos'
        os.makedirs(self.output_path, exist_ok=True)

    def get_event_ids(self) -> list:
        """
        English: Retrieves event IDs from the latest ingested events file.
        Português: Recupera IDs de eventos do último arquivo de eventos ingerido.
        """
        files = glob.glob(os.path.join(self.input_path, '*.parquet'))
        if not files:
            return []
        latest_file = max(files, key=os.path.getctime)
        df = pd.read_parquet(latest_file)
        return df['id'].tolist()

    def ingest_presencas(self):
        """
        English: Iterates through event IDs to fetch the list of attending deputies.
        Português: Itera pelos IDs de eventos para coletar a lista de deputados presentes.
        """
        event_ids = self.get_event_ids()
        all_presencas = []
        
        print(f"--- INICIANDO COLETA DE PRESENÇAS PARA {len(event_ids)} EVENTOS ---")

        for idx, event_id in enumerate(event_ids):
            if idx % 100 == 0:
                print(f"Processando evento {idx} de {len(event_ids)}...")

            try:
                # English: Endpoint for deputies present in a specific event
                # Português: Endpoint para deputados presentes em um evento específico
                response = requests.get(f"{self.base_url}/eventos/{event_id}/deputados")
                if response.status_code == 200:
                    deputados = response.json().get('dados', [])
                    for dep in deputados:
                        dep['id_evento'] = event_id # FK for Silver layer
                        all_presencas.append(dep)
                
                time.sleep(0.05) # Polite scraping
            except Exception as e:
                print(f"Erro no evento {event_id}: {e}")

        if all_presencas:
            df_presenca = pd.DataFrame(all_presencas)
            df_presenca['extraction_at'] = datetime.now()
            df_presenca['source_system'] = 'API_CAMARA_V2'
            
            file_name = f"presenca_eventos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            df_presenca.to_parquet(os.path.join(self.output_path, file_name), index=False)
            print(f"[SUCCESS] {len(all_presencas)} registros de presença salvos na Bronze.")

if __name__ == "__main__":
    ingestor = PresencaEventosIngestion()
    ingestor.ingest_presencas()