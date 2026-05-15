import pandas as pd
import os
from datetime import datetime

"""
English: Gold layer generation for legislative events, calculating attendance rates and activity density.
Português: Geração da camada Gold para eventos legislativos, calculando taxas de presença e densidade de atividade.
"""

class GoldEventos:
    def __init__(self):
        self.silver_path = r'data\silver\silver_presenca_eventos.parquet'
        self.gold_path = r'data\gold'
        os.makedirs(self.gold_path, exist_ok=True)

    def generate_analytics(self):
        """
        English: Aggregates silver data into high-level business metrics for the legislative calendar.
        Português: Agrega dados da silver em métricas de negócio de alto nível para o calendário legislativo.
        """
        if not os.path.exists(self.silver_path):
            return

        df = pd.read_parquet(self.silver_path)
        
        # English: 1. Attendance Rate per Deputy
        # Português: 1. Taxa de Presença por Deputado
        presenca_deputado = df.groupby(['nome', 'siglaPartido', 'siglaUf']).size().reset_index(name='total_presencas')
        presenca_deputado = presenca_deputado.sort_values(by='total_presencas', ascending=False)

        # English: 2. Weekly Event Density
        # Português: 2. Densidade de Eventos por Semana
        df['data_evento'] = pd.to_datetime(df['data_evento'])
        df['semana_ano'] = df['data_evento'].dt.isocalendar().week
        
        densidade_semanal = df.groupby(['semana_ano', 'tipo_evento']).size().reset_index(name='qtd_presencas')

        # English: 3. Attendance by Event Type
        # Português: 3. Presença por Tipo de Evento
        presenca_tipo = df.groupby('tipo_evento').size().reset_index(name='total_presencas')

        # English: Exporting Gold Assets
        # Português: Exportação dos Ativos Gold
        presenca_deputado.to_parquet(os.path.join(self.gold_path, 'gold_presenca_ranking.parquet'), index=False)
        densidade_semanal.to_parquet(os.path.join(self.gold_path, 'gold_evento_densidade_semanal.parquet'), index=False)
        
        print("--- RESULTADOS CAMADA GOLD: EVENTOS ---")
        print(f"Top 5 Deputados mais presentes em eventos:\n{presenca_deputado.head(5)}")
        print(f"\nResumo de presenças por tipo de evento:\n{presenca_tipo}")

if __name__ == "__main__":
    gold = GoldEventos()
    gold.generate_analytics()