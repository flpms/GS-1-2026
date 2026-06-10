"""Constrói o vector database a partir dos PDFs do corpus.

Execute UMA vez (ou sempre que trocar os PDFs):

    python construir_indice.py

Ele lê os PDFs de data/, gera os embeddings, monta o índice FAISS e salva
tudo em indice/. Depois é só rodar a interface com:

    python -m streamlit run app.py
"""

from rag.ingest import construir_passagens
from rag.embeddings import Embedder
from rag.vectorstore import VectorStore


def main():
    print("=" * 60)
    print("Construção do índice — Edifícios Verdes & Net Zero")
    print("=" * 60)

    passagens = construir_passagens("data")

    embedder = Embedder()
    textos = [p["texto"] for p in passagens]
    print("Gerando embeddings das passagens...")
    vetores = embedder.codificar(textos, normalizar=True)

    store = VectorStore()
    store.construir(vetores, passagens)
    store.salvar("indice")

    print("\nPronto! Índice gerado com sucesso.")
    print("Agora rode:  python -m streamlit run app.py")


if __name__ == "__main__":
    main()
