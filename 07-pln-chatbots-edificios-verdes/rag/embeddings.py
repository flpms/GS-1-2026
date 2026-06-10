"""Geração de embeddings.

Usa o modelo multilíngue `paraphrase-multilingual-MiniLM-L12-v2`, o mesmo
validado na Disciplina 05. Os vetores são normalizados (norma L2 = 1) para que
o produto interno no FAISS equivalha à similaridade de cosseno.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

NOME_MODELO = "paraphrase-multilingual-MiniLM-L12-v2"


class Embedder:
    def __init__(self, nome_modelo: str = NOME_MODELO):
        print(f"Carregando modelo de embeddings: {nome_modelo}")
        self.modelo = SentenceTransformer(nome_modelo)

    def codificar(self, textos, normalizar: bool = True) -> np.ndarray:
        if isinstance(textos, str):
            textos = [textos]
        vetores = self.modelo.encode(
            textos, convert_to_numpy=True, show_progress_bar=False
        )
        if normalizar:
            normas = np.linalg.norm(vetores, axis=1, keepdims=True)
            normas[normas == 0] = 1e-12
            vetores = vetores / normas
        return vetores.astype("float32")
