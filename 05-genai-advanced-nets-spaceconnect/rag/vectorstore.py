"""
Módulo do vector store (FAISS).

Cria e consulta um índice FAISS do tipo IndexFlatIP (produto interno).
Como os embeddings são normalizados, o produto interno equivale à
similaridade do cosseno — quanto maior o score, mais relevante o trecho.

O índice e os metadados são salvos em disco para não precisar
reprocessar o corpus a cada execução da aplicação.
"""

from __future__ import annotations

import pickle
from dataclasses import asdict
from pathlib import Path

import faiss
import numpy as np

from .embeddings import gerar_embedding_consulta, gerar_embeddings
from .ingest import Chunk, carregar_corpus

PASTA_INDICE = Path("indice")
ARQ_FAISS = PASTA_INDICE / "corpus.faiss"
ARQ_META = PASTA_INDICE / "metadados.pkl"


class VectorStore:
    """Encapsula o índice FAISS + os metadados dos chunks."""

    def __init__(self, indice: faiss.Index, chunks: list[Chunk]):
        self.indice = indice
        self.chunks = chunks

    # ----------------------------------------------------------------
    # Construção / persistência
    # ----------------------------------------------------------------
    @classmethod
    def construir(cls, pasta_corpus: str | Path = "corpus") -> "VectorStore":
        """Lê o corpus, gera embeddings e constrói o índice FAISS."""
        print("1) Ingestão de documentos")
        chunks = carregar_corpus(pasta_corpus)

        print("\n2) Geração de embeddings")
        textos = [c.texto for c in chunks]
        matriz = gerar_embeddings(textos)

        print("\n3) Construção do índice FAISS (IndexFlatIP)")
        dim = matriz.shape[1]
        indice = faiss.IndexFlatIP(dim)  # produto interno = cosseno (normalizado)
        indice.add(matriz)
        print(f"   Índice criado com {indice.ntotal} vetores (dim={dim})")

        return cls(indice, chunks)

    def salvar(self) -> None:
        """Persiste o índice e os metadados em disco."""
        PASTA_INDICE.mkdir(exist_ok=True)
        faiss.write_index(self.indice, str(ARQ_FAISS))
        with open(ARQ_META, "wb") as f:
            pickle.dump([asdict(c) for c in self.chunks], f)
        print(f"\n   Índice salvo em {PASTA_INDICE.resolve()}")

    @classmethod
    def carregar(cls) -> "VectorStore":
        """Carrega um índice previamente salvo."""
        if not ARQ_FAISS.exists() or not ARQ_META.exists():
            raise FileNotFoundError(
                "Índice não encontrado. Rode 'python -m rag.vectorstore' "
                "para construí-lo primeiro."
            )
        indice = faiss.read_index(str(ARQ_FAISS))
        with open(ARQ_META, "rb") as f:
            dados = pickle.load(f)
        chunks = [Chunk(**d) for d in dados]
        return cls(indice, chunks)

    # ----------------------------------------------------------------
    # Consulta
    # ----------------------------------------------------------------
    def buscar(self, consulta: str, k: int = 4) -> list[tuple[Chunk, float]]:
        """
        Recupera os k chunks mais relevantes para a consulta.

        Retorna uma lista de tuplas (chunk, score), ordenada do mais
        relevante para o menos relevante.
        """
        emb = gerar_embedding_consulta(consulta).reshape(1, -1)
        scores, indices = self.indice.search(emb, k)

        resultados: list[tuple[Chunk, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            resultados.append((self.chunks[idx], float(score)))
        return resultados


def construir_e_salvar(pasta_corpus: str | Path = "corpus") -> VectorStore:
    """Função de conveniência: constrói o índice e salva em disco."""
    store = VectorStore.construir(pasta_corpus)
    store.salvar()
    return store


if __name__ == "__main__":
    # Executar este módulo (re)constrói o índice a partir do corpus
    print("=" * 60)
    print("Construindo vector store a partir do corpus")
    print("=" * 60 + "\n")
    store = construir_e_salvar()

    # Teste rápido de busca
    print("\n" + "=" * 60)
    print("Teste de busca")
    print("=" * 60)
    consulta_teste = "Como satélites ajudam a monitorar a agricultura?"
    print(f"\nConsulta: {consulta_teste}\n")
    for i, (chunk, score) in enumerate(store.buscar(consulta_teste, k=3), 1):
        print(f"[{i}] score={score:.3f} | {chunk.titulo} (p.{chunk.pagina})")
        print(f"    {chunk.texto[:160]}...\n")
