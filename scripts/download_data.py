"""
download_data.py
----------------
Baixa e descompacta os 12 arquivos .csv do período utilizado na análise
(abril de 2025 a março de 2026) diretamente do repositório público da Divvy.

Uso:
    python scripts/download_data.py

Os arquivos .csv serão salvos em data/ na raiz do projeto.
"""

import urllib.request
import zipfile
import os
import sys


BASE_URL   = "https://divvy-tripdata.s3.amazonaws.com"
MESES      = [
    "202504", "202505", "202506", "202507", "202508", "202509",
    "202510", "202511", "202512", "202601", "202602", "202603",
]
DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")


def barra_progresso(baixados, total, largura=40):
    """Exibe uma barra de progresso simples no terminal."""
    proporcao  = baixados / total
    preenchido = int(largura * proporcao)
    barra      = "#" * preenchido + "-" * (largura - preenchido)
    porcentagem = proporcao * 100
    print(f"\r  [{barra}] {porcentagem:5.1f}%  {baixados/1_048_576:.1f} MB", end="", flush=True)


def baixar_arquivo(url, destino):
    """Faz o download de url para destino, exibindo progresso."""
    def progresso(contagem, tamanho_bloco, tamanho_total):
        if tamanho_total > 0:
            barra_progresso(contagem * tamanho_bloco, tamanho_total)

    urllib.request.urlretrieve(url, destino, reporthook=progresso)
    print() 


def descompactar(zip_path, pasta_destino):
    """Extrai apenas os .csv de um arquivo .zip."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        csvs = [name for name in zf.namelist() if name.endswith(".csv") and not name.startswith("__MACOSX")]
        for csv in csvs:
            zf.extract(csv, pasta_destino)
    return len(csvs)


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    total   = len(MESES)
    ok      = 0
    falhas  = []

    print(f"\nCyclistic — Download dos dados ({total} arquivos)\n")

    for i, mes in enumerate(MESES, start=1):
        nome_zip = f"{mes}-divvy-tripdata.zip"
        url      = f"{BASE_URL}/{nome_zip}"
        zip_path = os.path.join(DATA_DIR, nome_zip)

        print(f"[{i:02d}/{total}] {nome_zip}")

        try:
            print(f"  Baixando...")
            baixar_arquivo(url, zip_path)

            print(f"  Descompactando...")
            n_csvs = descompactar(zip_path, DATA_DIR)

            os.remove(zip_path)
            print(f"  OK: {n_csvs} arquivo(s) .csv extraído(s)\n")
            ok += 1

        except Exception as e:
            print(f"  ERRO: Falha: {e}\n")
            falhas.append(nome_zip)
            if os.path.exists(zip_path):
                os.remove(zip_path)

    print("-" * 50)
    print(f"Concluído: {ok}/{total} arquivos baixados com sucesso.")

    if falhas:
        print(f"\nArquivos com falha ({len(falhas)}):")
        for f in falhas:
            print(f"  * {f}")
        print("\nVerifique sua conexão e tente novamente.")
        sys.exit(1)
    else:
        print("\nTodos os arquivos estão em data/. Você já pode executar os notebooks.")


if __name__ == "__main__":
    main()
