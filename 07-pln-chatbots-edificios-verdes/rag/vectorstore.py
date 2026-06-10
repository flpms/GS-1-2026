"""Vector database (FAISS).

Índice `IndexFlatIP` (produto interno). Como os embeddings são normalizados,
o produto interno é igual à similaridade de cosseno. O índice e os metadados
das passagens são persistidos em disco, atendendo ao requisito do enunciado de
"armazenar o corpus em um vector database".
"""

import json
from pathlib import Path

import faiss
import numpy as np


class VectorStore:
    def __init__(self):
        self.index = None
        self.dimensao = None
        self.metadados: list[dict] = []

    def construir(self, vetores: np.ndarray, metadados: list[dict]) -> None:
        self.dimensao = int(vetores.shape[1])
        self.index = faiss.IndexFlatIP(self.dimensao)
        self.index.add(vetores)
        self.metadados = metadados
        print(f"Índice FAISS criado: {self.index.ntotal} vetores, dim={self.dimensao}")

    def buscar(self, vetor_consulta: np.ndarray, k: int = 4) -> list[dict]:
        if self.index is None:
            raise RuntimeError("Índice não carregado. Rode construir_indice.py antes.")
        scores, indices = self.index.search(vetor_consulta, k)
        resultados: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            item = dict(self.metadados[idx])
            item["score"] = float(score)
            resultados.append(item)
        return resultados

    def salvar(self, pasta: str = "indice") -> None:
        Path(pasta).mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(Path(pasta) / "faiss.index"))
        with open(Path(pasta) / "metadados.json", "w", encoding="utf-8") as f:
            json.dump(self.metadados, f, ensure_ascii=False, indent=2)
        print(f"Índice salvo em '{pasta}/'.")

    def carregar(self, pasta: str = "indice") -> None:
        caminho_index = Path(pasta) / "faiss.index"
        caminho_meta = Path(pasta) / "metadados.json"
        if not caminho_index.exists() or not caminho_meta.exists():
            raise FileNotFoundError(
                f"Índice não encontrado em '{pasta}/'. Rode 'python construir_indice.py' primeiro."
            )
        self.index = faiss.read_index(str(caminho_index))
        with open(caminho_meta, "r", encoding="utf-8") as f:
            self.metadados = json.load(f)
        self.dimensao = self.index.d
        print(f"Índice carregado: {self.index.ntotal} vetores.")
