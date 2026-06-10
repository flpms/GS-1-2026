"""
Pacote RAG — Assistente para a Nova Economia Espacial.

GS 2026.1 — Disciplina 05: Generative AI & Advanced Nets

Pipeline:
    ingest      -> lê PDFs e divide em chunks
    embeddings  -> gera vetores (paraphrase-multilingual-MiniLM-L12-v2)
    vectorstore -> índice FAISS (IndexFlatIP) para recuperação
    generate    -> resposta final via llama3.2 (Ollama)
"""

from .ingest import Chunk, carregar_corpus
from .vectorstore import VectorStore, construir_e_salvar
from .generate import gerar_resposta, verificar_ollama

__all__ = [
    "Chunk",
    "carregar_corpus",
    "VectorStore",
    "construir_e_salvar",
    "gerar_resposta",
    "verificar_ollama",
]
