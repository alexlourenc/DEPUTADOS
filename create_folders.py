import os

# English: Automation script for project scaffolding in a Windows environment.
# Português: Script de automação para estrutura inicial do projeto em ambiente Windows.

def create_scaffolding():
    # English: Project directory tree based on Medallion Architecture
    # Português: Árvore de diretórios do projeto baseada na Arquitetura Medallion
    base_path = os.getcwd()
    structure = [
        r'data\bronze',
        r'data\silver',
        r'data\gold',
        r'notebooks',
        r'src\ingestion',
        r'src\transform',
        r'src\utils',
        r'docs\runbooks',
        r'tests'
    ]

    print(f"--- INICIANDO SETUP DE PASTAS EM: {base_path} ---")

    for folder in structure:
        path = os.path.join(base_path, folder)
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"[SUCCESS] Criado: {folder}")
            else:
                print(f"[INFO] Já existente: {folder}")
        except Exception as e:
            print(f"[ERROR] Falha ao criar {folder}: {e}")

if __name__ == "__main__":
    create_scaffolding()