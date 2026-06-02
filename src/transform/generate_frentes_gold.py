import pandas as pd
import os
import logging
from datetime import datetime

# English: Configuring centralized logging / Português: Configurando o logging centralizado
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GoldFrentes:
    # Created by / Autoria: Alex Lourenço (FIHD)
    # English: Gold layer generation with schema validation and data integrity checks.
    # Português: Geração da camada Gold com validação de esquema e verificação de integridade de dados.

    def __init__(self):
        # English: Dynamic cross-platform paths / Português: Caminhos dinâmicos multiplataforma
        self.silver_path = os.path.join('data', 'silver', 'silver_frentes_membros.parquet')
        self.gold_path = os.path.join('data', 'gold')
        os.makedirs(self.gold_path, exist_ok=True)

    def generate_metrics(self):
        # English: Calculates analytical metrics with pre-validation of the Silver dataset.
        # Português: Calcula métricas analíticas com pré-validação do conjunto de dados Silver.
        logging.info("--- INICIANDO GERAÇÃO GOLD: FRENTES PARLAMENTARES E DIVERSIDADE ---")
        
        if not os.path.exists(self.silver_path):
            logging.error(f"[ERROR] Arquivo Silver não encontrado em: {self.silver_path}")
            return

        try:
            df = pd.read_parquet(self.silver_path)

            # English: Ensure required columns exist and remove nulls for aggregation
            # Português: Garante que as colunas necessárias existam e remove nulos para agregação
            required_columns = ['id_frente', 'siglaPartido', 'nome', 'siglaUf']
            available_cols = [c for c in required_columns if c in df.columns]
            
            if 'siglaPartido' not in available_cols:
                logging.error(f"[ERROR] Coluna 'siglaPartido' ausente. Colunas disponíveis: {df.columns.tolist()}")
                return

            # English: Drop rows with missing critical data to avoid KeyError during grouping
            # Português: Descarta linhas com dados críticos ausentes para evitar KeyError no agrupamento
            df_clean = df.dropna(subset=['id_frente', 'siglaPartido'])

            # English: HHI Calculation per front to measure party diversity
            # Português: Cálculo de HHI por frente para medir a diversidade partidária
            party_counts = df_clean.groupby(['id_frente', 'siglaPartido']).size().reset_index(name='count')
            total_members = df_clean.groupby('id_frente').size().reset_index(name='total')
            
            diversity = pd.merge(party_counts, total_members, on='id_frente')
            # Formula: Sum of the squares of the shares / Fórmula: Soma dos quadrados das participações
            diversity['share_sq'] = (diversity['count'] / diversity['total']) ** 2 
            
            hhi = diversity.groupby('id_frente')['share_sq'].sum().reset_index(name='hhi_index')

            # English: Deputy activity ranking (number of active fronts)
            # Português: Ranking de atividade dos deputados (número de frentes ativas)
            deputados_ativos = df_clean.groupby(['nome', 'siglaPartido', 'siglaUf']).size().reset_index(name='total_frentes')
            deputados_ativos = deputados_ativos.sort_values(by='total_frentes', ascending=False)

            # English: Storage of Gold entities
            # Português: Armazenamento das entidades Gold
            hhi_output = os.path.join(self.gold_path, 'gold_frentes_diversidade.parquet')
            deputados_output = os.path.join(self.gold_path, 'gold_deputados_ativos.parquet')

            hhi.to_parquet(hhi_output, index=False)
            deputados_ativos.to_parquet(deputados_output, index=False)
            
            logging.info(f"[SUCCESS] Total de frentes analisadas e exportadas: {len(hhi)}")
            logging.info(f"[INFO] Ativos gravados com sucesso em: {self.gold_path}")

        except Exception as e:
            # English: Error handling
            # Português: Tratamento de erro
            logging.error(f"[ERROR] Falha fatal ao processar métricas da Gold de Frentes: {e}")
            raise e

if __name__ == "__main__":
    gold = GoldFrentes()
    gold.generate_metrics()