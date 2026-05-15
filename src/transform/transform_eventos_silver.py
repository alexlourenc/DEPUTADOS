import pandas as pd
import glob
import os
from datetime import datetime

"""
English: Silver transformation to consolidate events, their details, and deputy attendance.
Português: Transformação Silver para consolidar eventos, seus detalhes e a presença dos deputados.
"""

class SilverEventosTransformation:
    def __init__(self):
        self.bronze_path = r'data\bronze'
        self.silver_path = r'data\silver'
        os.makedirs(self.silver_path, exist_ok=True)

    def get_latest_file(self, entity: str) -> str:
        """
        English: Helper to get the most recent file from Bronze.
        Português: Auxiliar para obter o arquivo mais recente da Bronze.
        """
        files = glob.glob(os.path.join(self.bronze_path, entity, '*.parquet'))
        return max(files, key=os.path.getctime) if files else None

    def process_eventos_presenca(self):
        """
        English: Joins event metadata with attendance records and master deputy list.
        Português: Une metadados de eventos com registros de presença e a lista mestre de deputados.
        """
        print("--- INICIANDO TRANSFORMAÇÃO SILVER: EVENTOS ---")
        
        path_eventos = self.get_latest_file('eventos')
        path_presenca = self.get_latest_file('presenca_eventos')
        path_deputados = self.get_latest_file('deputados')

        if not all([path_eventos, path_presenca, path_deputados]):
            return

        df_eventos = pd.read_parquet(path_eventos)
        df_presenca = pd.read_parquet(path_presenca)
        df_deputados = pd.read_parquet(path_deputados)

        # English: Selecting relevant columns from Events
        # Português: Selecionando colunas relevantes de Eventos
        df_eventos_clean = df_eventos[['id', 'dataHoraInicio', 'descricaoTipo', 'descricao']].copy()
        df_eventos_clean.columns = ['id_evento', 'data_evento', 'tipo_evento', 'descricao_evento']
        
        # English: Convert date string to datetime object
        # Português: Converte a string de data para objeto datetime
        df_eventos_clean['data_evento'] = pd.to_datetime(df_eventos_clean['data_evento']).dt.date

        # English: Join Presence with Event details
        # Português: Cruza Presença com detalhes do Evento
        df_silver = pd.merge(df_presenca, df_eventos_clean, on='id_evento', how='inner')

        # English: Join with Master Deputy list for Party and UF info
        # Português: Cruza com a lista mestre de Deputados para info de Partido e UF
        df_dep_master = df_deputados[['id', 'siglaPartido', 'siglaUf']].rename(columns={'id': 'id_deputado_mestre'})
        df_silver = pd.merge(df_silver, df_dep_master, left_on='id', right_on='id_deputado_mestre', how='left')

        df_silver['processing_at'] = datetime.now()
        
        output_file = os.path.join(self.silver_path, 'silver_presenca_eventos.parquet')
        df_silver.to_parquet(output_file, index=False)
        
        print(f"✔ Sucesso: Camada Silver gerada com {len(df_silver)} registros consolidados.")

if __name__ == "__main__":
    transformer = SilverEventosTransformation()
    transformer.process_eventos_presenca()