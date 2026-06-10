"""
experimento.py — Orquestra o experimento completo: clássico vs QML.

Etapas:
  1. Extrai atributos da telemetria (features.py).
  2. Padroniza e reduz dimensionalidade com PCA -> n_qubits atributos.
  3. Cria um subconjunto balanceado e reduzido (viável para QML em simulador).
  4. Treina/avalia baselines clássicos (SVM RBF, Random Forest).
  5. Treina/avalia modelos QML (QSVC e VQC) no mesmo subconjunto (comparação justa).
  6. Avalia também o baseline clássico no dataset COMPLETO (teto de referência).
  7. Salva tabela de resultados (resultados/resultados.csv) e gráficos comparativos.

Uso:
    python experimento.py
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

from features import extrair_features
from baseline_classico import rodar_baselines
from qml_modelo import rodar_qsvc, rodar_vqc
from comum import build_pipeline

N_QUBITS = 4          # atributos após PCA = qubits
N_AMOSTRAS_QML = 120  # subconjunto balanceado para o QML (simulador)
SEED = 42
DIR_SAIDA = "resultados"


def subconjunto_balanceado(X, y, n_total, seed=SEED):
    """Seleciona n_total/2 de cada classe para um subconjunto balanceado."""
    rng = np.random.default_rng(seed)
    idx0 = np.where(y == 0)[0]
    idx1 = np.where(y == 1)[0]
    k = min(n_total // 2, len(idx0), len(idx1))
    sel0 = rng.choice(idx0, k, replace=False)
    sel1 = rng.choice(idx1, k, replace=False)
    sel = np.concatenate([sel0, sel1])
    rng.shuffle(sel)
    return X[sel], y[sel]


def main() -> None:
    os.makedirs(DIR_SAIDA, exist_ok=True)
    print("[1] Extraindo atributos da telemetria ...")
    X, y, _ = extrair_features()
    print(f"    {X.shape[0]} janelas, {X.shape[1]} atributos brutos, "
          f"{100*y.mean():.1f}% anomalias")

    print(f"[2] Subconjunto balanceado para QML ({N_AMOSTRAS_QML} amostras) ...")
    # Subconjunto e split feitos nos atributos BRUTOS; o pré-processamento
    # (padronização + PCA + escala angular) é ajustado SOMENTE no treino.
    Xb, yb = subconjunto_balanceado(X, y, N_AMOSTRAS_QML)
    Xb_tr, Xb_te, y_tr, y_te = train_test_split(
        Xb, yb, test_size=0.3, stratify=yb, random_state=SEED)

    print(f"[3] Pré-processamento (fit só no treino) -> {N_QUBITS} qubits ...")
    pipe = build_pipeline(N_QUBITS)
    X_tr = pipe.fit_transform(Xb_tr)
    X_te = pipe.transform(Xb_te)
    var = float(pipe.named_steps["pca"].explained_variance_ratio_.sum())
    print(f"    treino={len(X_tr)} | teste={len(X_te)} | "
          f"balanceamento treino={y_tr.mean():.2f} | "
          f"variância PCA explicada={100*var:.1f}%")

    resultados = []

    print("[4] Baselines clássicos (subconjunto reduzido) ...")
    for r in rodar_baselines(X_tr, y_tr, X_te, y_te):
        r["conjunto"] = "reduzido"
        resultados.append(r)
        print(f"    {r['modelo']:22s} acc={r['acuracia']:.3f} f1={r['f1']:.3f} "
              f"t_treino={r['t_treino_s']:.3f}s")

    print("[5] Modelos QML (Qiskit, simulador Aer) ...")
    print("    treinando QSVC (kernel quântico) ...")
    r = rodar_qsvc(X_tr, y_tr, X_te, y_te, n_qubits=N_QUBITS)
    r["conjunto"] = "reduzido"; resultados.append(r)
    print(f"    {r['modelo']:22s} acc={r['acuracia']:.3f} f1={r['f1']:.3f} "
          f"t_treino={r['t_treino_s']:.2f}s qubits={r['n_qubits']} "
          f"prof={r['profundidade_circuito']}")

    print("    treinando VQC (variacional) ...")
    r = rodar_vqc(X_tr, y_tr, X_te, y_te, n_qubits=N_QUBITS)
    r["conjunto"] = "reduzido"; resultados.append(r)
    print(f"    {r['modelo']:22s} acc={r['acuracia']:.3f} f1={r['f1']:.3f} "
          f"t_treino={r['t_treino_s']:.2f}s qubits={r['n_qubits']} "
          f"prof={r['profundidade_circuito']}")

    print("[6] Baseline clássico no dataset COMPLETO (teto de referência) ...")
    Xc_tr_raw, Xc_te_raw, yc_tr, yc_te = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=SEED)
    pipe_c = build_pipeline(N_QUBITS)
    Xc_tr = pipe_c.fit_transform(Xc_tr_raw)
    Xc_te = pipe_c.transform(Xc_te_raw)
    for r in rodar_baselines(Xc_tr, yc_tr, Xc_te, yc_te):
        r["conjunto"] = "completo"
        r["modelo"] = r["modelo"] + " [dataset completo]"
        resultados.append(r)
        print(f"    {r['modelo']:32s} acc={r['acuracia']:.3f} f1={r['f1']:.3f}")

    # ---- Salvar resultados ----------------------------------------------
    df = pd.DataFrame(resultados)
    csv_path = os.path.join(DIR_SAIDA, "resultados.csv")
    df.to_csv(csv_path, index=False)
    with open(os.path.join(DIR_SAIDA, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\n[7] Resultados salvos em {csv_path}")

    _gerar_graficos(df)
    print(f"    Gráficos salvos em {DIR_SAIDA}/")
    print("\n=== TABELA FINAL ===")
    cols = ["modelo", "tipo", "conjunto", "acuracia", "f1", "t_treino_s",
            "n_qubits", "profundidade_circuito"]
    print(df[cols].to_string(index=False))


def _gerar_graficos(df: pd.DataFrame) -> None:
    # Comparação no subconjunto reduzido (clássico vs quântico)
    red = df[df["conjunto"] == "reduzido"].copy()
    cores = ["#4C72B0" if t == "clássico" else "#C44E52" for t in red["tipo"]]

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ax[0].bar(red["modelo"], red["acuracia"], color=cores)
    ax[0].set_title("Acurácia — subconjunto reduzido (4 qubits)")
    ax[0].set_ylim(0, 1); ax[0].tick_params(axis="x", rotation=20)
    ax[0].set_ylabel("Acurácia")

    ax[1].bar(red["modelo"], red["t_treino_s"], color=cores)
    ax[1].set_title("Tempo de treino (s) — escala log")
    ax[1].set_yscale("log"); ax[1].tick_params(axis="x", rotation=20)
    ax[1].set_ylabel("segundos (log)")
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_SAIDA, "comparacao_acuracia_tempo.png"), dpi=130)
    plt.close()

    # Acurácia vs F1 agrupado
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(red)); w = 0.38
    ax.bar(x - w/2, red["acuracia"], w, label="Acurácia", color="#4C72B0")
    ax.bar(x + w/2, red["f1"], w, label="F1", color="#DD8452")
    ax.set_xticks(x); ax.set_xticklabels(red["modelo"], rotation=20, ha="right")
    ax.set_ylim(0, 1); ax.legend(); ax.set_title("Acurácia e F1 por modelo")
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_SAIDA, "acuracia_f1.png"), dpi=130)
    plt.close()


if __name__ == "__main__":
    main()
