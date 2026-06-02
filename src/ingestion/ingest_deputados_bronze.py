import requests
import pandas as pd
from datetime import datetime
import os

"""
English: Ingests the complete list of deputies to serve as a master dimension in the Bronze layer.
Português: Ingere a lista completa de deputados para servir como dimensão mestre na camada Bronze.
"""

class DeputadosBronzeIngestion:
    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.output_path = r'data\bronze\deputados'
        os.makedirs(self.output_path, exist_ok=True)

    def ingest(self):
        print("Iniciando coleta da lista mestre de Deputados...")
        # English: Fetching current deputies / Português: Coletando deputados atuais
        endpoint = "deputados"
        params = {'ordem': 'ASC', 'ordenarPor': 'nome'}
        
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            data = response.json().get('dados', [])
            
            if data:
                df = pd.DataFrame(data)
                df['extraction_at'] = datetime.now()
                df['source_system'] = 'API_CAMARA_V2'
                
                file_name = f"deputados_master_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
                df.to_parquet(os.path.join(self.output_path, file_name), index=False)
                print(f"Sucesso! {len(data)} deputados salvos na Bronze.")
        except Exception as e:
            print(f"Erro na ingestão de deputados: {e}")

if __name__ == "__main__":
    ingestor = DeputadosBronzeIngestion()
    ingestor.ingest()

# English: Suggested Commit / Português: Commit Sugerido:
# FEAT: INGESTÃO DA LISTA MESTRE DE DEPUTADOS NA CAMADA BRONZE