"""
features.py — Extração de atributos a partir da telemetria (janelamento temporal).

A série temporal bruta é dividida em janelas deslizantes. Para cada janela e cada
sensor calculam-se estatísticas (média, desvio-padrão, mínimo, máximo e tendência/
inclinação), produzindo um vetor de atributos por janela. O rótulo da janela é 1
(anomalia) se a fração de amostras anômalas na janela superar um limiar.

Isso transforma o problema de série temporal em um problema tabular de classificação
binária, adequado tanto ao baseline clássico quanto ao QML.
"""

import os
import numpy as np
import pandas as pd

SENSORES = ["temp_painel", "tensao_bateria", "corrente_carga", "temp_interna", "roda_reacao"]
TAMANHO_JANELA = 15
PASSO = 10
LIMIAR_ANOMALIA = 0.3
CSV = os.path.join(os.path.dirname(__file__), "dados", "telemetria_satelite.csv")


def _stats_janela(janela: np.ndarray) -> list[float]:
    """média, desvio, min, max e inclinação (slope) de um trecho 1D."""
    x = np.arange(len(janela))
    slope = np.polyfit(x, janela, 1)[0] if len(janela) > 1 else 0.0
    return [janela.mean(), janela.std(), janela.min(), janela.max(), slope]


def extrair_features(csv: str = CSV):
    """Retorna X (atributos), y (rótulos) e os nomes das colunas."""
    df = pd.read_csv(csv)
    X, y = [], []
    for ini in range(0, len(df) - TAMANHO_JANELA + 1, PASSO):
        fim = ini + TAMANHO_JANELA
        bloco = df.iloc[ini:fim]
        feats = []
        for s in SENSORES:
            feats.extend(_stats_janela(bloco[s].to_numpy()))
        X.append(feats)
        y.append(int(bloco["rotulo"].mean() >= LIMIAR_ANOMALIA))

    nomes = [f"{s}_{est}" for s in SENSORES
             for est in ("media", "desvio", "min", "max", "slope")]
    return np.array(X, dtype=float), np.array(y, dtype=int), nomes


if __name__ == "__main__":
    X, y, nomes = extrair_features()
    print(f"Janelas: {len(X)} | Atributos: {X.shape[1]}")
    print(f"Anomalias: {int(y.sum())} ({100*y.mean():.1f}%) | Nominais: {int((1-y).sum())}")
