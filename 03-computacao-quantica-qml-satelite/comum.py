"""
comum.py — Utilidades compartilhadas pelos experimentos adicionais
(robustez multi-semente e simulação com ruído).

Centraliza a extração de atributos e a construção do Pipeline de
pré-processamento (padronização -> PCA -> escala angular). O Pipeline é
ajustado (fit) SOMENTE sobre os dados de treino e apenas aplicado
(transform) aos dados de teste, evitando vazamento de informação
(data leakage). Garante que todos os experimentos partam exatamente do
mesmo ponto e sejam reprodutíveis.
"""

import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

from features import extrair_features

N_QUBITS = 4
SEED_PCA = 42  # PCA com semente fixa para reprodutibilidade


def build_pipeline(n_qubits: int = N_QUBITS) -> Pipeline:
    """Pipeline de pré-processamento: padroniza -> PCA(n_qubits) -> escala [0, pi].

    Deve ser ajustado (fit) APENAS no treino e aplicado (transform) ao teste.
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("pca", PCA(n_components=n_qubits, random_state=SEED_PCA)),
        ("angular", MinMaxScaler(feature_range=(0, np.pi))),
    ])


def preparar_features():
    """Retorna (X, y) com os atributos BRUTOS (sem transformação).

    A transformação é feita por build_pipeline() depois do split, para não
    haver data leakage.
    """
    X, y, _ = extrair_features()
    return X, y


# Compatibilidade: mantém o nome antigo, agora retornando atributos brutos.
def preparar_dados(n_qubits: int = N_QUBITS):
    return preparar_features()


def subconjunto_balanceado(X, y, n_total: int, seed: int):
    """n_total/2 de cada classe, embaralhado. A seed controla a amostragem."""
    rng = np.random.default_rng(seed)
    idx0 = np.where(y == 0)[0]
    idx1 = np.where(y == 1)[0]
    k = min(n_total // 2, len(idx0), len(idx1))
    sel0 = rng.choice(idx0, k, replace=False)
    sel1 = rng.choice(idx1, k, replace=False)
    sel = np.concatenate([sel0, sel1])
    rng.shuffle(sel)
    return X[sel], y[sel]


def split_treino_teste(Xb, yb, test_size: float, seed: int):
    return train_test_split(
        Xb, yb, test_size=test_size, stratify=yb, random_state=seed)


def preprocessar_split(Xtr, Xte, n_qubits: int = N_QUBITS):
    """Ajusta o Pipeline NO TREINO e transforma treino e teste (sem leakage)."""
    pipe = build_pipeline(n_qubits)
    Xtr_t = pipe.fit_transform(Xtr)
    Xte_t = pipe.transform(Xte)
    var = float(pipe.named_steps["pca"].explained_variance_ratio_.sum())
    return Xtr_t, Xte_t, var
