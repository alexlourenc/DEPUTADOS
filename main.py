import subprocess
import time

# English: Main orchestrator to execute the full Medallion pipeline in order.
# Português: Orquestrador principal para executar todo o pipeline Medallion em ordem.

def run_script(script_path):
    # English: Executes a single script and captures its output
    # Português: Executa um único script e captura sua saída
    print(f"--- Executing: {script_path} ---")
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"[SUCCESS] {script_path}")
    else:
        print(f"[ERROR] in {script_path}: {result.stderr}")
        
    return result.returncode

def main():
    start_time = time.time()
    
    # English: Pipeline execution sequence respecting architectural dependencies
    # Português: Sequência de execução do pipeline respeitando dependências arquiteturais
    pipeline = [
        # --- INGESTION (BRONZE) ---
        "src/ingestion/ingest_deputados_bronze.py",
        "src/ingestion/ingest_eventos_bronze.py",
        "src/ingestion/ingest_frentes_bronze.py",
        "src/ingestion/ingest_gastos_bronze.py",
        "src/ingestion/ingest_membros_frentes_bronze.py",
        "src/ingestion/ingest_presenca_eventos_bronze.py",
        
        # --- TRANSFORMATION (SILVER) ---
        "src/transform/transform_eventos_silver.py",
        "src/transform/transform_frentes_silver.py",
        "src/transform/transform_gastos_silver.py",
        
        # --- ANALYTICS (GOLD) ---
        "src/transform/generate_eventos_gold.py",
        "src/transform/generate_frentes_gold.py",
        "src/transform/generate_gastos_gold.py"
    ]
    
    for script in pipeline:
        if run_script(script) != 0:
            # English: Halts pipeline if any script fails
            # Português: Interrompe o pipeline se algum script falhar
            print("\n[CRITICAL] Pipeline halted due to error.")
            break
            
    end_time = time.time()
    print(f"\n--- PIPELINE CONCLUÍDO EM {round(end_time - start_time, 2)} SEGUNDOS ---")

if __name__ == "__main__":
    main()