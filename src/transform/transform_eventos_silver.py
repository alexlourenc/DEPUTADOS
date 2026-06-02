import pandas as pd
import glob
import os
from datetime import datetime

# English: Consolidated Silver transformation for Events and Attendance, ensuring clean column schemas.
# Português: Transformação Silver consolidada para Eventos e Presença, garantindo esquemas de colunas limpos.

class SilverEventosTransformation:
    def __init__(self):
        # English: Cross-platform paths configuration
        # Português: Configuração de caminhos multiplataforma
        self.bronze_path = os.path.join('data', 'bronze')
        self.silver_path = os.path.join('data', 'silver')
        os.makedirs(self.silver_path, exist_ok=True)

    def get_latest_file(self, entity: str) -> str:
        # English: Returns the most recent file for the specified entity.
        # Português: Retorna o arquivo mais recente para a entidade especificada.
        files = glob.glob(os.path.join(self.bronze_path, entity, '*.parquet'))
        return max(files, key=os.path.getctime) if files else None

    def process_eventos_presenca(self):
        # English: Normalizes event and attendance data into a trusted single table.
        # Português: Normaliza dados de eventos e presença em uma tabela única confiável.
        print("--- INICIANDO TRANSFORMAÇÃO SILVER: EVENTOS E PRESENÇAS ---")
        
        path_eventos = self.get_latest_file('eventos')
        path_presenca = self.get_latest_file('presenca_eventos')
        path_deputados = self.get_latest_file('deputados')

        if not all([path_eventos, path_presenca, path_deputados]):
            print("[ERROR] Arquivos da camada Bronze ausentes. Execute a ingestão primeiro.")
            return

        df_eventos = pd.read_parquet(path_eventos)
        df_presenca = pd.read_parquet(path_presenca)
        df_deputados = pd.read_parquet(path_deputados)

        # English: Clean attendance data by removing existing party/uf columns to avoid merge conflicts
        # Português: Limpa dados de presença removendo colunas de partido/uf existentes para evitar conflitos de merge
        cols_to_drop = ['siglaPartido', 'siglaUf', 'uriPartido']
        df_presenca_clean = df_presenca.drop(columns=[c for c in cols_to_drop if c in df_presenca.columns])

        # English: Enrich with Event metadata
        # Português: Enriquece com metadados do Evento
        df_eventos_sub = df_eventos[['id', 'dataHoraInicio', 'descricaoTipo']].copy()
        df_eventos_sub.columns = ['id_evento', 'data_evento', 'tipo_evento']

        df_silver = pd.merge(df_presenca_clean, df_eventos_sub, on='id_evento', how='inner')

        # English: Final enrichment with Master Deputy list for guaranteed Schema consistency
        # Português: Enriquecimento final com a lista mestre de Deputados para consistência de esquema garantida
        df_dep_master = df_deputados[['id', 'siglaPartido', 'siglaUf']].rename(columns={'id': 'id_dep_master'})
        
        df_silver = pd.merge(df_silver, df_dep_master, left_on='id', right_on='id_dep_master', how='left')

        # English: Adding processing timestamp
        # Português: Adicionando carimbo de tempo de processamento da Silver
        df_silver['processing_at'] = datetime.now()
        
        output_file = os.path.join(self.silver_path, 'silver_presenca_eventos.parquet')
        df_silver.to_parquet(output_file, index=False)
        
        print(f"[SUCCESS] Silver Eventos consolidada. {len(df_silver)} registros processados.")

if __name__ == "__main__":
    transformer = SilverEventosTransformation()
    transformer.process_eventos_presenca()