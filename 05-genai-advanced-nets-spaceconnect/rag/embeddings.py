"""
Módulo de geração de embeddings.

Usa o modelo 'paraphrase-multilingual-MiniLM-L12-v2', que é multilíngue
(funciona bem em português e inglês — importante porque o corpus tem
documentos em inglês e as perguntas serão em português).

Os embeddings são normalizados (norma L2 = 1) para que o produto interno
no FAISS seja equivalente à similaridade do cosseno.
"""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

# Modelo compacto, rápido e multilíngue (mesmo usado nos sprints anteriores)
NOME_MODELO = "paraphrase-multilingual-MiniLM-L12-v2"

# cache global para não recarregar o modelo a cada chamada
_modelo: SentenceTransformer | None = None


def obter_modelo() -> SentenceTransformer:
    """Carrega (uma única vez) e devolve o modelo de embeddings."""
    global _modelo
    if _modelo is None:
        print(f"  Carregando modelo de embeddings: {NOME_MODELO}")
        _modelo = SentenceTransformer(NOME_MODELO)
    return _modelo


def gerar_embeddings(textos: list[str], batch_size: int = 32) -> np.ndarray:
    """
    Gera embeddings normalizados para uma lista de textos.

    Retorna um array float32 de shape (n_textos, dim) pronto para o FAISS.
    """
    modelo = obter_modelo()
    embeddings = modelo.encode(
        textos,
        batch_size=batch_size,
        show_progress_bar=len(textos) > 50,
        convert_to_numpy=True,
        normalize_embeddings=True,  # normalização L2 -> cosseno via produto interno
    )
    return embeddings.astype("float32")


def gerar_embedding_consulta(consulta: str) -> np.ndarray:
    """Gera o embedding (normalizado) de uma única consulta."""
    return gerar_embeddings([consulta])[0]
