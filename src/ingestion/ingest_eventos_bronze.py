import requests
import pandas as pd
from datetime import datetime
import os

"""
English: Ingests legislative events (sessions, hearings, etc.) into the Bronze layer.
Português: Ingere eventos legislativos (sessões, audiências, etc.) na camada Bronze.
"""

class EventosBronzeIngestion:
    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.output_path = r'data\bronze\eventos'
        os.makedirs(self.output_path, exist_ok=True)

    def ingest(self):
        """
        English: Fetches events for the current year with pagination handling.
        Português: Coleta eventos do ano atual gerenciando a paginação.
        """
        print("Iniciando coleta de Eventos Legislativos (2026)...")
        endpoint = "eventos"
        # English: Filtering by the year 2026 as per project context
        # Português: Filtrando pelo ano de 2026 conforme o contexto do projeto
        params = {
            'dataInicio': '2026-01-01',
            'ordem': 'ASC',
            'ordenarPor': 'dataHoraInicio',
            'itens': 100
        }
        
        all_events = []
        page = 1
        
        while True:
            params['pagina'] = page
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            
            if response.status_code != 200:
                break
                
            data = response.json().get('dados', [])
            if not data:
                break
                
            all_events.extend(data)
            page += 1
            
        if all_events:
            df = pd.DataFrame(all_events)
            df['extraction_at'] = datetime.now()
            df['source_system'] = 'API_CAMARA_V2'
            
            file_name = f"eventos_2026_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
            df.to_parquet(os.path.join(self.output_path, file_name), index=False)
            print(f"Sucesso! {len(all_events)} eventos salvos na Bronze.")

if __name__ == "__main__":
    ingestor = EventosBronzeIngestion()
    ingestor.ingest()

# English: Suggested Commit / Português: Commit Sugerido:
# FEAT: INGESTÃO DE EVENTOS LEGISLATIVOS NA CAMADA BRONZE