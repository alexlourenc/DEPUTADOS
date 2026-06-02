import requests
import pandas as pd
from datetime import datetime
import os

"""
English: Script to ingest Parliamentary Fronts data from the Chamber of Deputies API to the Bronze layer.
Português: Script para ingerir dados das Frentes Parlamentares da API da Câmara para a camada Bronze.
"""

class BronzeIngestion:
    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.output_path = r'data\bronze\frentes'
        os.makedirs(self.output_path, exist_ok=True)

    def fetch_api_data(self, endpoint: str) -> list:
        """
        English: Fetches data from the API handling basic pagination.
        Português: Coleta dados da API gerenciando a paginação básica.
        """
        all_results = []
        page = 1
        print(f"Iniciando coleta de: {endpoint}")
        
        while True:
            params = {'pagina': page, 'itens': 100}
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            
            if response.status_code != 200:
                print(f"Erro na página {page}: {response.status_code}")
                break
                
            data = response.json().get('dados', [])
            if not data:
                break
                
            all_results.extend(data)
            page += 1
            
        print(f"Total de registros coletados: {len(all_results)}")
        return all_results

    def save_to_bronze(self, data: list, entity_name: str):
        """
        English: Saves raw data to Parquet format with audit columns.
        Português: Salva os dados brutos em formato Parquet com colunas de auditoria.
        """
        if not data:
            print("Nenhum dado para salvar.")
            return

        df = pd.DataFrame(data)
        
        # English: Adding audit metadata / Português: Adicionando metadados de auditoria
        df['extraction_at'] = datetime.now()
        df['source_system'] = 'API_CAMARA_V2'
        
        file_name = f"{entity_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        full_path = os.path.join(self.output_path, file_name)
        
        df.to_parquet(full_path, index=False)
        print(f"Arquivo salvo com sucesso em: {full_path}")

if __name__ == "__main__":
    ingestor = BronzeIngestion()
    
    # English: Step 1 - Ingest Parliamentary Fronts
    # Português: Passo 1 - Ingerir Frentes Parlamentares
    frentes_data = ingestor.fetch_api_data("frentes")
    ingestor.save_to_bronze(frentes_data, "frentes_parlamentares")

# English: Suggested Commit / Português: Commit Sugerido:
# FEAT: IMPLEMENTAÇÃO DA INGESTÃO DA CAMADA BRONZE PARA FRENTES PARLAMENTARES