import pandas as pd
import os
import logging
from datetime import datetime

# English: Configuring logging to prevent terminal encoding failures on Windows
# Português: Configurando o logging para evitar falhas de codificação de terminal no Windows
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GoldEventos:
    # Created by / Autoria: Alex Lourenço (FIHD)
    # English: Gold layer generation for legislative events, calculating attendance rates and activity density.
    # Português: Geração da camada Gold para eventos legislativos, calculando taxas de presença e densidade de atividade.

    def __init__(self):
        # English: Dynamic cross-platform paths
        # Português: Caminhos dinâmicos multiplataforma
        self.silver_path = os.path.join('data', 'silver', 'silver_presenca_eventos.parquet')
        self.gold_path = os.path.join('data', 'gold')
        os.makedirs(self.gold_path, exist_ok=True)

    def generate_analytics(self):
        # English: Aggregates silver data into high-level business metrics for the legislative calendar.
        # Português: Agrega dados da silver em métricas de negócio de alto nível para o calendário legislativo.
        logging.info("--- INICIANDO GERAÇÃO GOLD: EVENTOS E PRESENÇAS ---")
        
        if not os.path.exists(self.silver_path):
            logging.warning(f"[WARNING] Arquivo Silver não encontrado em: {self.silver_path}. Abortando.")
            return

        try:
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

            # English: Exporting Gold Assets
            # Português: Exportação dos Ativos Gold
            ranking_path = os.path.join(self.gold_path, 'gold_presenca_ranking.parquet')
            densidade_path = os.path.join(self.gold_path, 'gold_evento_densidade_semanal.parquet')
            
            presenca_deputado.to_parquet(ranking_path, index=False)
            densidade_semanal.to_parquet(densidade_path, index=False)
            
            logging.info("[SUCCESS] Resultados Camada Gold: Eventos gerados com sucesso.")
            logging.info(f"[INFO] Arquivo exportado: {ranking_path}")
            logging.info(f"[INFO] Arquivo exportado: {densidade_path}")

        except Exception as e:
            # English: Error handling during Gold layer generation
            # Português: Tratamento de erro durante a geração da camada Gold
            logging.error(f"[ERROR] Erro fatal durante a geração dos agregados Gold de Eventos: {e}")
            raise e

if __name__ == "__main__":
    gold = GoldEventos()
    gold.generate_analytics()